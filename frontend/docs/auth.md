# Phase 2 Frontend --- Authentication (`auth.md`)

## 1. Purpose

This document records the frontend architecture and implementation plan
for the Authentication part of Phase 2 of the e-commerce project.

Use it as the working reference while implementing the login and
registration experience. Keep it aligned with the main
`architecture.md`.

## 2. Project principles

-   **Frontend technology:** HTML, CSS, vanilla JavaScript, and the
    Fetch API.
-   **No React yet:** learn and implement the fundamentals first; React
    can be introduced later.
-   **Backend first, then frontend integration:** the FastAPI
    authentication endpoints already exist and have been tested in
    Swagger.
-   **Build incrementally:** implement a small part, run it, test it,
    and then continue.
-   **Preserve Phase 1:** extend the existing frontend instead of
    replacing it.
-   **Keep responsibilities separate:** HTML provides structure, CSS
    handles presentation, and JavaScript handles behavior and API
    communication.
-   **Backend is authoritative:** frontend role checks improve the user
    experience, but the backend must enforce authorization on every
    protected endpoint.

## 3. Current status and assumptions

### Completed on the backend

-   User module
-   Authentication
-   Authorization / roles
-   `POST /auth/login` returns an access token
-   `GET /auth/me` works when called with a valid token in Swagger

### Existing frontend

The Phase 1 frontend already has:

-   `index.html`
-   `css/style.css`
-   `js/app.js`

Preserve these files and their existing product-listing behavior.

### Still to confirm before API integration

Inspect the actual FastAPI implementation or `/docs` and record:

-   The exact request format for `POST /auth/login` (JSON body or form
    data)
-   The exact request format for `POST /auth/register`
-   The exact successful response from `GET /auth/me`
-   The expected token header format (usually
    `Authorization: Bearer <token>`)
-   Whether the backend supports cookie-based authentication or only
    bearer tokens

Do not assume these details; the frontend must match the real API
contract.

## 4. Planned frontend structure

``` text
ecommerce/
├── backend/
│   └── app/
│       ├── auth/
│       ├── users/
│       └── products/
│
└── frontend/
    ├── index.html                 # Existing Phase 1 store page
    │
    ├── pages/
    │   ├── login.html             # New: login page
    │   └── register.html          # New: registration page
    │
    ├── components/                # Add reusable UI only when needed
    │
    ├── css/
    │   ├── style.css              # Existing product-store styles
    │   └── auth.css               # New: login and registration styles
    │
    └── js/
        ├── app.js                 # Existing product-store behavior
        ├── auth.js                # Shared authentication helpers
        ├── login.js               # Login form behavior
        └── register.js            # Registration form behavior
```

Create only the files needed for the current task. `components/` can
remain empty until a reusable component is actually needed.

## 5. Responsibility of each file

### `pages/login.html`

Contains the login form and the page elements required by `login.js`,
such as:

-   Email or username field, depending on the actual API contract
-   Password field
-   Submit button
-   Area for validation and API error messages
-   Link to the registration page

It should link to `../css/auth.css` and load `../js/login.js`.

### `pages/register.html`

Contains the customer-registration form, based on the fields accepted by
the existing registration endpoint.

Likely fields include name, email, and password, but confirm these
against the backend schema. Public registration must not let the client
choose an admin role.

It should link to `../css/auth.css` and load `../js/register.js`.

### `css/auth.css`

Contains styling shared by login and registration pages:

-   Form layout and spacing
-   Inputs and buttons
-   Error and success messages
-   Responsive behavior
-   Focus and disabled states

Avoid copying product-page styles into this file.

### `js/login.js`

Responsible for the login page only:

1.  Find the login form in the DOM.
2.  Listen for the form's `submit` event.
3.  Prevent the browser's default form submission.
4.  Read and validate the input values.
5.  Send the login request using `fetch()`, matching the actual backend
    contract.
