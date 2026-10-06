# E-Commerce Web Development Project

A project-based approach to learning modern web development by building an e-commerce application from the ground up.

The goal is **not just to build an e-commerce site**, but to understand how a real web application works from browser to backend to database.

---

## 1. Project Goal

Build a modular e-commerce web application in multiple phases.

The project will start simple and gradually introduce more advanced concepts.

### Main learning approach

Since backend development is already more familiar:

```
Phase
  │
  ├── Backend
  │
  ├── Frontend
  │
  └── Integration
```

We will first build the backend for a phase, then build its frontend, and finally connect and test everything together.

This allows backend concepts to remain familiar while learning frontend development gradually.

---

# 2. Architecture Philosophy

The project will initially use a **Modular Monolith** architecture.

The application will be one deployable backend application, but internally divided into independent feature modules.

```
                    E-Commerce Application
                             │
              ┌──────────────┴──────────────┐
              │                             │
           Frontend                       Backend
              │                             │
              │                  ┌──────────┼──────────┐
              │                  │          │          │
              │              Products     Users      Orders
              │                  │          │          │
              │                  └──────────┼──────────┘
              │                             │
              │                        PostgreSQL
              │
              └──────────── HTTP / API ─────┘
```

### Why modular?

As the application grows, new features can be added as separate modules:

```
products/
users/
cart/
orders/
payments/
reviews/
coupons/
notifications/
```

This avoids turning the project into one large, difficult-to-maintain codebase.

We will **not** start with microservices.

If the application eventually becomes large enough to justify separate services, individual modules can be extracted later.

---

# 3. Phase 1 — Product Store

## Goal

Build the basic store experience.

A visitor should be able to browse and search products.

An administrator should be able to manage products.

### User flow

```
Home
  │
  ▼
Product Listing
  │
  ├── Search
  ├── Filter
  └── Pagination
  │
  ▼
Product Details
```

### Admin flow

```
Admin
  │
  ▼
Product Management
  │
  ├── Create Product
  ├── View Products
  ├── Update Product
  └── Delete Product
```

---

## Phase 1 Features

### Product Catalog

- Product listing
- Product details
- Product name
- Description
- Price
- Stock quantity
- Product image
- Category
- Creation/update timestamps

### Product Search

Basic search by:

- Product name
- Description

### Product Filtering

Initially:

- Category
- Price range

Additional filters can be added later.

### Pagination

Product lists should not return every product at once.

Example:

```
/products?page=1&limit=20
```

### Product Management

Admin functionality:

```
POST    /products
GET     /products
GET     /products/{id}
PUT     /products/{id}
DELETE  /products/{id}
```

---

# 4. Phase 1 Architecture

```
                        Browser
                           │
                           │ HTTP
                           ▼
                      FastAPI API
                           │
                  ┌────────┴────────┐
                  │                 │
             Product Module      Other Core
                  │
                  ▼
              PostgreSQL
```

### Phase 1 backend

Conceptually:

```
backend/
└── app/
    ├── main.py
    │
    ├── core/
    │
    ├── db/
    │
    ├── d/
    │   ├── models.py
    │   ├── schemas.py
    │   ├── router.py
    │   └── service.py
    │
    └── ...
```

The exact structure will be introduced gradually during implementation rather than creating everything at once.

---

# 5. Phase 1 Development Sequence

## Phase 1A — Backend

### Step 1 — Project setup

Learn/setup:

- Python environment
- FastAPI
- project configuration
- environment variables
- Git

### Step 2 — Database

Set up:

- PostgreSQL
- SQLAlchemy
- Alembic

Learn:

- tables
- primary keys
- foreign keys
- basic relationships
- migrations

### Step 3 — Product module

Create:

```
Product
```

with fields such as:

```
id
name
description
price
stock
category_id
image_url
created_at
updated_at
```

### Step 4 — CRUD API

Implement:

```
Create
Read
Update
Delete
```

### Step 5 — Search/filter/pagination

Add:

```
search
filter
pagination
```

### Step 6 — Backend testing

Test:

- API endpoints
- validation
- database operations
- common error cases

---

# 6. Phase 1B — Frontend

The first frontend will use:

```
HTML
CSS
JavaScript
```

We will intentionally avoid React at this stage.

### Pages

```
/
├── Home
│
├── /products
│   └── Product listing
│
├── /products/{id}
│   └── Product details
│
└── /admin
    └── Product management
```

### Frontend concepts learned

