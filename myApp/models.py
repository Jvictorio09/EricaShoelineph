from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError

# ----------------------------------------
# CATEGORY MODEL
# ----------------------------------------


class Category(models.Model):
    name = models.CharField(max_length=100)
    discount_text = models.CharField(max_length=50, blank=True, null=True)
    image = CloudinaryField('image', folder="ericashoeline/category_images/")
    is_main_header = models.BooleanField(default=False, help_text="✅ Show as the main homepage slider (only one)")
    show_on_homepage = models.BooleanField(default=False, help_text="✅ Show in the 3-category section (max 3)")

    def __str__(self):
        return self.name

    def clean(self):
        if self.is_main_header:
            count = Category.objects.filter(is_main_header=True).exclude(id=self.id).count()
            if count >= 1:
                raise ValidationError("🚫 Only one category can be marked as main header.")
        
        if self.show_on_homepage:
            count = Category.objects.filter(show_on_homepage=True).exclude(id=self.id).count()
            if count >= 3:
                raise ValidationError("🚫 Only 3 categories can be shown on the homepage category section.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Triggers clean()
        super().save(*args, **kwargs)
        if self.image:
            print(f"📦 Cloudinary Image URL for Category '{self.name}': {self.image.url}")


# ----------------------------------------
# SIZE MODEL
# ----------------------------------------
class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# ----------------------------------------
# COLOR MODEL
# ----------------------------------------
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, unique=True, help_text="Pick a color", default="#000000")

    def __str__(self):
        return f"{self.name} ({self.hex_code})"

# ----------------------------------------
# PRODUCT MODEL
# ----------------------------------------
class Product(models.Model):
    PRICE_RANGE_CHOICES = [
        ('500-1000', '₱500 - ₱1,000'),
        ('1000-2000', '₱1,000 - ₱2,000'),
        ('3000-5000', '₱3,000 - ₱5,000'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = CloudinaryField('image', folder="ericashoeline/product_images/")
    best_seller = models.BooleanField(default=False)
    sizes = models.ManyToManyField(Size, blank=True)
    colors = models.ManyToManyField(Color, blank=True)
    price_range = models.CharField(max_length=20, choices=PRICE_RANGE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_price(self):
        if self.discount_price:
            return self.discount_price
        if self.price:
            return self.price
        return self.estimated_price_from_range()

    def estimated_price_from_range(self):
        if self.price_range:
            min_price, max_price = map(int, self.price_range.split('-'))
            return (min_price + max_price) / 2
        return 0

    @property
    def get_discount_percentage(self):
        if self.discount_price:
            return int((1 - (self.discount_price / self.price)) * 100)
        return None

    def get_average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 1) if average else 0

# ----------------------------------------
# CART & CARTITEM MODEL
# ----------------------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.total_price for item in self.cart_items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user.username if self.user else 'Guest'})"
    
   
    @property
    def total_price(self):
        return self.quantity * self.product.get_price()



# ----------------------------------------
# BLOG & COMMENTS
# ----------------------------------------
class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="blogs", default=1)
    author = models.CharField(max_length=100)
    published_date = models.DateField(auto_now_add=True)
    image = CloudinaryField('image', folder="ericashoeline/blog_images/")
    content = models.TextField()
    tags = models.ManyToManyField('Tag', blank=True, related_name="blogs")
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    def __str__(self):
        return f"Comment by {self.user.username if self.user else self.guest_name} on {self.blog.title}"

# ----------------------------------------
# OTHER MODELS
# ----------------------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    title = models.CharField(max_length=255)
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

class SpecialOffer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.IntegerField()
    bg_image = CloudinaryField('image', folder="ericashoeline/offers/")
    image1 = CloudinaryField('image', folder="ericashoeline/offers/")
    image2 = CloudinaryField('image', folder="ericashoeline/offers/")
    image3 = CloudinaryField('image', folder="ericashoeline/offers/")

    def __str__(self):
        return self.title

class Feature(models.Model):
    title = models.CharField(max_length=255)
    icon = CloudinaryField('image', folder="ericashoeline/features/")

    def __str__(self):
        return self.title

class ProductCollection(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image', folder="ericashoeline/collections/")
    

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    image = CloudinaryField('image', folder="ericashoeline/team/")
    facebook = models.URLField(blank=True, null=True)
    dribbble = models.URLField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    feedback = models.TextField()
    image = CloudinaryField('image', folder="ericashoeline/testimonials/")
    date_posted = models.DateField(default="2025-01-01")

    def __str__(self):
        return f"{self.name} - {self.date_posted}"



class AboutSection(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    image = CloudinaryField('image', folder="ericashoeline/about/")
    is_reversed = models.BooleanField(default=False, help_text="✅ Reverse the row for image on right, text on left")
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} - Section {self.order}"


# models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('preparing', 'Preparing'),
        ('to_ship', 'To Ship'),
        ('shipped', 'Shipped'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255, null=True, blank=True)  # ✅ NEW
    region = models.CharField(max_length=50,null=True, blank=True)     # ✅ NEW
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ NEW

     
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    order_notes = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='received'
    )

    def __str__(self):
        return f"Order #{self.tracking_number} - {self.get_status_display()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