6.  Handle unsuccessful HTTP responses and network errors.
7.  Process the returned access token according to the agreed
    token-storage strategy.
8.  Call `/auth/me` with the token to obtain the current user's details,
    if required by the response contract.
9.  Redirect or update the interface after successful login.

Keep API request logic understandable while learning. Shared helpers can
be extracted into `auth.js` once the basic flow works.

### `js/register.js`

Responsible for registration:

1.  Listen for registration form submission.
2.  Read and validate form values.
3.  Send the request in the format expected by `POST /auth/register`.
4.  Display validation, duplicate-email, server, and network errors
    clearly.
5.  On success, direct the user to the login page unless the existing
    application intentionally supports automatic login.

Do not send a `role` field from the public registration form.

### `js/auth.js`

Will contain shared authentication helpers as they become necessary, for
example:

-   API base URL or shared API configuration
-   Reading the current authentication state
-   Requesting the current user from `/auth/me`
-   Logout behavior
-   Shared handling for authentication errors

Avoid building a large authentication framework. Add only helpers used
by more than one page or needed to keep the implementation clear.

### `index.html` and `js/app.js`

Keep the existing product-store behavior intact. Once login works,
integrate the relevant UI:

-   Show Login and Register links when signed out.
-   Show the appropriate signed-in navigation when authenticated.
-   Show admin navigation only when the current user's role is `admin`.
-   Keep product browsing, search, filters, and pagination working.

The frontend may hide or show controls based on role, but backend
authorization remains mandatory.

## 6. Authentication flow

### Login

``` text
User opens pages/login.html
        |
        v
Enters credentials and submits form
        |
        v
login.js sends POST /auth/login
        |
        v
FastAPI validates credentials
        |
        v
Backend returns access token
        |
        v
Frontend handles token according to the chosen strategy
        |
        v
Frontend requests GET /auth/me with the token
        |
        v
Frontend learns the authenticated user's details and role
        |
        v
Redirect to the store or update navigation
```

The request body and response property names must be taken from the
actual backend implementation.

### Registration

``` text
User opens pages/register.html
        |
        v
Enters registration details
        |
        v
register.js sends POST /auth/register
        |
        v
FastAPI validates and creates a customer account
        |
        v
Frontend displays success and links to login
```

### Protected request

For a protected API request using bearer-token authentication:

``` http
Authorization: Bearer <access_token>
```

Use this header only if it matches the backend's authentication
implementation.

## 7. Token handling and security decisions

The backend currently returns an access token. Before implementing
storage, choose a strategy deliberately.

-   **Avoid putting tokens in URLs.**
-   **Do not commit tokens, passwords, or secrets to Git.**
-   `localStorage` is simple for learning but JavaScript can read its
    contents; an XSS vulnerability can expose stored tokens.
-   `sessionStorage` is also accessible to JavaScript and is not an
    XSS-proof solution.
-   An `HttpOnly`, `Secure`, appropriately configured cookie can reduce
    JavaScript access to the token, but requires backend support and
    appropriate CSRF protections.
-   Do not claim the frontend is secure merely because admin buttons are
    hidden.
-   Treat the backend's authorization checks as the real security
    boundary.
-   On logout, clear client-side authentication state and any token
    stored by the chosen strategy. If the backend uses stateless JWTs
    without revocation, client-side removal does not invalidate a copied
    token.

**Decision:** token storage is not finalized in this document. Confirm
the backend's capabilities and choose the strategy before writing the
final login integration.

## 8. API integration checklist

Record the real values from the backend before coding:

  -----------------------------------------------------------------------
  Item                                Confirmed value
  ----------------------------------- -----------------------------------
  API base URL                        Local development: usually
                                      `http://localhost:8000`

  Login endpoint                      `POST /auth/login`

  Login request content type          To confirm from `/docs` or
                                      `app/auth/routers.py`

  Login request fields                To confirm from the backend schema

  Token response field                Confirmed to return an access
                                      token; exact property name to
                                      verify

  Current-user endpoint               `GET /auth/me`

  Token header                        Confirm expected bearer-token
                                      format

  Registration endpoint               `POST /auth/register`

  Registration request fields         To confirm from the backend schema

  CORS                                Ensure FastAPI permits the
                                      frontend's local origin
  -----------------------------------------------------------------------

