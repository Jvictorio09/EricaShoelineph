from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login, authenticate
from .models import Product, Category, SpecialOffer, Feature, ProductCollection, Testimonial, Cart, CartItem, Coupon, TeamMember, Blog
from myApp.context_processors import cart_context

def home(request):
    main_category = Category.objects.filter(is_main_header=True).first()
    featured_categories = Category.objects.filter(show_on_homepage=True)[:3]
    products = Product.objects.all()  # Fetch all products dynamically
    special_offer = SpecialOffer.objects.first()
    features = Feature.objects.all()
    best_sellers = Product.objects.filter(best_seller=True)
    product_collections = ProductCollection.objects.all()
    testimonials = Testimonial.objects.all()

    context = {
        "main_category": main_category,
        "categories": featured_categories,
        "products": products,
        'special_offer': special_offer,
        'features': features,
        'best_sellers': best_sellers,
        "product_collections": product_collections,
        "testimonials": testimonials
    }
    return render(request, "myApp/index.html", context)



# views.py



from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def shop_category(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)  # Filter dynamically
    
     
    return render(request, 'myApp/shop_category.html', {
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
    
     
    return render(request, 'myApp/shop.html', context)


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


from decimal import Decimal

def get_cart_data(request):
    items = []
    subtotal = Decimal("0.00")

    if request.user.is_authenticated:
        cart_items = CartItem.objects.select_related("product").filter(user=request.user)

        for item in cart_items:
            product = item.product
            price = Decimal(product.get_price())
            quantity = item.quantity
            subtotal += price * quantity

            items.append({
                "id": item.id,
                "product_id": product.id,
                "name": product.name,
                "image_url": product.image.url if product.image else "",
                "quantity": quantity,
                "price": float(price),
            })

    else:
        cart = request.session.get("cart", {})
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                price = Decimal(product.get_price())
                quantity = item["quantity"]
                subtotal += price * quantity

                items.append({
                    "id": product.id,
                    "product_id": product.id,
                    "name": product.name,
                    "image_url": product.image.url if product.image else "",
                    "quantity": quantity,
                    "price": float(price),
                })
            except Product.DoesNotExist:
                continue

    return JsonResponse({
        "items": items,
        "cart_subtotal": float(subtotal),
    })



from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CartItem

@require_POST
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id)

        if request.user.is_authenticated:
            if cart_item.user == request.user:
                cart_item.delete()
            else:
                return JsonResponse({"success": False, "error": "Unauthorized access."}, status=403)

        else:
            session_id = request.session.get("session_id")
            if cart_item.cart.session_id == session_id:
                cart_item.delete()
            else:
                return JsonResponse({"success": False, "error": "Unauthorized session."}, status=403)

        return JsonResponse({"success": True, "message": "Item removed successfully!"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


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
from django.shortcuts import render
from .models import CartItem, Product
from decimal import Decimal  # ✅ Import Decimal

def cart_view(request):
    cart_items = []
    cart_subtotal = Decimal("0.00")  # ✅ Ensure cart_subtotal is Decimal

    if request.user.is_authenticated:
        # ✅ Logged-in user: Fetch cart from DB
        cart_items = CartItem.objects.filter(user=request.user)
        cart_subtotal = sum(item.total_price for item in cart_items)


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

    return render(request, "myApp/cart.html", context)




def checkout(request):
    cart_items = []
    cart_subtotal = Decimal("0.00")  # ✅ Ensure cart_subtotal is Decimal

    if request.user.is_authenticated:
        # ✅ Logged-in user: Fetch cart from DB
        cart_items = CartItem.objects.filter(user=request.user)
        cart_subtotal = sum(item.total_price for item in cart_items)
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

    return render(request, "myApp/checkout.html", context)


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
    return render(request, "myApp/checkout.html")


from django.http import JsonResponse
from .models import Cart, CartItem

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = CartItem.objects.filter(cart=cart).count() if cart else 0
    else:
        session_id = request.session.get("session_id")
        cart = Cart.objects.filter(session_id=session_id).first()
        count = CartItem.objects.filter(cart=cart).count() if cart else 0

    return JsonResponse({
        "success": True,
        "message": "Item added to cart!",
        "cart_count": count
    })



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
    
    return render(request, "myApp/login.html")


from django.shortcuts import render
from .models import TeamMember, Testimonial, Blog, AboutSection

def about(request):
    team_members = TeamMember.objects.all()
    testimonials = Testimonial.objects.all()
    latest_blogs = Blog.objects.order_by("-published_date")[:3]  # ✅ FIXED FIELD NAME
    about_sections = AboutSection.objects.all().order_by('order')

    return render(request, "myApp/about.html", {
        "team_members": team_members,
        "testimonials": testimonials,
        "latest_blogs": latest_blogs,
        "about_sections": about_sections,
    })




from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

def contact_view(request):
    if request.method == 'POST':
        print("POST received!")  # Debug

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject') or 'General Inquiry'
        message = request.POST.get('message')

        full_message = f"""
        New Contact Submission:

        Name: {name}
        Email: {email}
        Subject: {subject}
        Message:
        {message}
        """

        try:
            # Send to your inbox
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            # Auto-reply to user
            send_mail(
                subject="We Received Your Message!",
                message=f"Hi {name},\n\nThanks for reaching out! We'll get back to you shortly.\n\nBlessings,\nThe Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')

        except Exception as e:
            print("Email failed:", e)
            messages.error(request, "Something went wrong. Please try again later.")
            return redirect('contact')

    return render(request, 'myApp/contact.html')



# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, CartItem, Cart
import json
import uuid

@csrf_exempt
def update_cart_quantity(request, product_id):
    """ Updates the quantity of an item in the cart via AJAX """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_quantity = int(data.get("quantity", 1))
        except (ValueError, json.JSONDecodeError):
            return JsonResponse({"success": False, "error": "Invalid data"}, status=400)

        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product, user=request.user)
        else:
            session_id = request.session.get("session_id")
            if not session_id:
                session_id = str(uuid.uuid4())
                request.session["session_id"] = session_id
            cart, _ = Cart.objects.get_or_create(session_id=session_id)
            cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product, user=None)

        cart_item.quantity = new_quantity
        cart_item.save()

        return JsonResponse({"success": True, "new_quantity": cart_item.quantity})

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)



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

     
    return render(request, 'myApp/product_detail.html', {
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
    return render(request, "myApp/blog.html", {"blogs": blogs})


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
    return render(request, "myApp/blog_details.html", context)


def blog_by_archive(request, year, month):
    blogs = Blog.objects.filter(published_date__year=year, published_date__month=month)
    return render(request, "myApp/blog_archive.html", {"blogs": blogs, "year": year, "month": month})

def blog_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    blogs = Blog.objects.filter(tags=tag)
    return render(request, "myApp/blog_tag.html", {"blogs": blogs, "tag": tag})


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


