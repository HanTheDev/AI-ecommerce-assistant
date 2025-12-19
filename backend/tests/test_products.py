def test_list_products(client, sample_products):
    """Test listing products"""
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Laptop"

def test_get_product(client, sample_products):
    """Test getting a specific product"""
    product_id = sample_products[0].id
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99

def test_get_nonexistent_product(client):
    """Test getting a product that doesn't exist"""
    response = client.get("/products/999")
    assert response.status_code == 404

def test_create_product_as_admin(client, admin_headers, db_session):
    """Test creating a product as admin"""
    response = client.post(
        "/products",
        headers=admin_headers,
        json={
            "name": "New Product",
            "description": "Test description",
            "price": 49.99,
            "stock": 100,
            "category": "Test"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Product"
    assert data["price"] == 49.99

def test_create_product_as_user(client, auth_headers):
    """Test creating a product as regular user (should fail)"""
    response = client.post(
        "/products",
        headers=auth_headers,
        json={
            "name": "New Product",
            "price": 49.99,
            "stock": 100
        }
    )
    assert response.status_code == 403

def test_create_product_no_auth(client):
    """Test creating a product without authentication"""
    response = client.post(
        "/products",
        json={"name": "New Product", "price": 49.99, "stock": 100}
    )
    assert response.status_code == 401

def test_update_product(client, admin_headers, sample_products):
    """Test updating a product"""
    product_id = sample_products[0].id
    response = client.put(
        f"/products/{product_id}",
        headers=admin_headers,
        json={
            "name": "Updated Laptop",
            "description": "Updated description",
            "price": 899.99,
            "stock": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Laptop"
    assert data["price"] == 899.99

def test_delete_product(client, admin_headers, sample_products):
    """Test deleting a product"""
    product_id = sample_products[2].id
    response = client.delete(f"/products/{product_id}", headers=admin_headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404