# myApp/context_processors.py
from .models import CartItem, Product
from decimal import Decimal

def cart_context(request):
    cart_items = []
    cart_subtotal = Decimal("0.00")

    if request.user.is_authenticated:
        items = CartItem.objects.select_related('product').filter(user=request.user)
        cart_items = items
        for item in items:
            cart_subtotal += item.product.get_price() * item.quantity
    else:
        cart = request.session.get("cart", {})
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                total = product.get_price() * item["quantity"]
                cart_items.append({
                    "product": product,
                    "quantity": item["quantity"],
                    "total_price": total,
                })
                cart_subtotal += total
            except Product.DoesNotExist:
                continue

    return {
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal
    }
