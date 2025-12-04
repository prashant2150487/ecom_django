from django.contrib import admin

# Register your models here.
from .models import Category, Product, ProductImage, ProductVariant, ProductAttribute

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'order', 'created_at', 'updated_at')
    list_filter = ('is_active',)    
    search_fields= ('name', 'slug')
    prepopulated_fields= {"slug": ("name",)}
    list_editable = ('is_active', 'order')
    ordering = ('order', 'name')
    def category_product_count(self, obj):
        return obj.get_products_count()
    category_product_count.short_description = 'Total Products'

# ================================
# ✅ PRODUCT IMAGES INLINE
# ================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# ================================
# ✅ PRODUCT VARIANTS INLINE
# ================================

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


# ================================
# ✅ PRODUCT ATTRIBUTES INLINE
# ================================

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


# ================================
# ✅ PRODUCT ADMIN
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'price', 'is_active', 'is_featured', 'is_bestseller', 'is_new', 'is_digital', 'status', 'created_at', 'updated_at', 'published_at')
    list_filter = ('is_active', 'is_featured', 'is_bestseller', 'is_new', 'is_digital', 'status')
    search_fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ('is_active', 'is_featured', 'is_bestseller', 'is_new', 'is_digital')
    inlines = [ProductImageInline, ProductVariantInline, ProductAttributeInline]    
    ordering = ('-created_at',)
    readonly_fields = ('average_rating', 'review_count')
    
    
    

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'display_order')
    list_editable = ('is_primary', 'display_order')
    
    
# ================================
# ✅ PRODUCT VARIANT ADMIN
# ================================

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variant_type',
        'variant_value',
        'final_price',
        'stock_quantity',
        'is_active'
    )
    list_filter = ('variant_type', 'is_active')
    search_fields = ('variant_value', 'sku')    
    
# ================================
# ✅ PRODUCT ATTRIBUTE ADMIN
# ================================

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'attribute_name',
        'attribute_value',
        'is_filterable'
    )
    list_filter = ('is_filterable',)
    search_fields = ('attribute_name', 'attribute_value')    