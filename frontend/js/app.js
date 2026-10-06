/* ==========================================================================
   E-Commerce Store Frontend Logic (app.js)
   Connects to FastAPI backend (http://localhost:8000)
   Handles fetching, rendering, search, category filtering & pagination
   ========================================================================== */

// 1. Configuration & Global State
const API_BASE_URL = "http://localhost:8000";
const PAGE_LIMIT = 6; // 6 products per page for neat 2x3 or 3x2 grid

let currentPage = 1;
let selectedCategory = ""; // "" = All, "1" = Electronics, "2" = Clothing
let searchQuery = "";
let cartCount = 0;

// The DOM is basically the browser's JavaScript representation of your HTML page.
// 2. DOM Elements
const productsGrid = document.getElementById("productsGrid");
const productCount = document.getElementById("productCount");
const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const categoryRadios = document.querySelectorAll('input[name="categoryFilter"]');
const clearFiltersBtn = document.getElementById("clearFiltersBtn");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const pageIndicator = document.getElementById("pageIndicator");
const cartBtn = document.getElementById("cartBtn");

// 3. Fetch Products from Backend API
async function fetchProducts() {
    // Show loading state
    productsGrid.innerHTML = `
        <div class="status-card">
            <p>⏳ Loading products from catalog...</p>
        </div>
    `;

    // Build URL Query Parameters: /products?page=X&limit=Y&category_id=Z&search=W
    const params = new URLSearchParams({
        page: currentPage,
        limit: PAGE_LIMIT
    });

    if (selectedCategory) {
        params.append("category_id", selectedCategory);
    }

    if (searchQuery) {
        params.append("search", searchQuery);
    }

    const requestUrl = `${API_BASE_URL}/products?${params.toString()}`;
    console.log("Fetching:", requestUrl);

    try {
        const response = await fetch(requestUrl);

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const products = await response.json();
        renderProducts(products);
        updatePagination(products.length);

    } catch (error) {
        console.error("Failed to load products:", error);
        productsGrid.innerHTML = `
            <div class="status-card" style="color: #ef4444;">
                <p>⚠️ Could not connect to backend API.</p>
                <p style="font-size: 0.85rem; margin-top: 0.5rem; color: #64748b;">
                    Make sure your FastAPI server is running on <code>http://localhost:8000</code>.
                </p>
            </div>
        `;
        productCount.textContent = "";
    }
}

// 4. Render Product Cards into DOM
function renderProducts(products) {
    productsGrid.innerHTML = "";

    if (!products || products.length === 0) {
        productsGrid.innerHTML = `
            <div class="status-card">
                <p>🔍 No products found matching your criteria.</p>
                <p style="font-size: 0.85rem; margin-top: 0.5rem;">
                    Try clearing your search or switching categories.
                </p>
            </div>
        `;
        productCount.textContent = "0 products found";
        return;
    }

    productCount.textContent = `Showing ${products.length} product${products.length > 1 ? "s" : ""}`;

    products.forEach(product => {
        const card = document.createElement("div");
        card.className = "product-card";

        // Format price and stock badge
        const formattedPrice = Number(product.price).toFixed(2);
        const inStock = product.stock > 0;
        const stockBadge = inStock
            ? `<span class="product-stock">In Stock (${product.stock})</span>`
            : `<span class="product-stock out-of-stock">Out of Stock</span>`;

        // Image with graceful fallback if missing or broken URL
        const imageUrl = product.image_url || "";
        const imageElement = imageUrl
            ? `<img src="${imageUrl}" alt="${escapeHtml(product.name)}" onerror="this.onerror=null; this.parentElement.innerHTML='<span class=\\'img-placeholder\\'>📦</span>';">`
            : `<span class="img-placeholder">📦</span>`;

        card.innerHTML = `
            <div class="product-thumb">
                ${imageElement}
            </div>

            <div class="product-details">
                <div>
                    <h3 class="product-title" title="${escapeHtml(product.name)}">${escapeHtml(product.name)}</h3>
                    <p class="product-description">${escapeHtml(product.description || "No description provided.")}</p>
                </div>

                <div>
                    <div class="product-meta">
                        <span class="product-price">$${formattedPrice}</span>
                        ${stockBadge}
                    </div>

                    <button class="btn btn-primary add-to-cart-btn" data-id="${product.id}" ${!inStock ? "disabled" : ""}>
                        ${inStock ? "Add to Cart" : "Sold Out"}
                    </button>
                </div>
            </div>
        `;

        // Attach "Add to Cart" event
        const addToCartBtn = card.querySelector(".add-to-cart-btn");
        if (inStock && addToCartBtn) {
            addToCartBtn.addEventListener("click", () => handleAddToCart(product, addToCartBtn));
        }

        productsGrid.appendChild(card);
    });
}

// 5. Cart Feedback Functionality
function handleAddToCart(product, button) {
    cartCount++;
    cartBtn.textContent = `Cart (${cartCount})`;

    // Brief visual feedback on the button
    const originalText = button.textContent;
    button.textContent = "✓ Added!";
    button.style.backgroundColor = "#16a34a";

    setTimeout(() => {
        button.textContent = originalText;
        button.style.backgroundColor = "";
    }, 900);
}

// 6. Pagination Controls
function updatePagination(itemsReceived) {
    pageIndicator.textContent = `Page ${currentPage}`;

    // Disable "Previous" if on first page
    prevBtn.disabled = (currentPage === 1);

    // Disable "Next" if current page has fewer items than PAGE_LIMIT
    nextBtn.disabled = (itemsReceived < PAGE_LIMIT);
}

// 7. Utility to prevent XSS in displayed product text
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 8. Event Listeners Setup

// Search Form Submit
searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    searchQuery = searchInput.value.trim();
    currentPage = 1; // Reset to first page
    fetchProducts();
});

// Category Radio Selection
categoryRadios.forEach(radio => {
    radio.addEventListener("change", (e) => {
        selectedCategory = e.target.value;
        currentPage = 1; // Reset to first page
        fetchProducts();
    });
});

// Clear Filters Button
clearFiltersBtn.addEventListener("click", () => {
    searchQuery = "";
    searchInput.value = "";
    selectedCategory = "";
    
    // Check the "All Products" radio
    const allRadio = document.querySelector('input[name="categoryFilter"][value=""]');
    if (allRadio) allRadio.checked = true;

    currentPage = 1;
    fetchProducts();
});

// Pagination Navigation
prevBtn.addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        fetchProducts();
    }
});

nextBtn.addEventListener("click", () => {
    currentPage++;
    fetchProducts();
});

// Cart Header Button
cartBtn.addEventListener("click", () => {
    alert(`You have ${cartCount} item(s) in your cart!`);
});

// 9. Initial Load on Page Startup
document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
});