Do not copy the example API base URL blindly if your backend runs on a
different host or port.

## 9. Development sequence

Complete each task before starting the next.

### Task 1 --- Prepare the structure

-   [ ] Create `pages/login.html`
-   [ ] Create `pages/register.html`
-   [ ] Create `css/auth.css`
-   [ ] Create `js/auth.js`
-   [ ] Create `js/login.js`
-   [ ] Create `js/register.js`
-   [ ] Keep the existing Phase 1 files unchanged for now

### Task 2 --- Build the login page UI

-   [ ] Create semantic HTML for the login form
-   [ ] Add labels and appropriate input types
-   [ ] Add a submit button and message area
-   [ ] Link the stylesheet and JavaScript file
-   [ ] Verify the page opens and looks correct before API integration

### Task 3 --- Integrate login

-   [ ] Confirm the exact login request schema and response
-   [ ] Add form submission handling
-   [ ] Send the request with `fetch()`
-   [ ] Handle HTTP errors and network errors
-   [ ] Implement the agreed token-handling strategy
-   [ ] Request `/auth/me` using the token
-   [ ] Test valid and invalid credentials

### Task 4 --- Build and integrate registration

-   [ ] Build the registration form
-   [ ] Confirm the backend request schema
-   [ ] Submit registration using `fetch()`
-   [ ] Display validation and duplicate-email errors
-   [ ] Ensure public registration cannot assign `admin`
-   [ ] Test registration and then log in with the new account

### Task 5 --- Authentication-aware navigation

-   [ ] Show Login/Register when signed out
-   [ ] Show signed-in navigation when authenticated
-   [ ] Show admin links only for an admin user
-   [ ] Implement logout
-   [ ] Handle missing, invalid, or expired tokens
-   [ ] Confirm that backend endpoints still reject unauthorized
    requests

### Task 6 --- Regression testing

-   [ ] Existing product listing still works
-   [ ] Search, category filtering, and pagination still work
-   [ ] Login and registration work
-   [ ] Customer cannot perform admin operations
-   [ ] Admin can perform authorized product operations
-   [ ] Browser console and network tab show no unhandled errors

## 10. How to run and debug

-   Run FastAPI using the command already used in this project.
-   Open the frontend through a local development server rather than
    relying on `file://` URLs, especially when using JavaScript modules
    or cross-origin requests.
-   Use browser DevTools:
    -   **Console:** JavaScript errors
    -   **Network:** request URL, method, payload, status code, and
        response
    -   **Application/Storage:** inspect the selected client-side
        storage strategy
-   If the browser blocks requests, check the FastAPI CORS configuration
    and the frontend's origin.
-   Never put a production secret in frontend JavaScript. Anything
    shipped to the browser is visible to users.

## 11. Definition of done for this authentication frontend

This part is complete when:

-   A visitor can open the login and registration pages.
-   A visitor can register a customer account.
-   A valid user can log in through the frontend.
-   Invalid credentials produce a clear error.
-   The frontend can retrieve the current user's details through
    `/auth/me`.
-   The interface can distinguish customers from admins.
-   Logout clears the frontend's authentication state.
-   Backend authorization remains effective even if someone manually
    calls an admin endpoint.
-   Existing Phase 1 product browsing continues to work.

## 12. Working agreement for the next steps

Proceed one task at a time. Do not implement all files at once.

The immediate next task is to inspect the actual `POST /auth/login`,
`POST /auth/register`, and `GET /auth/me` contracts in Swagger or in the
backend files. Then build the static login form before connecting it to
the API.

Keep this document updated whenever the agreed structure or
implementation decisions change.
