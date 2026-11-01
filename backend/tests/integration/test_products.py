from decimal import Decimal

from app.products.models import Category, Product


# --------------------------------------------------
# 1. Public catalog retrieval & details
# --------------------------------------------------

def test_list_products_empty(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


def test_list_products_returns_all(client, test_product):
    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1

    item = data[0]
    assert item["id"] == test_product.id
    assert item["name"] == "Test Product"
    assert Decimal(str(item["price"])) == Decimal("25.00")
    assert item["stock"] == 10
    assert item["category_id"] == test_product.category_id
    assert "created_at" in item
    assert "updated_at" in item


def test_get_product_by_id_success(client, test_product):
    response = client.get(f"/products/{test_product.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_product.id
    assert data["name"] == test_product.name
    assert Decimal(str(data["price"])) == Decimal("25.00")
    assert data["stock"] == 10


def test_get_product_by_id_not_found(client):
    response = client.get("/products/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


# --------------------------------------------------
# 2. Pagination, search, and filtering
# --------------------------------------------------

def test_list_products_pagination(client, db_session, test_category):
    for i in range(1, 6):
        db_session.add(
            Product(
                name=f"Paginated Product {i}",
                description=f"Description {i}",
                price=Decimal(f"{i * 10}.00"),
                stock=5,
                category_id=test_category.id,
            )
        )
    db_session.flush()

    # Page 1, limit 2
    res_page1 = client.get("/products?page=1&limit=2")
    assert res_page1.status_code == 200
    data_page1 = res_page1.json()
    assert len(data_page1) == 2

    # Page 2, limit 2
    res_page2 = client.get("/products?page=2&limit=2")
    assert res_page2.status_code == 200
    data_page2 = res_page2.json()
    assert len(data_page2) == 2

    # Verify elements are distinct across pages
    ids_page1 = [p["id"] for p in data_page1]
    ids_page2 = [p["id"] for p in data_page2]
    assert set(ids_page1).isdisjoint(set(ids_page2))


def test_list_products_filter_by_category(client, db_session):
    cat_a = Category(name="Category A")
    cat_b = Category(name="Category B")
    db_session.add_all([cat_a, cat_b])
    db_session.flush()

    prod_a = Product(
        name="Laptop",
        price=Decimal("1000.00"),
        stock=5,
        category_id=cat_a.id,
    )
    prod_b = Product(
        name="T-Shirt",
        price=Decimal("20.00"),
        stock=15,
        category_id=cat_b.id,
    )
    db_session.add_all([prod_a, prod_b])
    db_session.flush()

    response = client.get(f"/products?category_id={cat_a.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"
    assert data[0]["category_id"] == cat_a.id


def test_list_products_filter_by_price_range(client, db_session, test_category):
    cheap = Product(name="Pen", price=Decimal("2.50"), stock=100, category_id=test_category.id)
    mid = Product(name="Book", price=Decimal("15.00"), stock=50, category_id=test_category.id)
    expensive = Product(name="Phone", price=Decimal("500.00"), stock=10, category_id=test_category.id)
    db_session.add_all([cheap, mid, expensive])
    db_session.flush()

    response = client.get("/products?min_price=10&max_price=100")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Book"


def test_list_products_search_by_name_and_description(client, db_session, test_category):
    p1 = Product(name="Wireless Gaming Mouse", description="Ergonomic RGB optical sensor", price=Decimal("49.99"), stock=10, category_id=test_category.id)
    p2 = Product(name="Office Desk", description="Contains mouse pad drawer", price=Decimal("120.00"), stock=5, category_id=test_category.id)
    p3 = Product(name="Coffee Mug", description="Ceramic 350ml cup", price=Decimal("9.99"), stock=20, category_id=test_category.id)
    db_session.add_all([p1, p2, p3])
    db_session.flush()

    # Search by name substring (case-insensitive)
    res_search1 = client.get("/products?search=gaming")
    assert res_search1.status_code == 200
    data1 = res_search1.json()
    assert len(data1) == 1
    assert data1[0]["name"] == "Wireless Gaming Mouse"

    # Search matches description
    res_search2 = client.get("/products?search=mouse pad")
    assert res_search2.status_code == 200
    data2 = res_search2.json()
    assert len(data2) == 1
    assert data2[0]["name"] == "Office Desk"


# --------------------------------------------------
# 3. Category creation & permissions
# --------------------------------------------------

def test_admin_can_create_category(admin_client):
    response = admin_client.post(
        "/products/create_category",
        json={"name": "Books & Stationery"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Books & Stationery"
    assert "id" in data


def test_unauthenticated_cannot_create_category(client):
    response = client.post(
        "/products/create_category",
        json={"name": "Hacked Category"},
    )

    assert response.status_code == 401


def test_customer_cannot_create_category(authenticated_client):
    response = authenticated_client.post(
        "/products/create_category",
        json={"name": "Hacked Category"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_cannot_create_category_with_empty_name(admin_client):
    response = admin_client.post(
        "/products/create_category",
        json={"name": ""},
    )

    assert response.status_code == 422


# --------------------------------------------------
# 4. Product creation & permissions
# --------------------------------------------------

def test_admin_can_create_product(admin_client, test_category):
    payload = {
        "name": "New Mechanical Keyboard",
        "description": "Tactile brown switches",
        "price": 89.99,
        "stock": 25,
        "category_id": test_category.id,
        "image_url": "https://example.com/keyboard.jpg",
    }

    response = admin_client.post("/products", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Mechanical Keyboard"
    assert Decimal(str(data["price"])) == Decimal("89.99")
    assert data["stock"] == 25
    assert data["category_id"] == test_category.id
    assert data["image_url"] == "https://example.com/keyboard.jpg"
    assert "id" in data


def test_unauthenticated_cannot_create_product(client, test_category):
    response = client.post(
        "/products",
        json={
            "name": "Unauthorized Product",
            "price": 10.00,
            "stock": 1,
            "category_id": test_category.id,
        },
    )

    assert response.status_code == 401


def test_customer_cannot_create_product(authenticated_client, test_category):
    response = authenticated_client.post(
        "/products",
        json={
            "name": "Unauthorized Product",
            "price": 10.00,
            "stock": 1,
            "category_id": test_category.id,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_cannot_create_product_with_zero_or_negative_price(admin_client, test_category):
    response_zero = admin_client.post(
        "/products",
        json={
            "name": "Free Product",
            "price": 0,
            "stock": 5,
            "category_id": test_category.id,
        },
    )
    assert response_zero.status_code == 422

    response_neg = admin_client.post(
        "/products",
        json={
            "name": "Negative Product",
            "price": -15.50,
            "stock": 5,
            "category_id": test_category.id,
        },
    )
    assert response_neg.status_code == 422


def test_cannot_create_product_with_negative_stock(admin_client, test_category):
    response = admin_client.post(
        "/products",
        json={
            "name": "Negative Stock Product",
            "price": 19.99,
            "stock": -1,
            "category_id": test_category.id,
        },
    )

    assert response.status_code == 422


def test_cannot_create_product_missing_required_fields(admin_client):
    response = admin_client.post(
        "/products",
        json={"name": "Incomplete Product"},
    )

    assert response.status_code == 422


# --------------------------------------------------
# 5. Product updating & permissions
# --------------------------------------------------

def test_admin_can_update_product(admin_client, test_product):
    update_payload = {
        "name": "Updated Test Product",
        "price": 35.50,
        "stock": 40,
    }

    response = admin_client.put(
        f"/products/{test_product.id}",
        json=update_payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_product.id
    assert data["name"] == "Updated Test Product"
    assert Decimal(str(data["price"])) == Decimal("35.50")
    assert data["stock"] == 40


def test_unauthenticated_cannot_update_product(client, test_product):
    response = client.put(
        f"/products/{test_product.id}",
        json={"name": "Unauthorized Update"},
    )

    assert response.status_code == 401


def test_customer_cannot_update_product(authenticated_client, test_product):
    response = authenticated_client.put(
        f"/products/{test_product.id}",
        json={"name": "Unauthorized Update"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_cannot_update_nonexistent_product(admin_client):
    response = admin_client.put(
        "/products/99999",
        json={"name": "Ghost Product"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_cannot_update_product_with_invalid_price(admin_client, test_product):
    response = admin_client.put(
        f"/products/{test_product.id}",
        json={"price": -5.00},
    )

    assert response.status_code == 422


# --------------------------------------------------
# 6. Product deletion & permissions
# --------------------------------------------------

def test_admin_can_delete_product(admin_client, client, test_product):
    delete_res = admin_client.delete(f"/products/{test_product.id}")
    assert delete_res.status_code == 204

    # Verify it is no longer found in catalog
    get_res = client.get(f"/products/{test_product.id}")
    assert get_res.status_code == 404


def test_unauthenticated_cannot_delete_product(client, test_product):
    response = client.delete(f"/products/{test_product.id}")
    assert response.status_code == 401


def test_customer_cannot_delete_product(authenticated_client, test_product):
    response = authenticated_client.delete(f"/products/{test_product.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_cannot_delete_nonexistent_product(admin_client):
    response = admin_client.delete("/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

