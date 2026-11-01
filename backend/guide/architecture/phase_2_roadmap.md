# E-Commerce Project — Phase 2 Roadmap

## Phase 2 — Real E-Commerce

### Goal

Turn the Phase 1 product store into a real e-commerce application.

Phase 2 introduces:

- Users
- Authentication
- Authorization / roles
- Shopping carts
- Orders
- Checkout

The development order is intentional:

```text
1. Users
   ↓
2. Authentication
   ↓
3. Authorization / Roles
   ↓
4. Cart
   ↓
5. Orders
   ↓
6. Checkout
```

---

# Phase 2A — Backend

We will build the backend first, following the same modular-monolith architecture and 4-layer pattern used in Phase 1:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Database
```

For every module, the learning/development sequence will be:

```text
1. Understand the concept
       ↓
2. Design the database
       ↓
3. Create SQLAlchemy model
       ↓
4. Create Alembic migration
       ↓
5. Create Pydantic schemas
       ↓
6. Create repository
       ↓
7. Create service
       ↓
8. Create router
       ↓
9. Test through Swagger/cURL
       ↓
10. Move to frontend
```

---

# Step 1 — Users

First, create the User module.

```text
backend/
└── app/
    ├── core/
    ├── db/
    ├── products/
    │
    └── users/
        ├── models.py
        ├── schemas.py
        ├── repository.py
        ├── service.py
        └── routers.py
```

## User database model

Conceptually:

```text
users
────────────────────
id
name
email
password_hash
role
created_at
updated_at
```

Example:

```text
id:            1
name:          User
email:         user@example.com
password_hash: $2b$12$....
role:          customer
```

### Important

Never store the user's actual password.

Instead:

```text
Plain password
      ↓
Password hashing
      ↓
Password hash
      ↓
Store hash in PostgreSQL
```

At this stage, learn:

- User database modeling
- Unique email
- Password hash storage
- User roles
- Alembic migrations
- User CRUD/profile concepts

---

# Step 2 — Authentication

After the User module works, introduce authentication.

Create:

```text
auth/
├── schemas.py
├── service.py
└── routers.py
```

Initial endpoints:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Registration flow

```text
REGISTER
   │
   ▼
User sends email + password
   │
   ▼
Validate input
   │
   ▼
Hash password
   │
   ▼
Save user in database
   │
   ▼
Registration complete
```

## Login flow

```text
LOGIN
   │
   ▼
User sends email + password
   │
   ▼
Find user in database
   │
   ▼
Verify password
   │
   ▼
Generate JWT token
   │
   ▼
Return token
```

### Concepts to learn

- Password hashing
- Authentication
- JWT
- Login
- Protected endpoints
- Current authenticated user

---

# Step 3 — Authorization & Roles

Introduce two initial roles:

```text
Customer
Admin
```

Authentication answers:

```text
"Who are you?"
```

Authorization answers:

```text
"What are you allowed to do?"
```

## Customer

Customers can:

```text
Browse products
Manage cart
Checkout
View their own orders
Manage their profile
```

Example protected endpoints:

```text
GET  /products
GET  /products/{id}

POST /cart/items
GET  /cart

POST /orders
GET  /orders
```

## Admin

Admins can:

```text
Manage products
View orders
Update order status
```

Example:

```text
POST   /products
PUT    /products/{id}
DELETE /products/{id}

GET    /orders
PUT    /orders/{id}/status
```

### Concepts to learn

- Role-based authorization
- Protected routes
- Dependency-based authentication
- Permission checks

---

# Step 4 — Shopping Cart

Create:

```text
cart/
├── models.py
├── schemas.py
├── repository.py
├── service.py
└── routers.py
```

The Phase 1 cart is currently only frontend state.

Phase 2 changes this into persistent database state.

## Database

### carts

```text
carts
────────────────
id
user_id
created_at
updated_at
```

### cart_items

```text
cart_items
────────────────
id
cart_id
product_id
quantity
```

## Relationship

```text
User
 │
 │ 1
 ▼
Cart
 │
 │ 1
 │
 ├───────────┐
 │           │
 ▼           ▼
CartItem   CartItem
 │           │
 ▼           ▼
