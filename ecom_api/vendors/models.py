from django.db import models

# Create your models here.


class Vendor(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, unique=True, blank=True)
	email = models.EmailField(blank=True, null=True)
	phone = models.CharField(max_length=50, blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'vendors'
		verbose_name = 'Vendor'
		verbose_name_plural = 'Vendors'

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		# generate slug if missing
		if not self.slug and self.name:
			from django.utils.text import slugify
			base = slugify(self.name)[:240]
			slug = base
			counter = 1
			while Vendor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)
