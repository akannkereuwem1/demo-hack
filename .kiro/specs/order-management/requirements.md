# Requirements Document

## Introduction

Order Management is the core transactional feature of AgroNet. It allows buyers to place orders against farmer product listings, and farmers to accept or decline those orders. Once confirmed, the order progresses through a strict state machine (pending → confirmed → paid → completed, or pending → declined) enforced entirely in the service layer. All endpoints are JSON-only, JWT-authenticated, and role-restricted per the mobile backend API contract.

## Glossary

- **Order_Service**: The service layer module (`orders/services.py`) that contains all order business logic.
- **Order_API**: The DRF view layer (`orders/views.py`) that handles HTTP requests and delegates to Order_Service.
- **Order**: A database record representing a buyer's request to purchase a quantity of a product from a farmer.
- **Buyer**: An authenticated User with `role = 'buyer'`.
- **Farmer**: An authenticated User with `role = 'farmer'`.
- **State_Machine**: The enforced sequence of order statuses: `pending → confirmed → paid → completed`, or `pending → declined`.
- **Transition**: A change from one order status to the next valid status in the State_Machine.
- **Product**: An agricultural listing created by a Farmer, referenced by an Order.
- **OrderItem**: A line item within an Order specifying a Product, quantity, and agreed unit price.

---

## Requirements

### Requirement 1: Order Model

**User Story:** As a developer, I want a well-defined Order data model, so that all order data is stored consistently and can be queried reliably.

#### Acceptance Criteria

1. THE Order SHALL use a UUID primary key.
2. THE Order SHALL store a foreign key reference to the Buyer (User) who created it, indexed for query performance.
3. THE Order SHALL store a foreign key reference to the Farmer (User) who owns the listed product, indexed for query performance.
4. THE Order SHALL store a `status` field constrained to the values: `pending`, `confirmed`, `paid`, `completed`, `declined`.
5. THE Order SHALL default `status` to `pending` on creation.
6. THE Order SHALL store `created_at` and `updated_at` timestamps, set automatically.
7. THE OrderItem SHALL store a foreign key to Order, a foreign key to Product, a `quantity` (positive decimal), and a `unit_price` (positive decimal) snapshot at time of order creation.
8. THE Order SHALL store a `total_price` decimal field computed as the sum of all OrderItem `quantity × unit_price` values.
9. THE Order SHALL store an optional `note` text field for buyer remarks, with a maximum length of 500 characters.

---

### Requirement 2: Order Creation

**User Story:** As a buyer, I want to place an order for a product, so that I can request to purchase agricultural produce from a farmer.

#### Acceptance Criteria

1. WHEN a Buyer submits a POST request to `/api/orders/` with a valid product ID and quantity, THE Order_Service SHALL create an Order with `status = pending`.
2. THE Order_API SHALL reject order creation requests from users with `role = 'farmer'` with HTTP 403.
3. THE Order_API SHALL reject unauthenticated order creation requests with HTTP 401.
4. WHEN the referenced Product does not exist, THE Order_API SHALL return HTTP 404.
5. WHEN the referenced Product has `is_available = False`, THE Order_Service SHALL reject the order with a descriptive error and HTTP 400.
6. WHEN a valid order is created, THE Order_Service SHALL set `farmer` on the Order to the `farmer` field of the referenced Product.
7. WHEN a valid order is created, THE Order_Service SHALL snapshot the Product's `price_per_unit` as `unit_price` on the OrderItem.
8. WHEN a valid order is created, THE Order_Service SHALL compute and store `total_price` as `quantity × unit_price`.
9. WHEN the submitted `quantity` is less than or equal to zero, THE Order_API SHALL return HTTP 400 with a descriptive validation error.

---

### Requirement 3: Order Listing

**User Story:** As a user, I want to list my orders, so that I can track the status of purchases or sales.

#### Acceptance Criteria

1. WHEN a Buyer sends GET `/api/orders/`, THE Order_API SHALL return only orders where `buyer = request.user`.
2. WHEN a Farmer sends GET `/api/orders/`, THE Order_API SHALL return only orders where `farmer = request.user`.
3. THE Order_API SHALL return order lists in descending `created_at` order.
4. THE Order_API SHALL paginate order list responses using the project default page size of 20.
5. THE Order_API SHALL support filtering the order list by `status` query parameter.

---

### Requirement 4: Order Detail

**User Story:** As a user, I want to retrieve a single order by ID, so that I can view its full details.

#### Acceptance Criteria

1. WHEN an authenticated user sends GET `/api/orders/{id}/`, THE Order_API SHALL return the full order detail if the requesting user is the Buyer or the Farmer on that order.
2. WHEN the requesting user is neither the Buyer nor the Farmer on the order, THE Order_API SHALL return HTTP 403.
3. WHEN the order ID does not exist, THE Order_API SHALL return HTTP 404.

---

### Requirement 5: Order State Machine — Farmer Actions

**User Story:** As a farmer, I want to confirm or decline a pending order, so that I can control which orders I fulfil.

#### Acceptance Criteria

