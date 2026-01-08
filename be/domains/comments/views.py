from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


@extend_schema_view(
    list=extend_schema(tags=['Comments']),
    create=extend_schema(tags=['Comments']),
    retrieve=extend_schema(tags=['Comments']),
    update=extend_schema(tags=['Comments']),
    partial_update=extend_schema(tags=['Comments']),
    destroy=extend_schema(tags=['Comments'])
)
class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    
    Provides CRUD operations and filtering for comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        # Extract author info from Keycloak token
        token = self.request.auth
        author_id = token.get('sub')
        author_name = token.get('preferred_username', 'anonymous')
        serializer.save(author_id=author_id, author_name=author_name)

    def get_serializer_class(self):
        """Use different serializer for create/update operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    @extend_schema(
        tags=['Comments'],
        summary="Get comments for a specific post",
        description="Returns all comments for the specified post ID",
        parameters=[
            OpenApiParameter(
                name='post_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Post ID to filter comments'
            )
        ],
        responses={200: CommentSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_post(self, request):
        """Get all comments for a specific post."""
        post_id = request.query_params.get('post_id')
        if not post_id:
            return Response({"error": "post_id query parameter is required"}, status=400)
        
        comments = self.queryset.by_post(post_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Comments'],
        summary="Get comments by a specific user",
        description="Returns all comments made by the specified user ID",
        parameters=[
            OpenApiParameter(
                name='user_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='User ID to filter comments'
            )
        ],
        responses={200: CommentSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get all comments by a specific user."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id query parameter is required"}, status=400)
        
        comments = self.queryset.by_user(user_id)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
