
from decimal import Decimal

from app.cart.models import Cart, CartItem
from app.users.models import User


# --------------------------------------------------
# Helper
# --------------------------------------------------

def get_item(response, product_id):
    for item in response.json()["items"]:
        if item["product_id"] == product_id:
            return item

    return None


# --------------------------------------------------
# 1. Authentication tests
# --------------------------------------------------

def test_unauthenticated_user_cannot_access_cart(client):
    response = client.get("/cart")

    assert response.status_code == 401


# --------------------------------------------------
# 2. Cart retrieval tests
# --------------------------------------------------

def test_customer_can_get_empty_cart(authenticated_client):
    response = authenticated_client.get("/cart")

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert Decimal(str(data["total"])) == Decimal("0")


def test_customer_can_get_cart_with_items(
    authenticated_client,
    test_product,
):
    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == test_product.id
    assert data["items"][0]["quantity"] == 2


# --------------------------------------------------
# 3. Adding cart items
# --------------------------------------------------

def test_customer_can_add_product(
    authenticated_client,
    test_product,
):
    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["product_id"] == test_product.id
    assert item["quantity"] == 2
    assert Decimal(str(item["unit_price"])) == Decimal("25.00")
    assert Decimal(str(item["subtotal"])) == Decimal("50.00")
    assert Decimal(str(data["total"])) == Decimal("50.00")


def test_adding_same_product_increases_quantity(
    authenticated_client,
    test_product,
):
    authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 5


def test_cannot_add_nonexistent_product(authenticated_client):
    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": 999999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404


def test_cannot_add_zero_quantity(
    authenticated_client,
    test_product,
):
    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 0,
        },
    )

    assert response.status_code == 422


def test_cannot_add_negative_quantity(
    authenticated_client,
    test_product,
):
    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": -1,
        },
    )

    assert response.status_code == 422


def test_cannot_add_quantity_exceeding_stock(
    authenticated_client,
    test_product,
):
    response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 11,
        },
    )

    assert response.status_code == 409


# --------------------------------------------------
# 4. Updating cart items
# --------------------------------------------------

def test_customer_can_update_cart_item(
    authenticated_client,
    test_product,
):
    add_response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    item_id = add_response.json()["items"][0]["id"]

    response = authenticated_client.put(
        f"/cart/items/{item_id}",
        json={
            "quantity": 4,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"][0]["quantity"] == 4
    assert Decimal(str(data["items"][0]["subtotal"])) == Decimal("100.00")
    assert Decimal(str(data["total"])) == Decimal("100.00")


def test_cannot_update_quantity_beyond_stock(
    authenticated_client,
    test_product,
):
    add_response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    item_id = add_response.json()["items"][0]["id"]

    response = authenticated_client.put(
        f"/cart/items/{item_id}",
        json={
            "quantity": 11,
        },
    )

    assert response.status_code == 409


def test_cannot_update_quantity_to_zero(
    authenticated_client,
    test_product,
):
    add_response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    item_id = add_response.json()["items"][0]["id"]

    response = authenticated_client.put(
        f"/cart/items/{item_id}",
        json={
            "quantity": 0,
        },
    )

    assert response.status_code == 422


def test_cannot_update_nonexistent_cart_item(authenticated_client):
    response = authenticated_client.put(
        "/cart/items/999999",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 404


# --------------------------------------------------
# 5. Removing cart items
# --------------------------------------------------

def test_customer_can_remove_cart_item(
    authenticated_client,
    test_product,
):
    add_response = authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    item_id = add_response.json()["items"][0]["id"]

    response = authenticated_client.delete(
        f"/cart/items/{item_id}"
    )

    assert response.status_code == 204

    cart_response = authenticated_client.get("/cart")

    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []


def test_customer_can_clear_cart(
    authenticated_client,
    test_product,
):
    authenticated_client.post(
        "/cart/items",
        json={
            "product_id": test_product.id,
            "quantity": 2,
        },
    )

    response = authenticated_client.delete("/cart")

    assert response.status_code == 204

    cart_response = authenticated_client.get("/cart")

    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == []


def test_customer_can_clear_empty_cart(authenticated_client):
    response = authenticated_client.delete("/cart")

    assert response.status_code == 204


# --------------------------------------------------
# 6. Cart ownership
# --------------------------------------------------

def test_customer_cannot_remove_another_customers_item(
    authenticated_client,
    db_session,
    test_product,
):
    # Create another customer.
    other_user = User(
        name="Other Customer",
        email="other@test.com",
        password_hash="not-used-in-this-test",
        role="customer",
    )

    db_session.add(other_user)
    db_session.flush()

    # Create another customer's cart.
    other_cart = Cart(
        user_id=other_user.id,
    )

    db_session.add(other_cart)
    db_session.flush()

    # Add an item to that cart.
    other_cart_item = CartItem(
        cart_id=other_cart.id,
        product_id=test_product.id,
        quantity=2,
    )

    db_session.add(other_cart_item)
    db_session.flush()

    response = authenticated_client.delete(
        f"/cart/items/{other_cart_item.id}"
    )

    assert response.status_code == 404
