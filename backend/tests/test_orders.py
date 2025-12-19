import pytest

def test_get_empty_cart(client, auth_headers):
    """Test getting an empty cart"""
    response = client.get("/orders/cart", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0.0

def test_add_to_cart(client, auth_headers, sample_products):
    """Test adding items to cart"""
    product_id = sample_products[0].id
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": product_id, "quantity": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == 999.99 * 2

def test_add_to_cart_insufficient_stock(client, auth_headers, sample_products):
    """Test adding more items than available stock"""
    product_id = sample_products[0].id
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": product_id, "quantity": 1000}
    )
    assert response.status_code == 400
    assert "stock" in response.json()["detail"].lower()

def test_add_multiple_items_to_cart(client, auth_headers, sample_products):
    """Test adding multiple different products to cart"""
    # Add first product
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": sample_products[0].id, "quantity": 1}
    )
    assert response.status_code == 200
    
    # Add second product
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": sample_products[1].id, "quantity": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2

def test_update_cart_quantity(client, auth_headers, sample_products):
    """Test updating quantity of existing cart item"""
    product_id = sample_products[0].id
    
    # Add item
    client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": product_id, "quantity": 1}
    )
    
    # Add same item again (should increase quantity)
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": product_id, "quantity": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["quantity"] == 3

def test_remove_from_cart(client, auth_headers, sample_products):
    """Test removing items from cart"""
    # Add item
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": sample_products[0].id, "quantity": 1}
    )
    cart_item_id = response.json()["items"][0]["id"]
    
    # Remove item
    response = client.delete(f"/orders/cart/{cart_item_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify cart is empty
    response = client.get("/orders/cart", headers=auth_headers)
    data = response.json()
    assert len(data["items"]) == 0

def test_checkout(client, auth_headers, sample_products, db_session):
    """Test checkout process"""
    # Add items to cart
    client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": sample_products[0].id, "quantity": 2}
    )
    
    # Get initial stock
    initial_stock = sample_products[0].stock
    
    # Checkout
    response = client.post("/orders/checkout", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["items"]) == 1
    
    # Verify stock was decreased
    db_session.refresh(sample_products[0])
    assert sample_products[0].stock == initial_stock - 2
    
    # Verify cart is empty
    response = client.get("/orders/cart", headers=auth_headers)
    assert len(response.json()["items"]) == 0

def test_checkout_empty_cart(client, auth_headers):
    """Test checkout with empty cart"""
    response = client.post("/orders/checkout", headers=auth_headers)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_list_orders(client, auth_headers, sample_products):
    """Test listing user's orders"""
    # Create an order
    client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": sample_products[0].id, "quantity": 1}
    )
    client.post("/orders/checkout", headers=auth_headers)
    
    # List orders
    response = client.get("/orders", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["status"] == "completed"