1. WHEN a Farmer sends PATCH `/api/orders/{id}/confirm/` and the order `status = pending`, THE Order_Service SHALL transition the order to `status = confirmed`.
2. WHEN a Farmer sends PATCH `/api/orders/{id}/decline/` and the order `status = pending`, THE Order_Service SHALL transition the order to `status = declined`.
3. WHEN the requesting user is not the Farmer on the order, THE Order_API SHALL return HTTP 403 for confirm and decline actions.
4. IF the order `status` is not `pending` when a confirm or decline action is requested, THEN THE Order_Service SHALL reject the transition with HTTP 400 and a descriptive error message.
5. WHEN a Buyer attempts to call the confirm or decline endpoints, THE Order_API SHALL return HTTP 403.

---

### Requirement 6: Order State Machine — Payment Transition

**User Story:** As a system, I want the order to advance to `paid` after a successful payment, so that the order lifecycle reflects payment reality.

#### Acceptance Criteria

1. WHEN the Payment system notifies Order_Service of a successful payment for an order with `status = confirmed`, THE Order_Service SHALL transition the order to `status = paid`.
2. IF the order `status` is not `confirmed` when a payment transition is requested, THEN THE Order_Service SHALL reject the transition with a descriptive error.
3. THE Order_Service SHALL expose a `mark_as_paid(order_id)` function callable by the payments module.

---

### Requirement 7: Order State Machine — Completion

**User Story:** As a farmer, I want to mark a paid order as completed, so that I can confirm fulfilment of the order.

#### Acceptance Criteria

1. WHEN a Farmer sends PATCH `/api/orders/{id}/complete/` and the order `status = paid`, THE Order_Service SHALL transition the order to `status = completed`.
2. WHEN the requesting user is not the Farmer on the order, THE Order_API SHALL return HTTP 403 for the complete action.
3. IF the order `status` is not `paid` when a complete action is requested, THEN THE Order_Service SHALL reject the transition with HTTP 400 and a descriptive error message.

---

### Requirement 8: State Machine Integrity

**User Story:** As a developer, I want the state machine to be strictly enforced, so that no order can skip or reverse states.

#### Acceptance Criteria

1. THE Order_Service SHALL define the complete set of valid transitions as: `{pending: [confirmed, declined], confirmed: [paid], paid: [completed]}`.
2. IF a requested transition is not in the valid transitions map for the current status, THEN THE Order_Service SHALL raise an error without modifying the order.
3. THE Order_Service SHALL enforce state transitions atomically using database transactions to prevent race conditions.
4. FOR ALL orders, THE Order_Service SHALL ensure that `status` is always one of the five defined values: `pending`, `confirmed`, `paid`, `completed`, `declined`.

---

### Requirement 9: Order Serialization

**User Story:** As a developer, I want consistent, well-structured JSON responses for orders, so that the mobile client can reliably parse order data.

#### Acceptance Criteria

1. THE Order_API SHALL serialize all order responses to JSON including: `id`, `buyer`, `farmer`, `status`, `total_price`, `note`, `created_at`, `updated_at`, and a nested list of `items`.
2. THE Order_API SHALL serialize each item in `items` with: `product_id`, `product_title`, `quantity`, `unit_price`.
3. THE Order_API SHALL mark `id`, `buyer`, `farmer`, `total_price`, `status`, `created_at`, `updated_at` as read-only in the serializer.
4. WHEN an invalid payload is submitted, THE Order_API SHALL return HTTP 400 with field-level validation errors in JSON format.

---

### Requirement 10: Order Permissions

**User Story:** As a system, I want role-based access control on all order endpoints, so that buyers and farmers can only perform their permitted actions.

#### Acceptance Criteria

1. THE Order_API SHALL require JWT authentication on all order endpoints.
2. THE Order_API SHALL restrict order creation (POST `/api/orders/`) to users with `role = 'buyer'`.
3. THE Order_API SHALL restrict confirm, decline, and complete actions to the Farmer who owns the specific order.
4. THE Order_API SHALL allow both the Buyer and the Farmer of an order to read that order's detail.
5. WHEN a request is made without a valid JWT token, THE Order_API SHALL return HTTP 401.
6. WHEN a request is made with a valid JWT token but insufficient role or ownership, THE Order_API SHALL return HTTP 403.

---

### Requirement 11: Order Tests

**User Story:** As a developer, I want comprehensive tests for the order feature, so that regressions are caught and the state machine is verified.

#### Acceptance Criteria

1. THE test suite SHALL include integration tests for order creation covering: success, 401 unauthenticated, 403 farmer-blocked, 404 product-not-found, 400 unavailable product, 400 invalid quantity.
2. THE test suite SHALL include integration tests for the state machine covering all valid transitions: pending→confirmed, pending→declined, confirmed→paid, paid→completed.
3. THE test suite SHALL include integration tests for all invalid state transitions, verifying HTTP 400 is returned.
4. THE test suite SHALL include integration tests for permission enforcement on confirm, decline, and complete endpoints.
5. THE test suite SHALL include integration tests for order listing, verifying buyers see only their orders and farmers see only their orders.
6. THE test suite SHALL include a test verifying that `total_price` is correctly computed as `quantity × unit_price` on order creation.
