from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='children', 
        blank=True, 
        null=True,
        verbose_name='Parent Category'
    )
    image = models.ImageField(
        upload_to='categories/', 
        blank=True, 
        null=True,
        help_text='Category image (recommended size: 400x400px)'
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower number shows first)')
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['parent', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
            # Ensure slug uniqueness
            slug_exists = True
            counter = 1
            original_slug = self.slug
            
            while slug_exists:
                try:
                    if Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                        self.slug = f"{original_slug}-{counter}"
                        counter += 1
                    else:
                        slug_exists = False
                except Category.DoesNotExist:
                    slug_exists = False
        
        super().save(*args, **kwargs)
    
    @property
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('category-detail', kwargs={'slug': self.slug})
    
    def get_full_path(self):
        """Get full category path including parents"""
        path = []
        current = self
        
        while current:
            path.insert(0, current.name)
            current = current.parent
        
        return ' > '.join(path)
    
    def get_all_children(self, include_self=False):
        """Get all descendant categories recursively"""
        categories = []
        
        if include_self:
            categories.append(self)
        
        for child in self.children.all():
            categories.append(child)
            categories.extend(child.get_all_children())
        
        return categories
    
    def get_active_children(self):
        """Get only active child categories"""
        return self.children.filter(is_active=True)
    
    def get_products_count(self):
        """Get total products in this category and all subcategories"""
        from django.db.models import Q
        
        # Get all category IDs including descendants
        all_category_ids = [cat.id for cat in self.get_all_children(include_self=True)]
        
        # Count products in these categories
        return Product.objects.filter(category__id__in=all_category_ids, is_active=True).count()
    
    def get_image_url(self):
        """Get category image URL or default"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-category.png'  # You'll need to create this default image
    
class Product(models.Model):
    PRODUCT_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    vendor = models.ForeignKey(
        'vendors.Vendor', 
        on_delete=models.CASCADE, 
        related_name='products',
        blank=True, 
        null=True,
        help_text='Leave empty for admin-owned products'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    sku = models.CharField(
        max_length=100, 
        unique=True,
        help_text='Stock Keeping Unit (auto-generated if empty)'
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Brief product description for listing pages'
    )
    description = models.TextField(help_text='Detailed product description')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        related_name='products',
        null=True
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        help_text='Original price for showing discounts'
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        help_text='Product cost (for profit calculation)'
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        help_text='Send alert when stock reaches this level'
    )
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(
        default=False,
        help_text='Allow customers to purchase out-of-stock products'
    )
    
    # Product details
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True, 
        null=True,
        help_text='Weight in kilograms'
    )
    length = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True, 
        null=True,
        help_text='Length in cm'
    )
    width = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True, 
        null=True,
        help_text='Width in cm'
    )
    height = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        blank=True, 
        null=True,
        help_text='Height in cm'
    )
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_digital = models.BooleanField(
        default=False,
        help_text='Digital products don\'t require shipping'
    )
    
    # Approval
    status = models.CharField(
        max_length=20, 
        choices=PRODUCT_STATUS_CHOICES, 
        default='approved'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='approved_products'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    
    # Ratings (denormalized for performance)
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0
    )
    review_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['is_bestseller', 'is_active']),
            models.Index(fields=['vendor', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate slug if empty
        if not self.slug:
            self.slug = slugify(self.name)
            
            # Ensure slug uniqueness
            slug_exists = True
            counter = 1
            original_slug = self.slug
            
            while slug_exists:
                try:
                    if Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                        self.slug = f"{original_slug}-{counter}"
                        counter += 1
                    else:
                        slug_exists = False
                except Product.DoesNotExist:
                    slug_exists = False
        
        # Generate SKU if empty
        if not self.sku:
            # Generate a unique SKU
            prefix = self.category.name[:3].upper() if self.category else 'PRO'
            self.sku = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
            
            # Check if SKU already exists (extremely unlikely but possible)
            while Product.objects.filter(sku=self.sku).exists():
                self.sku = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
        
        # Set published_at if product is being activated
        if self.is_active and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product-detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        if not self.track_inventory:
            return False
        return 0 < self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare price exists"""
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            return round(discount, 1)
        return 0
    
    @property
    def main_image(self):
        """Get the main/primary product image"""
        return self.images.filter(is_primary=True).first() or self.images.first()
    
    def get_dimensions(self):
        """Get formatted dimensions string"""
        if self.length and self.width and self.height:
            return f"{self.length} × {self.width} × {self.height} cm"
        return None
    
    def get_weight_display(self):
        """Get formatted weight string"""
        if self.weight:
            return f"{self.weight} kg"
        return None
    
    def update_rating(self):
        """Update average rating and review count"""
        from django.db.models import Avg, Count
        from reviews.models import ProductReview
        
        reviews = ProductReview.objects.filter(
            product=self, 
            status='approved'
        ).aggregate(
            average=Avg('rating'),
            count=Count('id')
        )
        
        self.average_rating = reviews['average'] or 0
        self.review_count = reviews['count'] or 0
        self.save(update_fields=['average_rating', 'review_count'])   
 
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        help_text='Product image (recommended size: 800x800px)'
    )
    alt_text = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Alternative text for accessibility'
    )
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(
        default=False,
        help_text='Set as primary/featured image'
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text='Order in which images are displayed (lower number first)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['display_order', 'created_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product
            ).exclude(
                pk=self.pk
            ).update(is_primary=False)
        
        # If no primary image exists for this product, set this as primary
        if not self.pk and not self.product.images.filter(is_primary=True).exists():
            self.is_primary = True
        
        super().save(*args, **kwargs)         
  
