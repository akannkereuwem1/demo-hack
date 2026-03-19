---
inclusion: fileMatch
fileMatchPattern: ['backend/apps/orders/**', 'backend/tests/test_order*']
---

# Order Management — Steering Guide

## Domain Overview

Order Management is the core transactional layer of AgroNet. Buyers place orders against farmer product listings; farmers accept or decline; payments advance the order to `paid`; farmers mark fulfilment as `completed`.

All order endpoints are JSON-only, JWT-authenticated, and role-restricted per the mobile backend API contract.

---

## State Machine (Strict — Never Bypass)

```
pending → confirmed → paid → completed
pending → declined
```

Valid transitions map (source of truth in `orders/services.py`):

```python
VALID_TRANSITIONS = {
    "pending":   ["confirmed", "declined"],
    "confirmed": ["paid"],
    "paid":      ["completed"],
}
```

- Any transition not in this map **must be rejected** with HTTP 400 and a descriptive error.
- Transitions must be executed **atomically** using `select_for_update()` inside a `transaction.atomic()` block.
- `mark_as_paid(order_id)` is the only entry point for the `confirmed → paid` transition; it is called by the payments module, not by a user-facing endpoint.

---

## Architecture (Three-Layer — Strictly Enforced)

```
orders/views.py       ← HTTP only: validate input, check permissions, call service, return Response
orders/services.py    ← All business logic: state machine, price computation, atomic writes
orders/models.py      ← Data only: no business logic
```

- Views **must not** contain business logic.
- Models **must not** contain business logic.
- Service functions are the single source of truth for order operations.

### Public Service Interface

```python
def create_order(buyer: User, product_id: UUID, quantity: Decimal, note: str = "") -> Order: ...
def transition_order(order: Order, target_status: str, actor: User) -> Order: ...
def mark_as_paid(order_id: UUID) -> Order: ...
```

---

## Endpoints & Permissions

| Method | URL | Permission Class |
|--------|-----|-----------------|
| GET | `/api/orders/` | `IsAuthenticated` |
| POST | `/api/orders/` | `IsBuyer` |
| GET | `/api/orders/{id}/` | `IsOrderParticipant` |
| PATCH | `/api/orders/{id}/confirm/` | `IsOrderFarmer` |
| PATCH | `/api/orders/{id}/decline/` | `IsOrderFarmer` |
| PATCH | `/api/orders/{id}/complete/` | `IsOrderFarmer` |

- `IsOrderParticipant`: user is `order.buyer` **or** `order.farmer`
- `IsOrderFarmer`: user is `order.farmer`
- Unauthenticated → 401. Wrong role/ownership → 403.

---

## Data Models

### `Order` (`db_table = 'orders'`)

| Field | Notes |
|-------|-------|
| `id` | UUID PK |
| `buyer` | FK(User), `db_index=True` |
| `farmer` | FK(User), `db_index=True` |
| `status` | choices: `pending/confirmed/paid/completed/declined`, default `pending` |
| `total_price` | `DecimalField(12,2)` — computed at creation, stored |
| `note` | optional, `max_length=500` |
| `created_at` / `updated_at` | auto timestamps |

### `OrderItem` (`db_table = 'order_items'`)

| Field | Notes |
|-------|-------|
| `id` | UUID PK |
| `order` | FK(Order), `db_index=True` |
| `product` | FK(Product), `on_delete=PROTECT`, `db_index=True` |
| `quantity` | `DecimalField(12,2)`, `MinValueValidator(0.01)` |
| `unit_price` | `DecimalField(12,2)` — **snapshot** of `product.price_per_unit` at creation time |

`total_price = sum(item.quantity * item.unit_price for item in order.items.all())` — computed and stored by the service on creation.

---

## Key Business Rules

1. Only users with `role = 'buyer'` may create orders. Farmers get HTTP 403.
2. `farmer` on the Order is set from `product.farmer` — never from the request payload.
3. `unit_price` is snapshotted from `product.price_per_unit` at creation — never updated later.
4. Orders referencing a product with `is_available = False` must be rejected with HTTP 400.
5. `quantity ≤ 0` must be rejected with HTTP 400.
6. Order listing is scoped: buyers see only their orders; farmers see only their orders. Ordered by `-created_at`, paginated at 20.

---

## Serializers

- `OrderCreateSerializer` — write: accepts `product_id`, `quantity`, `note`
- `OrderSerializer` — read: full order with nested `items`; read-only fields: `id`, `buyer`, `farmer`, `total_price`, `status`, `created_at`, `updated_at`
- `OrderItemSerializer` — nested read-only: `product_id`, `product_title`, `quantity`, `unit_price`

---

## Error Handling

All errors use the project's `custom_exception_handler` envelope:

```json
{ "success": false, "error": { "status_code": 400, "message": "...", "details": {} } }
```

Service layer raises `ValidationError` or `OrderTransitionError` (subclass of `ValueError`) for invalid transitions. Views catch these and return the appropriate DRF `Response`.

---

## Testing Requirements

Tests live in `backend/tests/`. Both integration tests and property-based tests (using `hypothesis`) are required.

**Integration tests must cover:**
- Order creation: success, 401, 403 (farmer), 404 (product), 400 (unavailable), 400 (bad quantity)
- All valid state transitions: `pending→confirmed`, `pending→declined`, `confirmed→paid`, `paid→completed`
- All invalid state transitions → HTTP 400
- Permission enforcement on confirm/decline/complete
- Listing isolation: buyer sees only their orders; farmer sees only theirs
- `total_price` = `quantity × unit_price` on creation

**Property-based tests must cover (min 100 iterations each):**
- `total_price` always equals `quantity × unit_price`
- Invalid transitions always rejected without mutating status
- Status sequence is always a valid path prefix
- Buyer/farmer listing isolation holds across arbitrary numbers of users and orders
- Unavailable product always rejected
- Non-positive quantity always rejected
- Farmer role always blocked from creation
- Non-owner always blocked from transitions
- `mark_as_paid` always rejects non-confirmed orders

Tag each property test with:
```python
# Feature: order-management, Property {N}: {property_text}
```
