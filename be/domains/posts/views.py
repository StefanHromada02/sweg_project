# posts/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Post
from .serializers import PostSerializer
from services.minio_storage import minio_storage


@extend_schema_view(
    list=extend_schema(tags=['Posts']),
    create=extend_schema(tags=['Posts']),
    retrieve=extend_schema(tags=['Posts']),
    update=extend_schema(tags=['Posts']),
    partial_update=extend_schema(tags=['Posts']),
    destroy=extend_schema(tags=['Posts'])
)
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts.
    
    Provides CRUD operations and search functionality for posts.
    """
    queryset = Post.objects.get_queryset()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']  # Standard: Neueste zuerst

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = self.perform_create(serializer)
        if not isinstance(post, Post):
            # Defensive: perform_create muss ein Model-Objekt liefern
            raise ValidationError({"error": "Post could not be created"})

        serializer.instance = post
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Upload image to MinIO before saving post.
        """
        image_file = self.request.FILES.get('image_file')
        image_path = None

        if image_file:
            # Upload to MinIO
            image_path = minio_storage.upload_image(image_file)
            if not image_path:
                raise ValidationError({"image_file": "Failed to upload image"})

        # Get user info from the token or from user object (for tests)
        token = self.request.auth
        if token:
            author_id = token.get('sub')
            author_name = token.get('preferred_username', 'anonymous')
        else:
            # For tests with force_authenticate, use the user object
            user = self.request.user
            author_id = getattr(user, 'sub', 'test-user')
            author_name = getattr(user, 'name', 'Test User')

        # Save with MinIO path and author details
        post = serializer.save(image=image_path or "", author_id=author_id, author_name=author_name)

        # Send resize task to queue and wait for result (RPC) -> avoids frontend polling
        if image_path:
            from services.rabbitmq_service import rabbitmq_service
            try:
                rabbitmq_service.send_resize_task_and_wait(image_path, post.id, timeout_s=float(self.request.query_params.get('thumbnail_timeout', 15)))
                post.refresh_from_db()  # should now include thumbnail
            except Exception as e:
                # If worker is slow/unavailable, we still return the post; thumbnail can appear later.
                # (No frontend polling needed if you keep create blocking long enough.)
                print(f"Thumbnail generation did not finish in time: {e}")

        return post

    def perform_update(self, serializer):
        """
        Handle image update: delete old, upload new.
        """
        instance = serializer.instance
        old_image = instance.image

        image_file = self.request.FILES.get('image_file')

        if image_file:
            # Delete old image if exists
            if old_image:
                minio_storage.delete_image(old_image)

            # Upload new image
            image_path = minio_storage.upload_image(image_file)
            if not image_path:
                raise ValidationError({"image_file": "Failed to upload image"})

            post = serializer.save(image=image_path, thumbnail=None)

            # Send resize task to queue and wait for result (RPC)
            from services.rabbitmq_service import rabbitmq_service
            try:
                rpc_result = rabbitmq_service.send_resize_task_and_wait(
                    image_path,
                    post.id,
                    timeout_s=float(self.request.query_params.get('thumbnail_timeout', 15)),
                )
                if rpc_result.get('status') == 'success':
                    post.refresh_from_db()
                else:
                    print(f"Thumbnail regeneration failed: {rpc_result}")
            except Exception as e:
                print(f"Thumbnail regeneration did not finish in time: {e}")
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete image from MinIO when post is deleted.
        """
        if instance.image:
            minio_storage.delete_image(instance.image)
        instance.delete()

    @extend_schema(
        tags=['Posts'],
        summary="Get user's posts",
        description="Returns all posts for the current user",
        responses={200: PostSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        user_info = request.user
        author_id = user_info.get('author_id')
        posts = Post.objects.filter(author_id=author_id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Posts'],
        summary="Get image",
        description="Proxy to serve images from MinIO storage",
        parameters=[
            OpenApiParameter(
                name='path',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Path to the image in MinIO',
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def image(self, request):
        """Serve image from MinIO storage."""
        from django.http import HttpResponse
        import boto3
        from botocore.exceptions import ClientError
        import os

        image_path = request.query_params.get('path')
        if not image_path:
            return Response(
                {"error": "Missing 'path' parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get image from MinIO
            endpoint = os.getenv('MINIO_ENDPOINT', 'minio:9000')
            access_key = os.getenv('MINIO_ACCESS_KEY', os.getenv('MINIO_ROOT_USER', 'minio'))
            secret_key = os.getenv('MINIO_SECRET_KEY', os.getenv('MINIO_ROOT_PASSWORD', 'minio_admin'))
            bucket_name = os.getenv('MINIO_BUCKET', 'social-media-bucket')

            s3_client = boto3.client(
                's3',
                endpoint_url=f"http://{endpoint}",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1'
            )

            response = s3_client.get_object(Bucket=bucket_name, Key=image_path)
            image_data = response['Body'].read()
            content_type = response.get('ContentType', 'image/jpeg')

            return HttpResponse(image_data, content_type=content_type)

        except ClientError as e:
            return Response(
                {"error": f"Image not found: {str(e)}"},
                status=status.HTTP_404_NOT_FOUND
            )