- HTML structure
- CSS layout
- Flexbox
- CSS Grid
- responsive design
- JavaScript
- DOM manipulation
- browser events
- forms
- Fetch API
- JSON
- API integration
- browser DevTools

---

# 7. Phase 1C — Integration

Connect:

```
Frontend
    │
    │ fetch()
    ▼
FastAPI
    │
    ▼
PostgreSQL
```

Example:

```
User opens Products page
        ↓
JavaScript requests /products
        ↓
FastAPI receives request
        ↓
Database query
        ↓
FastAPI returns JSON
        ↓
JavaScript receives JSON
        ↓
Products rendered in browser
```

### Phase 1 completion criteria

Phase 1 is complete when:

- Products can be stored in PostgreSQL
- Products can be managed through the API
- Products can be viewed from the frontend
- Search works
- Filtering works
- Pagination works
- Basic admin product management works
- Frontend and backend communicate correctly

---

# 8. Phase 2 — Real E-Commerce

## Goal

Turn the product store into an actual e-commerce application.

Phase 2 introduces users, authentication, shopping carts, checkout, and orders.

### Main user flow

```
Register / Login
       │
       ▼
Browse Products
       │
       ▼
Product Details
       │
       ▼
Add to Cart
       │
       ▼
Cart
       │
       ▼
Checkout
       │
       ▼
Create Order
       │
       ▼
Order Confirmation
       │
       ▼
My Orders
```

---

# 9. Phase 2 Features

## Authentication

Users can:

- Register
- Login
- Logout
- View their profile

Learn:

- password hashing
- authentication
- authorization
- sessions/tokens
- protected endpoints

---

## User Roles

Initially:

```
Customer
Admin
```

### Customer

Can:

- Browse products
- Manage cart
- Checkout
- View own orders
- Manage profile

### Admin

Can:

- Manage products
- View orders
- Update order status

---

## Shopping Cart

Users can:

- Add products
- Remove products
- Change quantity
- View cart
- See cart total

Example:

```
Cart
──────────────────────
Product       Qty  Price
──────────────────────
Shoes          2    $100
T-Shirt        1     $30
──────────────────────
Total                $130
```

---

## Checkout

Initial checkout:

```
Cart
 ↓
Shipping information
 ↓
Order summary
 ↓
Place order
 ↓
Order created
```

Real payment processing will **not** be introduced initially.

Payment can be simulated first.

---

## Orders

Users can:

- Create an order
- View their orders
- View order details

Admins can:

- View orders
- Update order status

Example statuses:

```
pending
confirmed
processing
shipped
delivered
cancelled
```

---

# 10. Phase 2 Architecture

The backend grows by adding modules rather than restructuring the whole application.

```
backend/
└── app/
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
    │
    └── main.py
```

Conceptually:

```
                         FastAPI
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
   Products              Users/Auth            Orders
       │                    │                    │
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                           Cart
                            │
                            ▼
                       PostgreSQL
```

---

# 11. Phase 2 Development Sequence

## Phase 2A — Backend

Build in this order:

```
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

This order is intentional.

Orders depend on users and products.

Cart depends on users and products.

Checkout depends on cart and orders.

---

## Phase 2B — Frontend

Build:

```
Login
Register
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

Admin:

```
Admin Dashboard
   ├── Products
   └── Orders
```

---

## Phase 2C — Integration

Connect all components:

```
Browser
   │
   ▼
Frontend
   │
   ▼
FastAPI
   │
   ├── Users
   ├── Products
   ├── Cart
   └── Orders
   │
   ▼
PostgreSQL
```

---

# 12. Final Phase 1 + Phase 2 Architecture

At the end of Phase 2, the application should roughly look like:

```
                         E-COMMERCE
                              │
              ┌───────────────┴───────────────┐
              │                               │
           Frontend                         Backend
              │                               │
       HTML/CSS/JavaScript              FastAPI
              │                               │
              │                    ┌──────────┼──────────┐
              │                    │          │          │
              │                Products     Users      Orders
              │                               │          │
              │                              Auth       Cart
              │                    │          │          │
              │                    └──────────┼──────────┘
              │                               │
              └──────────── API ──────────────┘
                                              │
                                              ▼
                                         PostgreSQL
```

This is still one application, but internally modular.

---

# 13. Project Structure

The structure will evolve with the phases.

## Starting structure

```
ecommerce/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/
│   │   └── products/
│   │
│   └── tests/
│
├── frontend/
│
├── .env
├── .gitignore
└── README.md
```

