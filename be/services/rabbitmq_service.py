"""
RabbitMQ Service for sending messages to the image resize queue.
"""
import os
import json
import pika
from typing import Optional


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

    def close(self, *args, **kwargs):
        return self._get().close(*args, **kwargs)


# Global proxy instance
rabbitmq_service = RabbitMQServiceProxy()
