"""
RabbitMQ Service for sending messages to the image resize queue.
"""
import os
import json
import pika
from typing import Optional, Dict, Any


class RabbitMQService:
    """Service class for interacting with RabbitMQ message queue."""

    def __init__(self):
        """Initialize RabbitMQ configuration."""
        self.host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.user = os.getenv('RABBITMQ_USER', 'guest')
        self.password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.queue_name = 'image_resize_queue'
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ."""
        if self.connection is None or self.connection.is_closed:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare the queue (creates if doesn't exist)
            self.channel.queue_declare(queue=self.queue_name, durable=True)

    def send_resize_task(self, image_path: str, post_id: int) -> bool:
        """
        Send an image resize task to the queue.

        Args:
            image_path: Path to the full-size image in MinIO
            post_id: ID of the post

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            self.connect()

            message = {
                'image_path': image_path,
                'post_id': post_id
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )

            print(f"Sent resize task for image: {image_path}")
            return True

        except Exception as e:
            print(f"Error sending resize task: {e}")
            return False

    def send_resize_task_and_wait(self, image_path: str, post_id: int, timeout_s: float = 15.0) -> Dict[str, Any]:
        """Send a resize task and synchronously wait for the worker response (RPC).

        Returns a dict like:
          success: {"status":"success","post_id":...,"thumbnail_path":...}
          error:   {"status":"error",...}

        Raises:
          TimeoutError on timeout.
          RuntimeError on publish/connection errors.
        """
        import uuid
        import time

        try:
            self.connect()

            # Exclusive, auto-delete callback queue for this request
            result = self.channel.queue_declare(queue='', exclusive=True, auto_delete=True)
            callback_queue = result.method.queue
            correlation_id = str(uuid.uuid4())

            response_holder: Dict[str, Any] = {}

            def on_response(ch, method, props, body):
                nonlocal response_holder
                if props and props.correlation_id == correlation_id:
                    try:
                        response_holder = json.loads(body)
                    except Exception:
                        response_holder = {"status": "error", "error_code": "INVALID_RESPONSE", "message": "Invalid JSON response"}

            consumer_tag = self.channel.basic_consume(
                queue=callback_queue,
                on_message_callback=on_response,
                auto_ack=True,
            )

            message = {
                'image_path': image_path,
                'post_id': post_id
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    reply_to=callback_queue,
                    correlation_id=correlation_id,
                    content_type='application/json',
                )
            )

            deadline = time.time() + float(timeout_s)
            while not response_holder and time.time() < deadline:
                # process network events, dispatch callbacks
                self.connection.process_data_events(time_limit=0.2)

            # stop consumer to avoid leaks
            try:
                self.channel.basic_cancel(consumer_tag)
            except Exception:
                pass

            if not response_holder:
                raise TimeoutError("Timed out waiting for resize result")

            return response_holder

        except TimeoutError:
            raise
        except Exception as e:
            raise RuntimeError(f"RPC resize request failed: {e}")

    def close(self):
        """Close the RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


class RabbitMQServiceProxy:
    """Proxy that manages RabbitMQ service instance."""

    def __init__(self):
        self._instance: Optional[RabbitMQService] = None

    def _get(self) -> RabbitMQService:
        if self._instance is None:
            self._instance = RabbitMQService()
        return self._instance

    def send_resize_task(self, *args, **kwargs):
        return self._get().send_resize_task(*args, **kwargs)

    def send_resize_task_and_wait(self, *args, **kwargs):
        return self._get().send_resize_task_and_wait(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self._get().close(*args, **kwargs)


# Global proxy instance
rabbitmq_service = RabbitMQServiceProxy()
