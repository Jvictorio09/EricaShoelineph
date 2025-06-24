from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from .models import (
    Product, Category, Size, Color, Blog, Tag, SpecialOffer,
    Feature, ProductCollection, Testimonial, AboutSection
)
from django.utils.safestring import mark_safe
from .models import Product, ProductImage  # Add ProductImage if not yet imported


# ---- CATEGORY ADMIN ----

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_main_header", "show_on_homepage", "get_blog_count")
    list_filter = ("is_main_header", "show_on_homepage")
    search_fields = ("name",)
    fields = ("name", "discount_text", "image", "is_main_header", "show_on_homepage")
    actions = ["mark_show_on_homepage", "remove_from_homepage"]

    def get_blog_count(self, obj):
        return obj.blogs.count()

    get_blog_count.short_description = "Blog Count"

    def mark_show_on_homepage(self, request, queryset):
        # Count current categories set to show on homepage
        current_count = Category.objects.filter(show_on_homepage=True).count()
        selected_count = queryset.count()

        # Calculate how many new items will be added
        to_add = [obj for obj in queryset if not obj.show_on_homepage]
        if current_count + len(to_add) > 3:
            self.message_user(
                request,
                f"🚫 You can only have up to 3 categories on the homepage. Currently showing: {current_count}, trying to add: {len(to_add)}.",
                level=messages.ERROR,
            )
            return

        # Update
        updated = queryset.update(show_on_homepage=True)
        self.message_user(
            request,
            f"✅ {updated} categories marked as 'Show on Homepage'.",
            level=messages.SUCCESS,
        )

    mark_show_on_homepage.short_description = "📌 Mark selected categories to show on homepage (max 3)"

    def remove_from_homepage(self, request, queryset):
        updated = queryset.update(show_on_homepage=False)
        self.message_user(
            request,
            f"🧹 {updated} categories removed from homepage.",
            level=messages.SUCCESS,
        )

    remove_from_homepage.short_description = "🚫 Remove selected categories from homepage"

# ---- BLOG ADMIN ----
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "published_date", "get_tags")
    search_fields = ("title", "author", "category__name", "tags__name")
    list_filter = ("category", "published_date", "tags")
    ordering = ("-published_date",)
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)

    def get_tags(self, obj):
        """Display assigned tags in the admin list view."""
        return ", ".join(tag.name for tag in obj.tags.all())

    get_tags.short_description = "Tags"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# ---- COLOR ADMIN ----
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code_display")
    search_fields = ("name",)
    fields = ("name", "hex_code")

    class Media:
        js = ("admin/js/colorpicker.js",)  # Load JS to enable color picker

    def hex_code_display(self, obj):
        return mark_safe(f'<div style="width: 30px; height: 30px; background-color: {obj.hex_code}; border-radius: 5px;"></div>')

    hex_code_display.short_description = "Color Preview"

class ProductImageInline(admin.TabularInline):  # You can also use StackedInline
    model = ProductImage
    extra = 1
    max_num = 5
    fields = ('image', 'alt_text', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" style="border-radius:5px;" />')
        return "No Image"

    preview.short_description = "Preview"


# ---- PRODUCT ADMIN ----
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount_price", "best_seller", "price_range", "get_sizes", "get_colors")
    search_fields = ("name", "category__name", "price_range")
    list_filter = ("category", "best_seller", "sizes", "colors", "price_range")
    autocomplete_fields = ("category",)
    filter_horizontal = ("sizes", "colors")
    inlines = [ProductImageInline]  # ✅ Add this line

    def get_sizes(self, obj):
        return ", ".join(size.name for size in obj.sizes.all())
    get_sizes.short_description = "Available Sizes"

    def get_colors(self, obj):
        return ", ".join(color.name for color in obj.colors.all())
    get_colors.short_description = "Available Colors"


class ProductImageInline(admin.TabularInline):  # You can also use StackedInline
    model = ProductImage
    extra = 1
    max_num = 5
    fields = ('image', 'alt_text', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" style="border-radius:5px;" />')
        return "No Image"

    preview.short_description = "Preview"



@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# ---- SPECIAL OFFER ADMIN ----
@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_percentage")
    search_fields = ("title",)
    list_filter = ("discount_percentage",)
    ordering = ("-discount_percentage",)

    fieldsets = (
        ('Offer Details', {
            'fields': ('title', 'description', 'discount_percentage')
        }),
        ('Images', {
            'fields': ('bg_image', 'image1', 'image2', 'image3')
        }),
    )

# ---- FEATURE ADMIN ----
@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["title"]

# ---- PRODUCT COLLECTION ADMIN ----
@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "image_preview")
    search_fields = ("name",)

    def image_preview(self, obj):
        """Show image preview in the admin panel"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:5px;" />')
        return "No Image"

    image_preview.short_description = "Preview"

# ---- TESTIMONIAL ADMIN ----
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "feedback_preview", "image_preview")
    search_fields = ("name", "feedback")

    def feedback_preview(self, obj):
        """Shorten feedback for admin display"""
        return obj.feedback[:50] + "..." if len(obj.feedback) > 50 else obj.feedback

    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:5px;" />')
        return "No Image"

    feedback_preview.short_description = "Feedback"
    image_preview.short_description = "Preview"


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_reversed']
    ordering = ['order']


