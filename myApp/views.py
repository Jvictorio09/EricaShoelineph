from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate
from .models import Product, Category, SpecialOffer, Feature, ProductCollection, Testimonial, Cart, CartItem, Coupon, TeamMember, Blog

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()  # Fetch all products dynamically
    special_offer = SpecialOffer.objects.first()
    features = Feature.objects.all()
    best_sellers = Product.objects.filter(best_seller=True)
    product_collections = ProductCollection.objects.all()
    testimonials = Testimonial.objects.all()

    context = {
        "categories": categories,
        "products": products,
        'special_offer': special_offer,
        'features': features,
        'best_sellers': best_sellers,
        "product_collections": product_collections,
        "testimonials": testimonials
    }
    return render(request, "myapp/index.html", context)


from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def shop_category(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)  # Filter dynamically
    
    return render(request, 'myapp/shop_category.html', {
        'category': category,
        'products': products
    })


from django.shortcuts import render
from .models import Product, Category, Brand

def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    # Sorting logic
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')

    # Price Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    context = {
        'products': products,
        'categories': categories,
        'brands': brands
    }
    return render(request, 'myapp/shop.html', context)


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Product

def quick_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    product_data = {
        "name": product.name,
        "description": product.description,
        "image_url": product.image.url if product.image else "",
        "price": float(product.get_price()),
        "old_price": float(product.price) if product.discount_price else None,
        "sizes": list(product.sizes.values_list("name", flat=True)) if product.sizes.exists() else []
    }

    return JsonResponse(product_data)

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
import uuid

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, user=request.user)
    else:
        session_id = request.session.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["session_id"] = session_id

        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, user=None)

    if not created:
        cart_item.quantity += quantity
    cart_item.save()

    return JsonResponse({
        "success": True,
        "message": "Item added to cart!",
        "cart_count": CartItem.objects.filter(cart=cart).count()
    })


def get_cart_data(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        items = [
            {
                "id": item.product.id,
                "name": item.product.name,
                "image": item.product.image.url if item.product.image else "",
                "quantity": item.quantity,
                "price": float(item.product.get_price()),
            }
            for item in cart_items
        ]
    else:
        cart = request.session.get("cart", {})
        items = []
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            items.append({
                "id": product.id,
                "name": product.name,
                "image": product.image.url if product.image else "",
                "quantity": item["quantity"],
                "price": float(product.get_price()),
            })

    return JsonResponse({"items": items})


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, product_id=product_id, user=request.user)
        cart_item.delete()
    else:
        cart = request.session.get("cart", {})
        if str(product_id) in cart:
            del cart[str(product_id)]
        request.session["cart"] = cart

    return JsonResponse({"success": True, "message": "Item removed successfully!"})


def clear_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()
    else:
        request.session["cart"] = {}

    return JsonResponse({"success": True, "message": "Cart cleared successfully!"})



from django.shortcuts import render, get_object_or_404
from .models import Product, CartItem

