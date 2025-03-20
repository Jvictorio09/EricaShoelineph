from django.contrib import admin
from .models import Product, Category

from django.contrib import admin
from .models import Product, Category

from django.contrib import admin
from .models import Blog, Tag, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "get_blog_count")
    search_fields = ("name",)
    
    def get_blog_count(self, obj):
        """Display count of blogs per category."""
        return obj.blogs.count()
    
    get_blog_count.short_description = "Blog Count"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "published_date", "get_tags")
    search_fields = ("title", "author", "category__name", "tags__name")
    list_filter = ("category", "published_date", "tags")
    ordering = ("-published_date",)
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("title",)}  # Auto-generate slug
    filter_horizontal = ("tags",)  # Enables a better UI for selecting multiple tags
    
    def get_tags(self, obj):
        """Display assigned tags in the admin list view."""
        return ", ".join([tag.name for tag in obj.tags.all()])
    
    get_tags.short_description = "Tags"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

from django.contrib import admin
from .models import Product, Category, Size, Color

from django.contrib import admin
from .models import Color

class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code_display")  
    search_fields = ("name",)
    fields = ("name", "hex_code")

    class Media:
        js = ("admin/js/colorpicker.js",)  # Load JS to enable color picker

    def hex_code_display(self, obj):
        return f'<div style="width: 30px; height: 30px; background-color: {obj.hex_code}; border-radius: 5px;"></div>'
    hex_code_display.allow_tags = True
    hex_code_display.short_description = "Color Preview"

admin.site.register(Color, ColorAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount_price", "best_seller", "get_sizes", "get_colors")
    search_fields = ("name", "category__name")
    list_filter = ("category", "best_seller", "sizes", "colors")
    autocomplete_fields = ("category",)  # Optimized for performance
    filter_horizontal = ("sizes", "colors")  # Enables multi-selection UI

    def get_sizes(self, obj):
        return ", ".join([size.name for size in obj.sizes.all()])
    get_sizes.short_description = "Available Sizes"

    def get_colors(self, obj):
        return ", ".join([color.name for color in obj.colors.all()])
    get_colors.short_description = "Available Colors"


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)



from django.contrib import admin
from .models import SpecialOffer

@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage')  # Show these fields in the admin list
    search_fields = ('title',)  # Allow searching by title
    list_filter = ('discount_percentage',)  # Add filters
    ordering = ('-discount_percentage',)  # Order by discount

    # Fields shown when adding/editing a SpecialOffer
    fieldsets = (
        ('Offer Details', {
            'fields': ('title', 'description', 'discount_percentage')
        }),
        ('Images', {
            'fields': ('bg_image', 'image1', 'image2', 'image3')
        }),
    )


from django.contrib import admin
from .models import Feature

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['title']


from django.contrib import admin
from .models import ProductCollection

@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "image_preview")  # Shows collection name, price, and a preview of the image
    search_fields = ("name",)
    
    def image_preview(self, obj):
        """Show image preview in the admin panel"""
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:5px;" />'
        return "No Image"
    
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"


from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "feedback_preview", "image_preview")  # Shows name, feedback preview, and image
    search_fields = ("name", "feedback")
    
    def feedback_preview(self, obj):
        """Shorten feedback for admin display"""
        return obj.feedback[:50] + "..." if len(obj.feedback) > 50 else obj.feedback
    
    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:5px;" />'
        return "No Image"

    feedback_preview.short_description = "Feedback"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"