class ProductVariant(models.Model):
    VARIANT_TYPES = (
        ('size', 'Size'),
        ('color', 'Color'),
        ('material', 'Material'),
        ('style', 'Style'),
        ('other', 'Other'),
    )
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='variants'
    )
    variant_type = models.CharField(
        max_length=20, 
        choices=VARIANT_TYPES, 
        default='other'
    )
    variant_value = models.CharField(max_length=100)
    sku = models.CharField(
        max_length=100, 
        unique=True,
        blank=True,
        help_text='Variant SKU (auto-generated if empty)'
    )
    price_adjustment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text='Additional price for this variant (+ve or -ve)'
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    weight_adjustment = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text='Additional weight for this variant in kg'
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    image = models.ForeignKey(
        ProductImage, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='variants',
        help_text='Specific image for this variant'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variants'
        ordering = ['display_order', 'variant_type', 'variant_value']
        unique_together = ['product', 'variant_type', 'variant_value']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
    
    def __str__(self):
        return f"{self.product.name} - {self.variant_value}"
    
    def save(self, *args, **kwargs):
        # Generate SKU if empty
        if not self.sku:
            base_sku = self.product.sku
            variant_code = self.variant_value[:3].upper().replace(' ', '')
            self.sku = f"{base_sku}-{variant_code}"
            
            # Ensure SKU uniqueness
            counter = 1
            original_sku = self.sku
            
            while ProductVariant.objects.filter(sku=self.sku).exclude(pk=self.pk).exists():
                self.sku = f"{original_sku}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        """Calculate final price with adjustment"""
        return self.product.price + self.price_adjustment
    
    @property
    def final_weight(self):
        """Calculate final weight with adjustment"""
        if self.product.weight:
            return self.product.weight + self.weight_adjustment
        return self.weight_adjustment
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold
    
    
class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='attributes'
    )
    attribute_name = models.CharField(max_length=100)
    attribute_value = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField(default=0)
    is_filterable = models.BooleanField(
        default=False,
        help_text='Show this attribute in filter options'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_attributes'
        ordering = ['display_order', 'attribute_name']
        verbose_name = 'Product Attribute'
        verbose_name_plural = 'Product Attributes'
    
    def __str__(self):
        return f"{self.attribute_name}: {self.attribute_value}"            
        