def cart_view(request):
    cart_items = []
    cart_subtotal = 0

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_subtotal = sum(item.get_total_price for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            total_price = product.get_price() * item["quantity"]
            cart_items.append({
                "product": product,
                "quantity": item["quantity"],
                "total_price": total_price
            })
            cart_subtotal += total_price

    context = {
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal,
    }

    return render(request, "myapp/cart.html", context)


from django.shortcuts import render
from .models import CartItem, Product
from decimal import Decimal  # ✅ Import Decimal

def checkout(request):
    cart_items = []
    cart_subtotal = Decimal("0.00")  # ✅ Ensure cart_subtotal is Decimal

    if request.user.is_authenticated:
        # ✅ Logged-in user: Fetch cart from DB
        cart_items = CartItem.objects.filter(user=request.user)
        cart_subtotal = sum(item.get_total_price() for item in cart_items)
    else:
        # ✅ Guest user: Use session-based cart
        cart = request.session.get("cart", {})
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            total_price = Decimal(product.get_price()) * Decimal(item["quantity"])  # ✅ Convert price to Decimal
            cart_items.append({
                "product": product,
                "quantity": item["quantity"],
                "total_price": total_price
            })
            cart_subtotal += total_price

    shipping_cost = Decimal("2.00")  # ✅ Convert to Decimal
    order_total = cart_subtotal + shipping_cost  # ✅ Fix the TypeError

    context = {
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal,
        "shipping_cost": shipping_cost,
        "order_total": order_total,
    }

    return render(request, "myapp/checkout.html", context)


from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("checkout")  # Redirect to checkout after login
    return render(request, "myapp/checkout.html")


def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = CartItem.objects.filter(cart=cart).count() if cart else 0
    else:
        cart = request.session.get("cart", {})
        count = sum(item["quantity"] for item in cart.values())

    return JsonResponse({"count": count})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Coupon

@csrf_exempt
def apply_coupon(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            coupon_code = data.get("coupon_code", "").strip()

            if not coupon_code:
                return JsonResponse({"success": False, "error": "Coupon code cannot be empty."}, status=400)

            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                return JsonResponse({"success": True, "discount": coupon.discount_percentage})
            except Coupon.DoesNotExist:
                return JsonResponse({"success": False, "error": "Invalid or expired coupon code."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid request data."}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to homepage or dashboard
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "myapp/login.html")


from django.shortcuts import render
from .models import TeamMember, Testimonial, Blog

def about(request):
    team_members = TeamMember.objects.all()
    testimonials = Testimonial.objects.all()
    latest_blogs = Blog.objects.order_by("-published_date")[:3]  # ✅ FIXED FIELD NAME

    return render(request, "myapp/about.html", {
        "team_members": team_members,
        "testimonials": testimonials,
        "latest_blogs": latest_blogs,
    })



from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'No Subject')
        message = request.POST.get('message')

        # Sending email (optional)
        send_mail(
            f"New Contact Request: {subject}",
            f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            'your-email@example.com',  # Replace with your actual email
            ['admin@example.com'],  # Replace with your admin email
            fail_silently=False,
        )

        messages.success(request, "Thank you for reaching out! We'll get back to you soon.")
        return redirect('contact')

    return render(request, 'myapp/contact.html')



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, CartItem

def update_cart_quantity(request, product_id):
    """ Updates quantity of an item in cart """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        new_quantity = int(request.POST.get("quantity", 1))

        if request.user.is_authenticated:
            cart_item, _ = CartItem.objects.get_or_create(user=request.user, product=product)
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart = request.session.get("cart", {})
            if str(product_id) in cart:
                cart[str(product_id)]["quantity"] = new_quantity
            request.session["cart"] = cart

        return JsonResponse({"success": True})
    

    from django.http import JsonResponse

def calculate_shipping(request):
    if request.method == "POST":
        country = request.POST.get("country", "")
        state = request.POST.get("state", "")
        city = request.POST.get("city", "")
        zipcode = request.POST.get("zipcode", "")

        # Example logic for shipping cost (replace with your API or logic)
        shipping_cost = 5.00  # Default flat rate
        if country == "US":
            shipping_cost = 10.00
        elif country == "UK":
            shipping_cost = 8.00
        elif country == "CA":
            shipping_cost = 12.00

        return JsonResponse({"cost": shipping_cost})
    return JsonResponse({"error": "Invalid request"}, status=400)


from django.shortcuts import render, get_object_or_404
from .models import Product, Review

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
    # ✅ Get related products from the same category, excluding the current product
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # ✅ Fetch product reviews
    reviews = Review.objects.filter(product=product)

    return render(request, 'myapp/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Review  # Import the necessary models
from django.contrib.auth.decorators import login_required

@login_required
def submit_review(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        title = request.POST.get("title")
        comment = request.POST.get("comment")

        if rating and title and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                title=title,
                comment=comment,
            )
            messages.success(request, "Review submitted successfully!")
        else:
            messages.error(request, "All fields are required!")

    return redirect("product_detail", id=product.id)


from django.shortcuts import render
from .models import Blog  # Assuming you have a BlogPost model

def blog_list(request):
    blogs = Blog.objects.all().order_by('-published_date')  # Fetch latest posts
    return render(request, "myapp/blog.html", {"blogs": blogs})


from django.shortcuts import render, get_object_or_404
from .models import Blog, Category, Tag
from django.db.models.functions import TruncMonth
from django.db.models import Count

from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog, Comment, Category, Tag
from .forms import CommentForm
from django.db.models.functions import TruncMonth
from django.db.models import Count

from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog, Comment
from .forms import CommentForm

def blog_details(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.comments.filter(parent__isnull=True).order_by('-created_at')  # Only top-level comments
    form = CommentForm()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog

            if request.user.is_authenticated:
                comment.user = request.user
            else:
                # ✅ Guest user: Name & email required
                guest_name = form.cleaned_data.get("guest_name")
                guest_email = form.cleaned_data.get("guest_email")
                if not guest_name or not guest_email:
                    return redirect("blog_details", slug=blog.slug)  # Prevent spam

                comment.guest_name = guest_name
                comment.guest_email = guest_email

            # ✅ Handle Replies (Nested Comments)
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)

            comment.save()
            return redirect("blog_details", slug=blog.slug)

    context = {
        "blog": blog,
        "comments": comments,
        "form": form,
    }
    return render(request, "myapp/blog_details.html", context)


def blog_by_archive(request, year, month):
    blogs = Blog.objects.filter(published_date__year=year, published_date__month=month)
    return render(request, "myapp/blog_archive.html", {"blogs": blogs, "year": year, "month": month})

def blog_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    blogs = Blog.objects.filter(tags=tag)
    return render(request, "myapp/blog_tag.html", {"blogs": blogs, "tag": tag})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog, Comment
from .forms import CommentForm

def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog

            # If user is logged in, assign the user
            if request.user.is_authenticated:
                comment.user = request.user
            else:
                # Validate guest name & email
                guest_name = form.cleaned_data.get("guest_name")
                guest_email = form.cleaned_data.get("guest_email")
                
                if not guest_name or not guest_email:
                    return redirect("blog_details", slug=blog.slug)  # Prevent anonymous spam

                comment.guest_name = guest_name
                comment.guest_email = guest_email

            # Handle reply functionality
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)

            comment.save()
            return redirect("blog_details", slug=blog.slug)

    return redirect("blog_details", slug=blog.slug)
