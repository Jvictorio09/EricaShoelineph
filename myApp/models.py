from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.text import slugify
import uuid  # For guest session ID

# ----------------------------------------
# CATEGORY MODEL
# ----------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    discount_text = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="category_images/", default="default_category.jpg")

    def __str__(self):
        return self.name

# ----------------------------------------
# SIZE MODEL
# ----------------------------------------
class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# ----------------------------------------
# COLOR MODEL (WITH ADMIN SUPPORT)
# ----------------------------------------
class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, unique=True, help_text="Pick a color", default="#000000")  # Default black color

    def __str__(self):
        return f"{self.name} ({self.hex_code})"

# ----------------------------------------
# PRODUCT MODEL
# ----------------------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to="product_images/", default="default_product.jpg")
    best_seller = models.BooleanField(default=False)
    sizes = models.ManyToManyField(Size, blank=True)
    colors = models.ManyToManyField(Color, blank=True)  # Allow multiple colors for a product

    def __str__(self):
        return self.name

    def get_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def get_discount_percentage(self):
        if self.discount_price:
            return int((1 - (self.discount_price / self.price)) * 100)
        return None

    def get_average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 1) if average else 0

# ----------------------------------------
# CART AND CARTITEM (FIXED FOR GUEST USERS)
# ----------------------------------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)  # Store session ID for guests
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow NULL for guest users
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user.username if self.user else 'Guest'})"

    @property
    def get_total_price(self):
        return self.quantity * self.product.get_price()

# ----------------------------------------
# BLOG & COMMENTS (ALLOW GUEST COMMENTS)
# ----------------------------------------
class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="blogs", default=1)
    author = models.CharField(max_length=100)
    published_date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to="blog_images/")
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow NULL users
    guest_name = models.CharField(max_length=100, blank=True, null=True)  # Guest name
    guest_email = models.EmailField(blank=True, null=True)  # Guest email
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
    bg_image = models.ImageField(upload_to='offers/')
    image1 = models.ImageField(upload_to='offers/')
    image2 = models.ImageField(upload_to='offers/')
    image3 = models.ImageField(upload_to='offers/')

    def __str__(self):
        return self.title
    
from django.db import models

class Feature(models.Model):
    title = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='features/')

    def __str__(self):
        return self.title
    

class ProductCollection(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="collections/")


from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    feedback = models.TextField()
    image = models.ImageField(upload_to="testimonials/")

    def __str__(self):
        return self.name


from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


from django.db import models

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code


from django.db import models
from django.contrib.auth.models import User

# Team Member Model
class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    image = models.ImageField(upload_to="team/")
    facebook = models.URLField(blank=True, null=True)
    dribbble = models.URLField(blank=True, null=True)
    pinterest = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    feedback = models.TextField()
    image = models.ImageField(upload_to="testimonials/")
    date_posted = models.DateField(default="2025-01-01")  # Set a default

    def __str__(self):
        return f"{self.name} - {self.date_posted}"