Product    Product
```

## Cart functionality

Users should be able to:

```text
Add product
Remove product
Change quantity
View cart
See cart total
Clear cart
```

Example endpoints:

```text
GET    /cart
POST   /cart/items
PUT    /cart/items/{item_id}
DELETE /cart/items/{item_id}
DELETE /cart
```

### Important learning point

The cart should no longer depend on:

```javascript
let cartCount = 0;
```

Instead:

```text
Browser
   ↓
FastAPI
   ↓
PostgreSQL
   ↓
User's persistent cart
```

Therefore, the cart can survive page refreshes and user sessions.

---

# Step 5 — Orders

Create:

```text
orders/
├── models.py
├── schemas.py
├── repository.py
├── service.py
└── routers.py
```

## Database

### orders

```text
orders
────────────────
id
user_id
status
total_amount
shipping_address
created_at
```

### order_items

```text
order_items
────────────────
id
order_id
product_id
quantity
unit_price
```

## Relationship

```text
User
  │
  ▼
Order
  │
  ├── OrderItem → Product
  ├── OrderItem → Product
  └── OrderItem → Product
```

## Order status

Initially:

```text
pending
   ↓
confirmed
   ↓
processing
   ↓
shipped
   ↓
delivered
```

Possible cancellation:

```text
pending → cancelled
```

Customers can:

```text
Create an order
View their orders
View order details
```

Admins can:

```text
View orders
Update order status
```

## Important database concept — historical price

`order_items` stores:

```text
unit_price
```

This preserves the price at the time of purchase.

Example:

```text
Purchase date:
Shoes = $100

Order:
Shoes
Quantity: 1
Unit price: $100
```

If the product later becomes:

```text
Shoes = $150
```

the old order must still show:

```text
Shoes = $100
```

This prevents historical orders from changing when the current product price changes.

---

# Step 6 — Checkout

Checkout connects the cart and order systems.

Initial checkout flow:

```text
Cart
  ↓
Checkout
  ↓
Shipping information
  ↓
Order summary
  ↓
Place order
  ↓
Create order
  ↓
Clear cart
  ↓
Order confirmation
```

For the initial Phase 2 implementation:

**Do not implement real payment processing yet.**

Payment can be simulated.

---

# Phase 2 Backend Architecture

By the end of Phase 2A:

```text
backend/
└── app/
    ├── main.py
    │
    ├── core/
    │
    ├── db/
    │
    ├── products/
    │
    ├── users/
    │
    ├── auth/
    │
    ├── cart/
    │
    └── orders/
```

Conceptually:

```text
                         FastAPI
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
      Products          Users/Auth          Orders
          │                 │                 │
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                           Cart
                            │
                            ▼
                       PostgreSQL
```

---

# Phase 2B — Frontend

Only after the corresponding backend functionality is working, expand the frontend.

## Customer flow

```text
Register / Login
      ↓
Product Store
      ↓
Product Details
      ↓
Cart
      ↓
Checkout
      ↓
Order Confirmation
      ↓
My Orders
```

Pages/features:

```text
Login
Register
Products
Product Details
Cart
Checkout
Order Confirmation
My Orders
Profile
```

## Admin

```text
Admin Dashboard
      │
      ├── Products
      │
      └── Orders
```

Admin functionality:

```text
Create products
Edit products
Delete products
Update inventory
View orders
Update order status
```

---

# Phase 2C — Integration

At the end, the complete system should look like:

```text
Browser
   │
   ▼
Frontend
   │
   ▼
FastAPI
   │
   ├── Users
   ├── Authentication
   ├── Products
   ├── Cart
   └── Orders
   │
   ▼
PostgreSQL
```

Example user flow:

```text
User
 ↓
Login
 ↓
JWT authentication
 ↓
Browse products
 ↓
Add product to cart
 ↓
Cart saved in PostgreSQL
 ↓
Checkout
 ↓
Create order
 ↓
Clear cart
 ↓
Order confirmation
 ↓