## After Phase 2

```
ecommerce/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │
│   │   ├── db/
│   │   │
│   │   ├── products/
│   │   │
│   │   ├── users/
│   │   │
│   │   ├── auth/
│   │   │
│   │   ├── cart/
│   │   │
│   │   └── orders/
│   │
│   └── tests/
│
├── frontend/
│   │
│   ├── pages/
│   ├── components/
│   ├── css/
│   └── js/
│
├── .env
├── .gitignore
└── README.md
```

The exact frontend structure may change when React is introduced.

---

# 14. Initial Technology Stack

Keep the initial stack small.

## Backend

| Technology | Purpose |
| --- | --- |
| Python | Backend language |
| FastAPI | API framework |
| SQLAlchemy | Database ORM |
| PostgreSQL | Relational database |
| Alembic | Database migrations |
| Pydantic | Data validation |

---

## Frontend

Initially:

| Technology | Purpose |
| --- | --- |
| HTML | Page structure |
| CSS | Styling/layout |
| JavaScript | Interactivity |
| Fetch API | Backend communication |

Later:

```
React
```

will be introduced after the fundamentals are understood.

---

## Development Tools

| Tool | Purpose |
| --- | --- |
| VS Code | Development |
| Git | Version control |
| GitHub | Repository |
| PostgreSQL | Local database |
| Postman/Insomnia | API testing |
| Browser DevTools | Frontend/debugging |

---

## DevOps — Initially

Only learn the essentials:

```
Git
Environment variables
Basic Docker
Docker Compose
```

Docker should be introduced after the basic application is working locally.

Later, when the project is ready for deployment:

```
Docker
CI/CD
HTTPS
Reverse Proxy
Cloud Deployment
Logging
Monitoring
```

---

# 15. Things We Will Deliberately NOT Use Initially

Avoid unnecessary complexity.

We will not start with:

```
Microservices
Kubernetes
Redis
Message queues
Event-driven architecture
Complex caching
GraphQL
Advanced CI/CD
Real payment integration
Recommendation systems
```

These may become useful later, but they are not necessary for learning the fundamentals or building the first version.

---

# 16. Development Rules

### Rule 1 — Learn while building

Do not try to learn the entire frontend ecosystem before writing the application.

Learn a concept when the project needs it.

---

### Rule 2 — Backend first

For each phase:

```
Backend
   ↓
Frontend
   ↓
Integration
```

This matches the development approach of the project.

---

### Rule 3 — Build small increments

Don't build an entire phase before running the application.

Instead:

```
Product model
   ↓
Run/test
   ↓
Product API
   ↓
Run/test
   ↓
Product page
   ↓
Run/test
```

---

### Rule 4 — Prefer simple architecture

Use the simplest design that solves the current problem.

Don't create abstractions for features that don't exist yet.

---

### Rule 5 — Keep modules independent

When adding a feature, ask:

> "Can this functionality live inside its own module?"
> 

For example:

```
products/
cart/
orders/
```

rather than putting everything into a generic `utils` or `services` folder.

---

# 17. Learning Progression

The project should gradually teach the following concepts.

```
PHASE 1
────────

Web fundamentals
      ↓
HTML
      ↓
CSS
      ↓
JavaScript
      ↓
HTTP / APIs
      ↓
FastAPI
      ↓
PostgreSQL
      ↓
SQLAlchemy
      ↓
CRUD
      ↓
Search / Filter / Pagination
      ↓
Frontend ↔ Backend
```

Then:

```
PHASE 2
────────

Authentication
      ↓
Authorization
      ↓
Users
      ↓
Frontend state
      ↓
Cart
      ↓
Database relationships
      ↓
Orders
      ↓
Transactions
      ↓
Checkout
```

Later phases can introduce:

```
React
Testing
Docker
Deployment
Payments
Caching
Background tasks
Advanced security
CI/CD
```

---

# 18. Definition of Success

The project is successful if, by the end, you can look at the application and understand:

```
What happens when a user clicks a button?
            ↓
How does JavaScript handle it?
            ↓
How does it make an HTTP request?
            ↓
How does FastAPI receive it?
            ↓
How does the backend process it?
            ↓
How does it communicate with PostgreSQL?
            ↓
How does the response return?
            ↓
How does the browser update?
```

The purpose of this project is therefore not simply:

> "Build an e-commerce website."
> 

It is:

> **Learn how modern web applications are designed, built, connected, and eventually deployed by building one real application incrementally.**
>