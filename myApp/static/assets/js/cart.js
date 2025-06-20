console.log("✅ cart.js loaded");

document.addEventListener("DOMContentLoaded", function () {
    updateCartCount();
    try { updateCartDisplay(); } catch (e) {}

    // ✅ ADD TO CART (from product detail page)
    const addToCartBtn = document.getElementById("addToCartBtn");
    if (addToCartBtn) {
        addToCartBtn.addEventListener("click", function () {
            const productId = this.getAttribute("data-product-id");
            const quantityInput = document.querySelector(".pro-qty input");
            const quantity = quantityInput ? quantityInput.value : 1;

            this.disabled = true;
            const originalText = this.textContent;
            this.textContent = "Adding...";

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ quantity }),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    updateCartCount();
                    loadCartItems();           // ✅ refresh aside cart contents
                    cartOffcanvas.show();      // ✅ open the aside cart (optional UX)
                    showToast("🛒 Added to cart!");
                } else {
                    alert(data.error || "Failed to add to cart.");
                }
            })
            .catch(err => {
                console.error("Add to cart error:", err);
                alert("Something went wrong.");
            })
            .finally(() => {
                this.disabled = false;
                this.textContent = originalText;
            });
        });
    }

    // ✅ ADD TO CART (grid button)
    document.querySelectorAll(".quick-add-to-cart").forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const productId = this.getAttribute("data-product-id");
            const quantity = 1;

            this.classList.add("disabled");
            const originalHTML = this.innerHTML;
            this.innerHTML = `<i class="fa fa-spinner fa-spin"></i>`;

            fetch(`/cart/add/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ quantity }),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    updateCartCount();
                    showToast("🛒 Product added!");
                } else {
                    alert(data.error || "Failed to add to cart.");
                }
            })
            .catch(err => {
                console.error("Grid add error:", err);
            })
            .finally(() => {
                this.classList.remove("disabled");
                this.innerHTML = originalHTML;
            });
        });
    });

    // ✅ ADD TO CART (from quick view modal)
    document.addEventListener("click", function (e) {
        const button = e.target.closest(".quick-add-to-cart");
        if (!button || !button.closest("#productQuickView")) return;

        const productId = button.getAttribute("data-product-id");
        const quantityInput = document.getElementById("quick-view-quantity");
        const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = `<i class="fa fa-spinner fa-spin"></i> Adding...`;

        fetch(`/cart/add/${productId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ quantity }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateCartCount();
                showToast("🛒 Added to cart!");
                closeQuickView();
            } else {
                alert(data.error || "Failed to add to cart.");
            }
        })
        .catch(err => {
            console.error("Modal add error:", err);
        })
        .finally(() => {
            button.disabled = false;
            button.innerHTML = originalHTML;
        });
    });

    // ✅ REMOVE FROM CART
    document.querySelectorAll(".remove-item").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const cartItemId = this.dataset.cartItemId;
            const row = this.closest("tr");
            if (row) {
                row.style.opacity = "0.5";
                this.disabled = true;
            }

            fetch(`/cart/remove/${cartItemId}/`, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (row) row.remove();
                    updateCartCount();
                    updateCartDisplay();
                    showToast("🧺 Item removed!");
                } else {
                    if (row) {
                        row.style.opacity = "1";
                        this.disabled = false;
                    }
                    alert(data.error || "Failed to remove item.");
                }
            })
            .catch(err => {
                console.error("Remove error:", err);
            });
        });
    });

    // ✅ CLEAR CART
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

    // ✅ QUANTITY UPDATE
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

    // ✅ SHIPPING CHANGE
    document.querySelectorAll('input[name="shipping"]').forEach(input => {
        input.addEventListener("change", updateCartDisplay);
    });
});

// =======================
// 🔧 Utility Functions
// =======================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
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
        const price = parseFloat(row.querySelector(".product-price .price").textContent.replace("₱", "")) || 0;
        const qty = parseInt(row.querySelector(".quantity").value) || 1;
        const total = price * qty;
        subtotal += total;

        const subtotalEl = row.querySelector(".product-subtotal .price");
        if (subtotalEl) subtotalEl.textContent = `₱${total.toFixed(2)}`;
    });

    const shipping = getShippingCost();
    const grandTotal = subtotal + shipping;

    subtotalElem.textContent = `₱${subtotal.toFixed(2)}`;
    totalElem.textContent = `₱${grandTotal.toFixed(2)}`;
}

function getShippingCost() {
    const selected = document.querySelector('input[name="shipping"]:checked');
    if (!selected) return 0.00;
    if (selected.value === "flat_rate") return 5.00;
    if (selected.value === "local_pickup") return 2.00;
    return 0.00;
}

function showToast(message) {
    let toast = document.getElementById("toast-container");

    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast-container";
        toast.style.position = "fixed";
        toast.style.bottom = "20px";
        toast.style.right = "20px";
        toast.style.background = "#333";
        toast.style.color = "#fff";
        toast.style.padding = "12px 20px";
        toast.style.borderRadius = "8px";
        toast.style.zIndex = "9999";
        toast.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
        toast.style.fontSize = "14px";
        toast.style.display = "none";

        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.style.display = "block";

    setTimeout(() => {
        toast.style.display = "none";
    }, 2500);
}