My Orders
```

---

# Complete Phase 2 Roadmap

```text
                    PHASE 2
                       │
                       ▼
              ┌─────────────────┐
              │ 1. USERS        │
              │ User Model      │
              │ User Data       │
              │ Profile         │
              └────────┬────────┘
                       ↓
              ┌─────────────────┐
              │ 2. AUTH         │
              │ Register        │
              │ Login           │
              │ JWT             │
              │ /auth/me        │
              └────────┬────────┘
                       ↓
              ┌─────────────────┐
              │ 3. AUTHORIZATION│
              │ Customer/Admin  │
              │ Protected APIs  │
              └────────┬────────┘
                       ↓
              ┌─────────────────┐
              │ 4. CART         │
              │ Cart            │
              │ Cart Items      │
              │ Persistent Data │
              └────────┬────────┘
                       ↓
              ┌─────────────────┐
              │ 5. ORDERS       │
              │ Orders          │
              │ Order Items     │
              │ Order Status    │
              └────────┬────────┘
                       ↓
              ┌─────────────────┐
              │ 6. CHECKOUT     │
              │ Cart → Order    │
              │ Confirmation    │
              └─────────────────┘
```

---

# Development Rules for Phase 2

## Rule 1 — Backend first

For each feature:

```text
Backend
   ↓
Frontend
   ↓
Integration
```

## Rule 2 — Build small increments

Do not implement an entire module before testing it.

Instead:

```text
User model
   ↓
Run migration
   ↓
Test
   ↓
User repository
   ↓
Test
   ↓
User service
   ↓
Test
   ↓
User router
   ↓
Test
```

## Rule 3 — Follow the existing architecture

Continue using the modular monolith.

Do not introduce microservices.

Continue separating:

```text
Router
Service
Repository
Model
Schema
```

## Rule 4 — Keep the technology stack simple

Do not introduce unnecessary technologies during Phase 2.

Avoid for now:

```text
Microservices
Kubernetes
Redis
Message queues
GraphQL
Complex caching
Real payment integration
Recommendation systems
Advanced CI/CD
```

These can be introduced in later phases when the application actually needs them.

---

# Phase 2 Learning Goals

By completing Phase 2, you should understand:

```text
Users
   ↓
Authentication
   ↓
Authorization
   ↓
JWT
   ↓
Password hashing
   ↓
Protected API endpoints
   ↓
Database relationships
   ↓
Persistent shopping carts
   ↓
Orders
   ↓
Order items
   ↓
Transactions
   ↓
Checkout
```

More importantly, you should be able to trace a real request:

```text
User clicks "Add to Cart"
        ↓
JavaScript event handler
        ↓
fetch()
        ↓
HTTP request
        ↓
FastAPI router
        ↓
Authentication
        ↓
Authorization
        ↓
Service
        ↓
Repository
        ↓
SQLAlchemy
        ↓
PostgreSQL
        ↓
Response
        ↓
JavaScript
        ↓
UI update
```

---

# Phase 2 Starting Point

**We begin with Step 1 — Users.**

Do not start with JWT yet.

First build and understand:

```text
users/
├── models.py
├── schemas.py
├── repository.py
├── service.py
└── routers.py
```

Then:

```text
User model
    ↓
Alembic migration
    ↓
users table
    ↓
User API
    ↓
Testing
```

Once the User module is solid, move to Authentication.

---

# Phase 2 Definition of Success

Phase 2 is complete when:

- Users can register.
- Users can log in.
- Passwords are securely hashed.
- JWT authentication works.
- Protected endpoints require authentication.
- Customer/Admin roles work.
- Customers can manage their carts.
- Cart data persists in PostgreSQL.
- Customers can create orders.
- Customers can view their own orders.
- Admins can view orders.
- Admins can update order status.
- Checkout converts a cart into an order.
- The cart is cleared after successful order creation.
- Frontend and backend communicate correctly.
- The complete customer flow works from registration to order history.

---

## Immediate Next Task

### Phase 2 → Step 1 → Users

Start with:

```text
1. Design users table
2. Create User SQLAlchemy model
3. Create Alembic migration
4. Create User schemas
5. Create User repository
6. Create User service
7. Create User router
8. Test User API
```

Only after these are working should we move to:

```text
Step 2 — Authentication
```

This keeps Phase 2 incremental, understandable, and consistent with the architecture established in Phase 1.
