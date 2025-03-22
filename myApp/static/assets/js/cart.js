console.log("✅ cart.js loaded");


document.addEventListener("DOMContentLoaded", function () {
    // ===== INIT =====
    updateCartCount();
    try { updateCartDisplay(); } catch (e) { console.warn("Cart display not on this page."); }

    // ===== ADD TO CART BUTTON (STANDARD PRODUCT PAGE) =====
    const addToCartBtn = document.getElementById("addToCartBtn");
    if (addToCartBtn) {
        addToCartBtn.addEventListener("click", function () {
            const productId = this.getAttribute("data-product-id");
            const quantityInput = document.querySelector(".pro-qty input");
            const quantity = quantityInput ? quantityInput.value : 1;

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ quantity: quantity }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartCount();
                    alert(data.message);
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Error adding to cart:", error));
        });
    }

    // ===== QUICK VIEW ADD TO CART =====
    const quickAddBtn = document.getElementById("quickAddToCart");
    if (quickAddBtn) {
        quickAddBtn.addEventListener("click", function () {
            const productId = this.getAttribute("data-product-id");
            const quantity = document.getElementById("quickQuantity").value || 1;

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartCount();
                    alert(data.message);
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => console.error("Quick add failed:", error));
        });
    }

    // ===== QUANTITY CHANGE =====
    document.querySelectorAll(".quantity").forEach(input => {
        input.addEventListener("change", function () {
            const productId = this.dataset.productId;
            const newQty = this.value;

            fetch(`/cart/update/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ quantity: newQty })
            })
            .then(res => res.json())
            .then(() => updateCartDisplay())
            .catch(err => console.error("Qty update error:", err));
        });
    });

    // ===== REMOVE ITEM =====
    // Toast function
function showToast(message, duration = 3000) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.style.position = "fixed";
        toast.style.bottom = "20px";
        toast.style.right = "20px";
        toast.style.background = "#333";
        toast.style.color = "#fff";
        toast.style.padding = "12px 20px";
        toast.style.borderRadius = "8px";
        toast.style.display = "none";
        toast.style.zIndex = "9999";
        document.body.appendChild(toast);
    }

    toast.innerText = message;
    toast.style.display = "block";

    setTimeout(() => {
        toast.style.display = "none";
    }, duration);
}

// Add-to-cart removal logic with toast
document.querySelectorAll(".remove-item").forEach(btn => {
    btn.addEventListener("click", function (e) {
        e.preventDefault();
        const cartItemId = this.dataset.cartItemId;

        fetch(`/cart/remove/${cartItemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Or fade out item then update subtotal
            } else {
                alert(data.error || "Failed to remove item.");
            }
        })
        .catch(err => console.error("Remove error:", err));
    });
});

    // ===== CLEAR CART =====
    const clearCartBtn = document.querySelector(".clear-cart");
    if (clearCartBtn) {
        clearCartBtn.addEventListener("click", function (e) {
            e.preventDefault();
            if (!confirm("Clear all items in cart?")) return;

            fetch("/cart/clear/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById("cart-items").innerHTML = "<tr><td colspan='6'>Your cart is empty.</td></tr>";
                    updateCartDisplay();
                } else {
                    alert("Something went wrong.");
                }
            })
            .catch(err => console.error("Clear cart error:", err));
        });
    }

    // ===== SHIPPING OPTIONS =====
    document.querySelectorAll('input[name="shipping"]').forEach(input => {
        input.addEventListener("change", updateCartDisplay);
    });
});



// ===== UTILITIES =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getShippingCost() {
    const selected = document.querySelector('input[name="shipping"]:checked');
    if (!selected) return 0.00;
    if (selected.value === "flat_rate") return 5.00;
    if (selected.value === "local_pickup") return 2.00;
    return 0.00;
}

function updateCartCount() {
    fetch("/cart/count/")
        .then(res => res.json())
        .then(data => {
            const countElem = document.getElementById("cart-count");
            if (countElem) countElem.textContent = data.cart_count;
        })
        .catch(err => console.error("Error updating cart count:", err));
}

function updateCartDisplay() {
    const subtotalElem = document.getElementById("cart-subtotal");
    const totalElem = document.getElementById("cart-total");

    if (!subtotalElem || !totalElem) return;

    let subtotal = 0;

    document.querySelectorAll(".cart-product-item").forEach(row => {
        const priceElement = row.querySelector(".product-price .price");
        const quantityInput = row.querySelector(".quantity");
        const subtotalElement = row.querySelector(".product-subtotal .price");

        const price = parseFloat(priceElement.textContent.replace("₱", "")) || 0;
        const quantity = parseInt(quantityInput.value) || 1;
        const itemTotal = price * quantity;

        subtotal += itemTotal;
        if (subtotalElement) subtotalElement.textContent = `₱${itemTotal.toFixed(2)}`;
    });

    const shipping = getShippingCost();
    const grandTotal = subtotal + shipping;

    subtotalElem.textContent = `₱${subtotal.toFixed(2)}`;
    totalElem.textContent = `₱${grandTotal.toFixed(2)}`;
}

// ===== QUICK VIEW (Optional Section) =====
// ===== QUICK VIEW (Optional Section) =====

