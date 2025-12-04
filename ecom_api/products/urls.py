from django.urls import path
from .views import CategoryViewSet

category_list = CategoryViewSet.as_view({'get': 'list'})
category_tree = CategoryViewSet.as_view({'get': 'tree'})

urlpatterns = [
    path('category/', category_list, name='category_list'),
    path('category/tree/', category_tree, name='category_tree'),
]
