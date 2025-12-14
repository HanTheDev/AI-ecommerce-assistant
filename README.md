# AI E-Commerce Assistant - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Backend Services](#backend-services)
6. [Frontend Application](#frontend-application)
7. [Database Schema](#database-schema)
8. [API Documentation](#api-documentation)
9. [Authentication & Authorization](#authentication--authorization)
10. [AI/ML Features](#aiml-features)
11. [Deployment](#deployment)
12. [Development Setup](#development-setup)
13. [CI/CD Pipeline](#cicd-pipeline)
14. [Future Enhancements](#future-enhancements)

---

## Overview

The AI E-Commerce Assistant is a full-stack web application that combines traditional e-commerce functionality with AI-powered features. The platform provides users with personalized product recommendations and an intelligent shopping assistant.

### Key Features
- User authentication and authorization
- Product catalog management
- Shopping cart functionality
- Order processing and history
- AI-powered product recommendations
- Collaborative filtering for similar products
- Admin dashboard for product management

### Design Goals
- Microservices architecture for scalability
- RESTful API design
- Responsive and modern UI
- Secure authentication flow
- Extensible AI/ML pipeline

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│                  (React + TypeScript + Vite)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────┴──────────────────────────────────────┐
│                      API Gateway Layer                       │
│                     (FastAPI Backend)                        │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Auth     │  │  Products  │  │   Orders   │            │
│  │  Service   │  │  Service   │  │  Service   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │         Recommendations Service                │         │
│  │         (ML-based recommender)                 │         │
│  └────────────────────────────────────────────────┘         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    Database Layer                            │
│                    (PostgreSQL)                              │
└──────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**User Registration/Login:**
```
User → Frontend → Auth Router → Database → JWT Token → User
```

**Product Browsing:**
```
User → Frontend → Products Router → Database → Product List → User
```

**Add to Cart:**
```
User → Frontend → Orders Router → Auth Middleware → Database → Cart Updated
```

**Get Recommendations:**
```
User → Frontend → Recommendations Router → Recommender Service → ML Model → Product IDs
```

---

## Technology Stack

### Frontend
- **Framework**: React 19.1.1
- **Language**: TypeScript 5.8.3
- **Build Tool**: Vite 7.1.7
- **Styling**: Tailwind CSS 4.1.13
- **Routing**: React Router DOM 7.9.2
- **State Management**: React Context API

### Backend
- **Framework**: FastAPI 0.68.1
- **Language**: Python 3.9
- **ASGI Server**: Uvicorn 0.15.0
- **ORM**: SQLAlchemy 1.4.23
- **Database**: PostgreSQL 15
- **Authentication**: JWT (python-jose 3.3.0)
- **Password Hashing**: Bcrypt (passlib 1.7.4)
- **HTTP Client**: HTTPX 0.18.2

### Database
- **RDBMS**: PostgreSQL 15
- **Migration Tool**: Alembic 1.7.4
- **Driver**: psycopg2-binary 2.9.1

### DevOps
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Code Quality**: Ruff (Python linter), ESLint (TypeScript)

### AI/ML (Planned)
- **Framework**: PyTorch / Scikit-learn
- **Technique**: Collaborative Filtering
- **NLP**: LangChain (for shopping assistant)

---

## Project Structure

```
ai-ecommerce-assistant/
├── .github/
│   └── workflows/
│       ├── backend.yml          # Backend CI pipeline
│       └── frontend.yml         # Frontend CI pipeline
├── backend/
│   ├── alembic/                 # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── routers/            # API endpoints
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── products.py     # Product CRUD
│   │   │   ├── orders.py       # Cart & checkout
│   │   │   └── recommendations.py  # ML recommendations
│   │   ├── auth.py             # JWT utilities
│   │   ├── database.py         # DB connection
│   │   ├── deps.py             # Dependency injection
│   │   ├── main.py             # FastAPI app entry
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── startup.py          # Initialization logic
│   ├── dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   │   └── AuthContext.tsx  # Global auth state
│   │   ├── pages/
│   │   │   ├── Admin.tsx        # Product management
│   │   │   ├── Cart.tsx         # Shopping cart
│   │   │   ├── Login.tsx        # Auth page
│   │   │   ├── OrderHistory.tsx # Order list
│   │   │   ├── ProductsList.tsx # Product catalog
│   │   │   └── Profile.tsx      # User profile
│   │   ├── App.tsx
│   │   ├── main.tsx             # App entry + routing
│   │   └── index.css
│   ├── dockerfile
│   └── package.json
├── docker-compose.yml           # Multi-container setup
└── README.md
```

---

## Backend Services

### Core Application (`backend/app/main.py`)

The FastAPI application serves as the main entry point for all backend services.

**Key Configurations:**
- CORS middleware for frontend origin (`http://localhost:5174`)
- Router registration for modular endpoints
- Database initialization on startup
- Admin user seeding

```python
app = FastAPI(title="AI E-commerce Assistant API")

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(recommendations.router)
```

### Authentication Service (`routers/auth.py`)

Handles user registration, login, and token management.

**Endpoints:**
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Authenticate and receive JWT token
- `GET /auth/me` - Get current user information

**Security Implementation:**
- Passwords hashed using bcrypt
- JWT tokens with 30-minute expiration
- Bearer token authentication for protected routes

### Products Service (`routers/products.py`)

Manages product catalog operations.

**Endpoints:**
- `GET /products/` - List all products (paginated)
- `GET /products/{id}` - Get single product details
- `POST /products/` - Create product (admin only)
- `PUT /products/{id}` - Update product (admin only)
- `DELETE /products/{id}` - Delete product (admin only)

**Authorization:**
- Read operations: Public access
- Write operations: Admin role required

### Orders Service (`routers/orders.py`)

Handles shopping cart and order processing.

**Endpoints:**
- `GET /orders/cart` - Retrieve current cart
- `POST /orders/cart` - Add item to cart
- `DELETE /orders/cart/{item_id}` - Remove item from cart
- `POST /orders/checkout` - Convert cart to order
- `GET /orders/` - List user's order history

**Business Logic:**
- Cart stored as unfulfilled order (`status="cart"`)
- Stock validation before adding to cart
- Automatic stock deduction on checkout
- Cart-to-order conversion on successful checkout

### Recommendations Service (`routers/recommendations.py`)

Proxy service for ML-based recommendations (currently references external recommender service).

**Endpoints:**
- `GET /recommendations/similar/{product_id}` - Get similar products
- `GET /recommendations/user/{user_id}` - Get personalized recommendations

**Integration:**
- Communicates with separate recommender microservice
- Uses HTTPX for async HTTP requests
- Returns product IDs for frontend to fetch details

---

## Frontend Application

### Architecture

The frontend follows a component-based architecture with React Router for navigation and Context API for global state management.

### Key Components

#### Authentication Context (`context/AuthContext.tsx`)

Manages global authentication state.

```typescript
interface User {
  id: number;
  email: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
}
```

#### Main Application (`main.tsx`)

- Implements protected routes
- Navigation component with conditional rendering
- Route definitions for all pages

#### Pages

**Login Page (`Login.tsx`)**
- Toggle between login/register forms
- JWT token storage in localStorage
- Automatic user data fetch after login
- Redirect to appropriate page (admin/products)

**Products List (`ProductsList.tsx`)**
- Display all available products
- Product selection modal
- Quantity selector
- Add to cart functionality

**Shopping Cart (`Cart.tsx`)**
- Display cart items with quantities
- Calculate total price
- Remove items from cart
- Checkout button

**Admin Dashboard (`Admin.tsx`)**
- CRUD operations for products
- Form for creating/updating products
- Product list with edit/delete actions
- Admin-only access protection

**Order History (`OrderHistory.tsx`)**
- Display completed orders
- Order items breakdown
- Order total calculation

**Profile (`Profile.tsx`)**
- Display user information
- Logout functionality

### Routing Structure

```typescript
/ - Home page (landing)
/products - Product catalog
/cart - Shopping cart (protected)
/orders - Order history (protected)
/admin - Admin dashboard (admin only)
/login - Authentication page
/profile - User profile (protected)
```

### State Management

- **Local State**: Component-specific data using `useState`
- **Global State**: User authentication via Context API
- **Persistent State**: JWT token in localStorage

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (PK)         │
│ email           │
│ hashed_password │
│ is_admin        │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│     Orders      │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ status          │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐       ┌─────────────────┐
│   Cart_Items    │  N:1  │    Products     │
├─────────────────┤───────┤─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ order_id (FK)   │       │ name            │
│ product_id (FK) │       │ description     │
│ quantity        │       │ price           │
└─────────────────┘       │ stock           │
                          │ created_at      │
                          └────────┬────────┘
                                   │
                                   │ 1:N
                                   │
                          ┌────────▼────────┐
                          │  Product_Views  │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ user_id (FK)    │
                          │ product_id (FK) │
                          │ viewed_at       │
                          └─────────────────┘
```

### Table Definitions

#### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_admin INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Orders
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR DEFAULT 'cart',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Cart_Items
```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER DEFAULT 1
);
```

#### Product_Views
```sql
CREATE TABLE product_views (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /auth/register
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "is_admin": 0,
  "created_at": "2025-01-15T10:30:00"
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```
GET /auth/me
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "is_admin": 0,
  "created_at": "2025-01-15T10:30:00"
}
```

### Products Endpoints

#### List Products
```
GET /products/?skip=0&limit=10

Response: 200 OK
[
  {
    "id": 1,
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 29.99,
    "stock": 50,
    "created_at": "2025-01-15T10:30:00"
  }
]
```

#### Get Product
```
GET /products/1

Response: 200 OK
{
  "id": 1,
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": 29.99,
  "stock": 50,
  "created_at": "2025-01-15T10:30:00"
}
```

#### Create Product (Admin)
```
POST /products/
Authorization: Bearer {admin_token}
Content-Type: application/json

Request Body:
{
  "name": "Mechanical Keyboard",
  "description": "RGB mechanical gaming keyboard",
  "price": 89.99,
  "stock": 30
}

Response: 200 OK
{
  "id": 2,
  "name": "Mechanical Keyboard",
  "description": "RGB mechanical gaming keyboard",
  "price": 89.99,
  "stock": 30,
  "created_at": "2025-01-15T11:00:00"
}
```

### Orders Endpoints

#### Get Cart
```
GET /orders/cart
Authorization: Bearer {token}

Response: 200 OK
{
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "product": {
        "id": 1,
        "name": "Wireless Mouse",
        "price": 29.99
      }
    }
  ],
  "total": 59.98
}
```

#### Add to Cart
```
POST /orders/cart
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "product_id": 1,
  "quantity": 2
}

Response: 200 OK
{
  "items": [...],
  "total": 59.98
}
```

#### Checkout
```
POST /orders/checkout
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "created_at": "2025-01-15T12:00:00",
  "items": [...]
}
```

### Recommendations Endpoints

#### Get Similar Products
```
GET /recommendations/similar/1

Response: 200 OK
[2, 5, 8, 12]
```

#### Get User Recommendations
```
GET /recommendations/user/1
Authorization: Bearer {token}

Response: 200 OK
[3, 7, 9, 15]
```

---

## Authentication & Authorization

### JWT Token Flow

1. User submits credentials to `/auth/login`
2. Backend validates credentials against database
3. If valid, JWT token created with 30-minute expiration
4. Token payload contains user email as subject
5. Frontend stores token in localStorage
6. Frontend includes token in Authorization header for protected requests
7. Backend middleware validates token and extracts user identity

### Token Structure

```json
{
  "sub": "user@example.com",
  "exp": 1705324200
}
```

### Protected Route Middleware

The `get_current_user` dependency:
1. Extracts token from Authorization header
2. Decodes and validates JWT signature
3. Queries database for user by email
4. Returns user object or raises 401 error

### Authorization Levels

- **Public**: Product listing, product details
- **Authenticated**: Cart operations, order history, profile
- **Admin**: Product CRUD operations

---

## AI/ML Features

### Current Implementation Status

The application includes infrastructure for AI/ML features but requires full implementation:

#### Recommender Service (Planned)

**Architecture:**
- Separate microservice (`recommender` container)
- Communicates with main backend via HTTP
- Processes user interaction data from database

**Planned Features:**

1. **Collaborative Filtering**
   - User-based: Find similar users and recommend their purchases
   - Item-based: Find similar products based on co-purchase patterns

2. **Content-Based Filtering**
   - Analyze product descriptions and categories
   - Recommend based on user's browsing history

3. **Hybrid Approach**
   - Combine collaborative and content-based methods
   - Weight recommendations by recency and frequency

**Data Pipeline:**
```
User Interactions → Database → Feature Engineering → 
ML Model → Recommendation Scores → Top-K Products
```

#### Shopping Assistant (Planned)

**Technology:** LangChain + LLM

**Capabilities:**
- Natural language product search
- Conversational product discovery
- Personalized suggestions based on context
- Query examples:
  - "Show me electronics under $50"
  - "What's a good gift for a programmer?"
  - "I need a wireless mouse for gaming"

---

## Deployment

### Docker Compose Setup

The application uses Docker Compose for local development and can be adapted for production deployment.

**Services:**
- `backend`: FastAPI application (port 8001)
- `frontend`: Vite dev server (port 5174)
- `db`: PostgreSQL database (port 5433)
- `recommender`: ML service (port 8002)

### Environment Variables

**Backend (.env file):**
```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secureadminpass
```

**Frontend:**
```bash
VITE_BACKEND_URL=http://localhost:8001
```

### Production Deployment Strategy (Planned)

**Frontend:**
- Build static assets: `npm run build`
- Deploy to AWS S3
- Serve via CloudFront CDN

**Backend:**
- Container deployment on AWS Elastic Beanstalk
- Or: ECS/EKS for better scalability
- Environment variables via AWS Secrets Manager

**Database:**
- AWS RDS PostgreSQL instance
- Automated backups and point-in-time recovery
- Read replicas for scalability

**Recommender Service:**
- Separate ECS/Lambda deployment
- Batch inference for offline recommendations
- Real-time inference via API endpoint

---

## Development Setup

### Prerequisites

- Docker Desktop
- Node.js 22+ (for local frontend development)
- Python 3.9+ (for local backend development)

### Quick Start

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/ai-ecommerce-assistant.git
cd ai-ecommerce-assistant
```

2. **Configure Backend Environment**
```bash
cd backend
cat > .env << EOF
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
EOF
```

3. **Start All Services**
```bash
docker-compose up --build
```

4. **Access Applications**
- Frontend: http://localhost:5174
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs
- Database: localhost:5433

### Development Workflow

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Database Migrations:**
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

#### Backend CI (`.github/workflows/backend.yml`)

**Triggers:**
- Push to main branch (backend changes)
- Pull request to main (backend changes)

**Steps:**
1. Checkout code
2. Set up Docker Buildx
3. Build backend container
4. Run linting with Ruff
5. Run tests with pytest (when implemented)

#### Frontend CI (`.github/workflows/frontend.yml`)

**Triggers:**
- Push to main branch (frontend changes)
- Pull request to main (frontend changes)

**Steps:**
1. Checkout code
2. Set up Docker Buildx
3. Build frontend container
4. Install dependencies
5. Run ESLint
6. Build production bundle
7. Upload build artifacts

### Code Quality

**Backend:**
- Ruff for linting and formatting
- Pytest for unit/integration tests (planned)

**Frontend:**
- ESLint for TypeScript linting
- TypeScript compiler for type checking

---

## Future Enhancements

### Phase 1: Core ML Features
- [ ] Implement collaborative filtering algorithm
- [ ] Build offline batch recommendation pipeline
- [ ] Create recommendation training pipeline
- [ ] Add A/B testing framework for recommendations

### Phase 2: AI Shopping Assistant
- [ ] Integrate LangChain for NLP
- [ ] Connect LLM (OpenAI GPT or open-source alternative)
- [ ] Build conversation memory and context
- [ ] Implement product query parser

### Phase 3: Advanced Features
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Payment integration (Stripe)
- [ ] Email notifications
- [ ] Product image upload
- [ ] Advanced search and filtering

### Phase 4: Analytics & Optimization
- [ ] User behavior tracking
- [ ] Analytics dashboard
- [ ] Performance monitoring
- [ ] Recommendation metrics (CTR, conversion)

### Phase 5: Production Readiness
- [ ] Comprehensive test coverage (>80%)
- [ ] Load testing and optimization
- [ ] Security audit
- [ ] Documentation completion
- [ ] AWS deployment scripts
- [ ] Monitoring and alerting setup

---

## Appendix

### API Base URL
- Development: `http://localhost:8001`
- Production: TBD

### Database Connection
- Development: `postgresql://postgres:postgres@localhost:5433/postgres`
- Production: AWS RDS endpoint

### Contact & Support
- GitHub Issues: [Repository Issues]
- Developer: [Your Name]
- Email: [Your Email]

---

**Document Version:** 1.0  
**Last Updated:** November 29, 2025  
**Status:** In Development