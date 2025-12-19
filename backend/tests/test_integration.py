import pytest

def test_full_shopping_flow(client, auth_headers, admin_headers, sample_products, db_session):
    """
    Test complete shopping flow:
    1. Browse products
    2. Add to cart
    3. Update cart
    4. Checkout
    5. View order history
    """
    # 1. Browse products
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    
    # 2. Add items to cart
    product1 = products[0]
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": product1["id"], "quantity": 2}
    )
    assert response.status_code == 200
    
    product2 = products[1]
    response = client.post(
        "/orders/cart",
        headers=auth_headers,
        json={"product_id": product2["id"], "quantity": 1}
    )
    assert response.status_code == 200
    
    # 3. View cart
    response = client.get("/orders/cart", headers=auth_headers)
    cart = response.json()
    assert len(cart["items"]) == 2
    expected_total = (product1["price"] * 2) + product2["price"]
    assert abs(cart["total"] - expected_total) < 0.01
    
    # 4. Checkout
    response = client.post("/orders/checkout", headers=auth_headers)
    assert response.status_code == 200
    order = response.json()
    assert order["status"] == "completed"
    
    # 5. View order history
    response = client.get("/orders", headers=auth_headers)
    orders = response.json()
    assert len(orders) >= 1
    assert orders[0]["id"] == order["id"]

def test_admin_product_management(client, admin_headers):
    """Test admin CRUD operations on products"""
    # Create
    response = client.post(
        "/products",
        headers=admin_headers,
        json={
            "name": "Admin Test Product",
            "description": "Test",
            "price": 99.99,
            "stock": 50,
            "category": "Test"
        }
    )
    assert response.status_code == 200
    product = response.json()
    product_id = product["id"]
    
    # Read
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Admin Test Product"
    
    # Update
    response = client.put(
        f"/products/{product_id}",
        headers=admin_headers,
        json={
            "name": "Updated Product",
            "description": "Updated",
            "price": 79.99,
            "stock": 30,
            "category": "Test"
        }
    )
    assert response.status_code == 200
    assert response.json()["price"] == 79.99
    
    # Delete
    response = client.delete(f"/products/{product_id}", headers=admin_headers)
    assert response.status_code == 200
    
    # Verify deleted
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404