function closeQuickView() {
    const modal = document.getElementById("productQuickView");
    if (modal) modal.style.display = "none";
}

function loadCartItems() {
    const container = document.getElementById("side-cart-items");
    const subtotalDisplay = document.getElementById("cart-subtotal");

    if (!container) return;

    container.innerHTML = `
        <li class="loading-cart">
            <span>⏳ Loading your items...</span>
        </li>
    `;
    if (subtotalDisplay) subtotalDisplay.textContent = "…";

    fetch("/cart/items/")
        .then(res => res.json())
        .then(data => {
            container.innerHTML = "";

            if (!data.cart_items.length) {
                container.innerHTML = "<li><span>Your cart is empty.</span></li>";
                if (subtotalDisplay) subtotalDisplay.textContent = "₱0.00";
                return;
            }

            let subtotal = 0;

            data.cart_items.forEach(item => {
                const totalPrice = item.quantity * item.price;
                subtotal += totalPrice;

                const li = document.createElement("li");
                li.className = "product-list-item";
                li.innerHTML = `
                    <a href="#" class="remove remove-item" data-cart-item-id="${item.id}">×</a>
                    <a href="/product/${item.product_id}/">
                        <img src="${item.image}" width="90" height="110" alt="${item.name}">
                        <span class="product-title">${item.name}</span>
                    </a>
                    <span class="product-price">${item.quantity} x ₱${item.price.toFixed(2)}</span>
                `;
                container.appendChild(li);
            });

            if (subtotalDisplay) {
                subtotalDisplay.textContent = `₱${subtotal.toFixed(2)}`;
            }

            // ✅ Bind remove buttons inside the loaded items
            container.querySelectorAll(".remove-item").forEach(btn => {
                btn.addEventListener("click", function (e) {
                    e.preventDefault();
                    const cartItemId = this.dataset.cartItemId;
                    const itemElement = this.closest(".product-list-item");

                    if (itemElement) {
                        itemElement.style.opacity = "0.5";
                        this.disabled = true;
                    }

                    fetch(`/cart/remove/${cartItemId}/`, {
                        method: "POST",
                        headers: { "X-CSRFToken": getCookie("csrftoken") }
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            if (itemElement) itemElement.remove();
                            updateCartCount();
                            showToast("🧺 Item removed!");
                            loadCartItems(); // Refresh to reflect new subtotal
                        } else {
                            if (itemElement) {
                                itemElement.style.opacity = "1";
                                this.disabled = false;
                            }
                            alert(data.error || "Failed to remove item.");
                        }
                    })
                    .catch(err => {
                        console.error("Remove error:", err);
                        if (itemElement) {
                            itemElement.style.opacity = "1";
                            this.disabled = false;
                        }
                    });
                });
            });

        })
        .catch(error => {
            console.error("Error loading side cart items:", error);
            container.innerHTML = `<li><span>⚠️ Failed to load cart items.</span></li>`;
        });
}

const cartToggle = document.getElementById("cartToggle");
const offcanvasCart = document.getElementById("AsideOffcanvasCart");

if (cartToggle && offcanvasCart) {
    const cartOffcanvas = new bootstrap.Offcanvas(offcanvasCart);

    cartToggle.addEventListener("click", () => {
        cartOffcanvas.show();
        loadCartItems();  // <== This is the function that was missing
    });
}


function openQuickView(productId) {
    const quickViewModal = document.getElementById("productQuickView");
    const loader = document.getElementById("quickViewLoader");
    if (loader) loader.style.display = "block";

    quickViewModal.style.display = "none";

    fetch(`/quick-view/${productId}/`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("quick-view-title").innerText = data.name;
            document.getElementById("quick-view-description").innerText = data.description;
            document.getElementById("quick-view-image").src = data.image_url;
            document.getElementById("quick-view-price").innerText = `₱${data.price}`;

            const oldPrice = document.getElementById("quick-view-old-price");
            if (oldPrice) {
                oldPrice.style.display = data.old_price ? "inline" : "none";
                oldPrice.innerText = data.old_price ? `₱${data.old_price}` : "";
            }

            const sizeDropdown = document.getElementById("quickViewSize");
            if (sizeDropdown) {
                sizeDropdown.innerHTML = '<option value="">Select a size</option>';
                data.sizes?.forEach(size => {
                    const opt = document.createElement("option");
                    opt.value = size;
                    opt.innerText = size;
                    sizeDropdown.appendChild(opt);
                });
            }

            const colorDropdown = document.getElementById("quickViewColor");
            if (colorDropdown) {
                colorDropdown.innerHTML = '<option value="">Select a color</option>';
                data.colors?.forEach(color => {
                    const opt = document.createElement("option");
                    opt.value = color;
                    opt.innerText = color;
                    colorDropdown.appendChild(opt);
                });
            }

            const addToCartBtn = quickViewModal.querySelector(".quick-add-to-cart");
            if (addToCartBtn) {
                addToCartBtn.setAttribute("data-product-id", productId);
            }

            if (loader) loader.style.display = "none";
            quickViewModal.style.display = "block";
        })
        .catch(error => {
            console.error("Quick View error:", error);
            if (loader) loader.style.display = "none";
            alert("⚠️ Failed to load product details.");
        });
}
