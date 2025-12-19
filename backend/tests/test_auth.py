import pytest
from fastapi.testclient import TestClient

def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert data["is_admin"] is False

def test_register_duplicate_email(client, test_user):
    """Test registration with existing email"""
    response = client.post(
        "/auth/register",
        json={
            "email": test_user.email,
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_register_weak_password(client):
    """Test registration with weak password"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "weak"
        }
    )
    assert response.status_code == 400
    assert "password" in response.json()["detail"].lower()

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "TestPassword123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email

def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data

def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/auth/me")
    assert response.status_code == 401