from django.urls import path
from . import views  # Import views from the same app
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordResetView


urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('category/<int:id>/', views.shop_category, name='shop_category'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/<int:id>/submit_review/', views.submit_review, name='submit_review'),  # Add this line

    path('shop/', views.shop, name='shop'),
    path('quick-view/<int:product_id>/', views.quick_view, name="quick_view"),

    path("cart-data/", views.get_cart_data, name="cart-data"),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('cart/clear/', views.clear_cart, name='clear_cart'),

    path("checkout/", views.checkout, name="checkout"),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
   
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("about/", views.about, name="about"),
    path('contact/', views.contact, name='contact'),
    path("cart/count/", views.cart_count, name="cart_count"),

    path("calculate-shipping/", views.calculate_shipping, name="calculate_shipping"),

    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_details, name="blog_details"),
    path("blog/archive/<int:year>/<int:month>/", views.blog_by_archive, name="blog_by_archive"),
    path("blog/tag/<str:tag_name>/", views.blog_by_tag, name="blog_by_tag"),

    path("blog/<slug:slug>/comment/", views.add_comment, name="add_comment"),
]