// ✅ QUICK VIEW: Open the modal and populate content
function openQuickView(productId) {
    const quickViewModal = document.getElementById("productQuickView");
    const addToCartBtn = quickViewModal.querySelector(".quick-add-to-cart");

    // ✅ Set the correct product ID on the button
    if (addToCartBtn) {
        addToCartBtn.setAttribute("data-product-id", productId);
    }

    fetch(`/quick-view/${productId}/`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("quick-view-title").innerText = data.name;
            document.getElementById("quick-view-description").innerText = data.description;
            document.getElementById("quick-view-image").src = data.image_url;
            document.getElementById("quick-view-price").innerText = `₱${data.price}`;

            const oldPrice = document.getElementById("quick-view-old-price");
            oldPrice.style.display = data.old_price ? "inline" : "none";
            oldPrice.innerText = data.old_price ? `₱${data.old_price}` : "";

            const sizeDropdown = document.getElementById("quickViewSize");
            sizeDropdown.innerHTML = '<option value="">Select a size</option>';
            if (Array.isArray(data.sizes)) {
                data.sizes.forEach(size => {
                    let opt = document.createElement("option");
                    opt.value = size;
                    opt.innerText = size;
                    sizeDropdown.appendChild(opt);
                });
            }

            const colorDropdown = document.getElementById("quickViewColor");
            colorDropdown.innerHTML = '<option value="">Select a color</option>';
            if (Array.isArray(data.colors)) {
                data.colors.forEach(color => {
                    let opt = document.createElement("option");
                    opt.value = color;
                    opt.innerText = color;
                    colorDropdown.appendChild(opt);
                });
            }

            quickViewModal.style.display = "block";
        })
        .catch(error => console.error("Error loading Quick View:", error));
}


// ✅ Close Quick View modal
function closeQuickView() {
    const modal = document.getElementById("productQuickView");
    if (modal) modal.style.display = "none";
}

document.addEventListener("click", function (e) {
    // ✅ Make sure it matches the button in Quick View
    const button = e.target.closest(".quick-add-to-cart");
    if (!button) return;

    const productId = button.getAttribute("data-product-id");
    const quantityInput = document.getElementById("quick-view-quantity");
    const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

    console.log("🛒 Attempting to add to cart:", { productId, quantity });

    if (!productId || productId === "null") {
        console.error("❌ Product ID missing in quick view.");
        alert("Something went wrong. Product not found.");
        return;
    }

    fetch(`/cart/add/${productId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ quantity: quantity }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateCartCount();
            alert(data.message || "Added to cart!");
            closeQuickView();
        } else {
            alert(data.error || "Something went wrong.");
        }
    })
    .catch(err => {
        console.error("🚨 Quick view add-to-cart error:", err);
        alert("Something went wrong. Please check the console.");
    });
});


function loadCartItems() {
    fetch("/cart/items/")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("side-cart-items");
            const subtotalDisplay = document.getElementById("cart-subtotal");

            if (!container) return;

            container.innerHTML = ""; // Clear any previous content

            if (data.items.length === 0) {
                container.innerHTML = "<li><span>Your cart is empty.</span></li>";
                subtotalDisplay.textContent = "₱0.00";
                return;
            }

            let subtotal = 0;

            data.items.forEach(item => {
                const totalPrice = item.quantity * item.price;
                subtotal += totalPrice;

                const li = document.createElement("li");
                li.className = "product-list-item";
                li.innerHTML = `
                    <a href="/cart/remove/${item.id}/" class="remove">×</a>
                    <a href="/product/${item.product_id}/">
                        <img src="${item.image_url}" width="90" height="110" alt="${item.name}">
                        <span class="product-title">${item.name}</span>
                    </a>
                    <span class="product-price">${item.quantity} x ₱${item.price.toFixed(2)}</span>
                `;
                container.appendChild(li);
            });

            subtotalDisplay.textContent = `₱${subtotal.toFixed(2)}`;
        })
        .catch(error => {
            console.error("Error loading side cart items:", error);
        });
}


const cartToggle = document.getElementById("cartToggle");
const offcanvasCart = document.getElementById("AsideOffcanvasCart");

if (cartToggle && offcanvasCart) {
    const cartOffcanvas = new bootstrap.Offcanvas(offcanvasCart);

    cartToggle.addEventListener("click", () => {
        cartOffcanvas.show();
        loadCartItems();  // 💥 Load cart items each time it's opened
    });
}



function loadAsideCart() {
    fetch("/cart/items/")
        .then(res => res.json())
        .then(data => {
            const cartList = document.getElementById("side-cart-items");
            const subtotalElement = document.getElementById("side-cart-subtotal");

            if (!cartList || !subtotalElement) return;

            cartList.innerHTML = ""; // Clear previous items
            let subtotal = 0;

            if (data.items.length === 0) {
                cartList.innerHTML = `<li><span>Your cart is empty.</span></li>`;
            } else {
                data.items.forEach(item => {
                    const total = item.quantity * item.price;
                    subtotal += total;

                    const li = document.createElement("li");
                    li.className = "product-list-item";
                    li.innerHTML = `
                        <a href="/cart/remove/${item.id}/" class="remove">×</a>
                        <a href="/product/${item.product_id}/">
                            <img src="${item.image_url}" width="90" height="110" alt="${item.name}">
                            <span class="product-title">${item.name}</span>
                        </a>
                        <span class="product-price">${item.quantity} x ₱${item.price.toFixed(2)}</span>
                    `;
                    cartList.appendChild(li);
                });
            }

            subtotalElement.textContent = `₱${subtotal.toFixed(2)}`;
        })
        .catch(err => console.error("🛒 Error loading side cart:", err));
}


function showToast(message) {
    const toast = document.getElementById("toast-container");
    toast.textContent = message;
    toast.style.display = "block";

    setTimeout(() => {
        toast.style.display = "none";
    }, 2500);
}