from django.shortcuts import render
from rest_framework import status, filters, viewsets
from rest_framework.permissions import AllowAny
from .models import Category
from .serializers import CategorySerializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializers
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset=super().get_queryset()
        parent = self.request.query_params.get('parent', None)
        if parent is not None:
            if parent == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent__slug=parent)
        return queryset.select_related('parent')
    
    @action(detail=False, methods=['get'])
    def tree(self,request):
        """Get complete category tree for navigation"""
        cache_key='category_tree'
        category_tree=cache.get(cache_key)
        if not category_tree:
            # Get root categories (no parent)
            root_category=self.queryset.filter(parent__isnull=True)
            serializer=CategorySerializers(root_category, many=True)
            category_tree=serializer.data
            cache.set(cache_key, category_tree,timeout=3600) # Cache for 1 hour
        return Response(category_tree)
    