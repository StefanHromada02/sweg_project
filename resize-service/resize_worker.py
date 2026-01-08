"""
Image Resize Microservice
Consumes messages from RabbitMQ queue and resizes images.
"""
import os
import sys
import json
import time
import pika
import boto3
from io import BytesIO
from PIL import Image
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, text


class ImageResizeService:
    """Service for processing image resize tasks from RabbitMQ."""

    def __init__(self):
        """Initialize connections to RabbitMQ and MinIO."""
        # RabbitMQ configuration
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.queue_name = 'image_resize_queue'

        # MinIO configuration
        self.minio_endpoint = os.getenv('MINIO_ENDPOINT', 'minio:9000')
        self.minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minio')
        self.minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minio_admin')
        self.bucket_name = os.getenv('MINIO_BUCKET', 'social-media-bucket')

        # Thumbnail configuration
        self.thumbnail_size = (1000, 1000)

        # Database configuration
        self.db_host = os.getenv('POSTGRES_HOST', 'db')
        self.db_name = os.getenv('POSTGRES_DB', 'social_media_db')
        self.db_user = os.getenv('POSTGRES_USER', 'postgres')
        self.db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')

        # Initialize MinIO client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{self.minio_endpoint}",
            aws_access_key_id=self.minio_access_key,
            aws_secret_access_key=self.minio_secret_key,
            region_name='us-east-1'
        )

        # Initialize SQLAlchemy Engine
        db_url = f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"
        self.db_engine = create_engine(db_url)

    def connect_db(self):
        """Connect to PostgreSQL database."""
        import psycopg2
        return psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    def download_image(self, image_path: str) -> BytesIO:
        """Download image from MinIO."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=image_path
            )
            return BytesIO(response['Body'].read())
        except ClientError as e:
            print(f"Error downloading image {image_path}: {e}")
            raise

    def resize_image(self, image_data: BytesIO) -> BytesIO:
        """Resize image to thumbnail size."""
        try:
            # Open image
            img = Image.open(image_data)
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize with aspect ratio preserved
            img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output
        except Exception as e:
            print(f"Error resizing image: {e}")
            raise

    def upload_thumbnail(self, thumbnail_data: BytesIO, original_path: str) -> str:
        """Upload thumbnail to MinIO."""
        try:
            # Generate thumbnail path
            parts = original_path.split('/')
            if len(parts) >= 2:
                folder = parts[0]
                filename = '/'.join(parts[1:])
                thumbnail_path = f"{folder}/thumbnails/{filename}"
            else:
                thumbnail_path = f"thumbnails/{original_path}"

            # Upload to MinIO
            thumbnail_data.seek(0)
            self.s3_client.upload_fileobj(
                thumbnail_data,
                self.bucket_name,
                thumbnail_path,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )

            print(f"Uploaded thumbnail: {thumbnail_path}")
            return thumbnail_path
        except ClientError as e:
            print(f"Error uploading thumbnail: {e}")
            raise

    def update_post_thumbnail(self, post_id: int, thumbnail_path: str):
        """Update post record with thumbnail path."""
        try:
            with self.db_engine.connect() as conn:
                conn.execute(
                    text("UPDATE posts_post SET thumbnail = :thumbnail WHERE id = :id"),
                    {"thumbnail": thumbnail_path, "id": post_id}
                )
                conn.commit()
            print(f"Updated post {post_id} with thumbnail: {thumbnail_path}")
        except Exception as e:
            print(f"Error updating post {post_id}: {e}")
            raise

    def _publish_rpc_response(self, ch, properties, payload: dict):
        """Publish an RPC response if reply_to/correlation_id are present."""
        try:
            reply_to = getattr(properties, 'reply_to', None)
            correlation_id = getattr(properties, 'correlation_id', None)
            if not reply_to or not correlation_id:
                return

            ch.basic_publish(
                exchange='',
                routing_key=reply_to,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    correlation_id=correlation_id,
                    content_type='application/json',
                    delivery_mode=1,
                )
            )
        except Exception as e:
            print(f"Failed to publish RPC response: {e}")

    def process_message(self, ch, method, properties, body):
        """Process a single resize task from the queue."""
        try:
            # Parse message
            message = json.loads(body)
            image_path = message['image_path']
            post_id = message['post_id']

            print(f"Processing resize task for post {post_id}, image: {image_path}")

            # Download image
            image_data = self.download_image(image_path)

            # Resize image
            thumbnail_data = self.resize_image(image_data)

            # Upload thumbnail
            thumbnail_path = self.upload_thumbnail(thumbnail_data, image_path)

            # Update database
            self.update_post_thumbnail(post_id, thumbnail_path)

            # Publish RPC response (if requested)
            self._publish_rpc_response(
                ch,
                properties,
                {
                    "status": "success",
                    "post_id": post_id,
                    "thumbnail_path": thumbnail_path,
                },
            )

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Successfully processed resize task for post {post_id}")

        except Exception as e:
            print(f"Error processing message: {e}")

            # Publish RPC error response (if requested)
            try:
                # best effort: attempt to parse post_id for the response
                post_id_for_error = None
                try:
                    msg = json.loads(body)
                    post_id_for_error = msg.get('post_id')
                except Exception:
                    pass

                self._publish_rpc_response(
                    ch,
                    properties,
                    {
                        "status": "error",
                        "post_id": post_id_for_error,
                        "error_code": "PROCESSING_FAILED",
                        "message": str(e),
                    },
                )
            except Exception:
                pass

            # Reject and requeue the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from RabbitMQ."""
        while True:
            try:
                # Connect to RabbitMQ
                credentials = pika.PlainCredentials(
                    self.rabbitmq_user,
                    self.rabbitmq_password
                )
                parameters = pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    port=self.rabbitmq_port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()

                # Declare queue
                channel.queue_declare(queue=self.queue_name, durable=True)

                # Set QoS - process one message at a time
                channel.basic_qos(prefetch_count=1)

                # Start consuming
                channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.process_message
                )

                print("Image Resize Service started. Waiting for messages...")
                channel.start_consuming()

            except Exception as e:
                print(f"Connection error: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)


if __name__ == '__main__':
    print("Starting Image Resize Service...")
    service = ImageResizeService()
    service.start_consuming()
