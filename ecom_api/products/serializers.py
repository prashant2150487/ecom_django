from rest_framework import serializers
from .models import Category , Product , ProductImage , ProductVariant , ProductAttribute




class CategorySerializers(serializers.ModelSerializer):
    children= serializers.SerializerMethodField()
    product_count=serializers.SerializerMethodField()
    parent_name=serializers.CharField(source='parent.name',read_only=True)
    
    
    
    class Meta:
        model=Category
        fields=[
            'id',
            'name',
            'slug',
            'description',
            'parent',
            'parent_name',
            'image',
            'is_active',
            'order',
            'meta_title',
            'meta_description',
            'meta_keywords',
            'created_at',
            'updated_at',
            'children',
            'product_count'

        ]
    def get_children(self, obj):
        """Get active child categories"""
        children = obj.get_active_children()
        return CategorySerializers(children, many=True).data

    def get_product_count(self, obj):
        return obj.get_products_count()

    def validate_parent(self, value):
        """Prevent circular parent relationships"""
        # when creating, self.instance may be None
        if value and getattr(self, 'instance', None) and value.parent and value.parent.id == self.instance.id:
            raise serializers.ValidationError("Can not set a child category as parent.")
        return value
            
            
         
        
        
