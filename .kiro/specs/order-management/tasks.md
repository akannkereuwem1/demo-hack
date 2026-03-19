# Implementation Plan: Order Management

## Overview

Implement the order management feature for AgroNet following the three-layer architecture (views → services → models). Tasks are ordered to build the data layer first, then business logic, then the API surface, and finally wire everything together with tests.

## Tasks

- [x] 1. Implement Order and OrderItem models
  - Define `OrderStatus` choices and `Order` model with UUID PK, buyer/farmer FKs, status, total_price, note, timestamps in `backend/apps/orders/models.py`
  - Define `OrderItem` model with FK to Order and Product, quantity and unit_price decimal fields with MinValueValidator
  - Set `db_table = 'orders'` and `db_table = 'order_items'`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [x] 2. Create and apply database migration
  - Run `makemigrations orders` to generate the migration file
  - Verify migration file is correct before applying
  - _Requirements: 1.1, 1.7_

- [x] 3. Implement order serializers
  - [x] 3.1 Write `OrderItemSerializer` (read-only: product_id, product_title, quantity, unit_price) in `backend/apps/orders/serializers.py`
    - _Requirements: 9.2_
  - [x] 3.2 Write `OrderSerializer` with nested `items`; read-only fields: id, buyer, farmer, total_price, status, created_at, updated_at
    - _Requirements: 9.1, 9.3_
  - [x] 3.3 Write `OrderCreateSerializer` accepting product_id (UUIDField), quantity (DecimalField with min_value=0.01), note (optional CharField max_length=500)
    - _Requirements: 9.4, 1.9, 2.9_

- [x] 4. Implement order permissions
  - Write `IsOrderParticipant` permission class in `backend/apps/orders/permissions.py`: `has_object_permission` returns True if user is order.buyer or order.farmer
  - Write `IsOrderFarmer` permission class: `has_object_permission` returns True if user is order.farmer
  - _Requirements: 10.3, 10.4_

- [x] 5. Implement the service layer
  - [x] 5.1 Create `backend/apps/orders/services.py` with `VALID_TRANSITIONS` constant and `OrderTransitionError` exception class
    - _Requirements: 8.1, 8.2_
  - [x] 5.2 Implement `create_order(buyer, product_id, quantity, note)` — fetch product (raise 404 if missing), validate is_available, snapshot unit_price, compute total_price, create Order + OrderItem atomically
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.7, 2.8_
  - [ ]* 5.3 Write property test for total price computation
    - **Property 1: Total price computation**
    - **Validates: Requirements 2.7, 2.8**
    - Use `hypothesis` with `st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999'), places=2)` for qty and price
    - Tag: `# Feature: order-management, Property 1: total_price == quantity * unit_price`
  - [ ]* 5.4 Write property test for unavailable product rejection
    - **Property 6: Unavailable product rejection**
    - **Validates: Requirements 2.5**
    - Tag: `# Feature: order-management, Property 6: unavailable product order rejected`
  - [ ]* 5.5 Write property test for non-positive quantity rejection
    - **Property 7: Non-positive quantity rejection**
    - **Validates: Requirements 2.9**
    - Use `st.decimals(max_value=Decimal('0'))`
    - Tag: `# Feature: order-management, Property 7: non-positive quantity rejected`
  - [x] 5.6 Implement `transition_order(order, target_status, actor)` — validate actor is order.farmer, look up VALID_TRANSITIONS, raise `OrderTransitionError` if invalid, update status atomically with `select_for_update`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 7.1, 7.3, 8.1, 8.2, 8.3_
  - [ ]* 5.7 Write property test for invalid state transitions
    - **Property 2: Only valid state transitions are accepted**
    - **Validates: Requirements 8.1, 8.2**
    - Use `st.sampled_from(OrderStatus)` × `st.sampled_from(OrderStatus)` to generate random (current, target) pairs
    - Tag: `# Feature: order-management, Property 2: invalid transitions rejected`
  - [ ]* 5.8 Write property test for sequential state path
    - **Property 3: State machine is strictly sequential — no skipping**
    - **Validates: Requirements 8.1, 8.4**
    - Tag: `# Feature: order-management, Property 3: status sequence is valid path`
  - [x] 5.9 Implement `mark_as_paid(order_id)` — fetch order, validate status == confirmed, transition to paid atomically
    - _Requirements: 6.1, 6.2, 6.3_
  - [ ]* 5.10 Write property test for mark_as_paid on non-confirmed orders
    - **Property 10: mark_as_paid only transitions confirmed orders**
    - **Validates: Requirements 6.2**
    - Use `st.sampled_from([pending, paid, completed, declined])`
    - Tag: `# Feature: order-management, Property 10: mark_as_paid rejects non-confirmed`

- [x] 6. Checkpoint — Ensure service layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement API views and URL routing
  - [x] 7.1 Rewrite `OrderListView` in `backend/apps/orders/views.py`:
    - GET: filter queryset by buyer or farmer based on role, order by -created_at, support `status` filter, paginate
    - POST: use `IsBuyer` permission, call `create_order`, return 201 with `OrderSerializer`
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 10.1, 10.2_
  - [ ]* 7.2 Write property test for buyer listing isolation
    - **Property 4: Buyer isolation in order listing**
    - **Validates: Requirements 3.1**
    - Use `st.integers(min_value=1, max_value=10)` for number of buyers/orders
    - Tag: `# Feature: order-management, Property 4: buyer sees only own orders`
  - [ ]* 7.3 Write property test for farmer listing isolation
    - **Property 5: Farmer isolation in order listing**
    - **Validates: Requirements 3.2**
    - Tag: `# Feature: order-management, Property 5: farmer sees only own orders`
  - [x] 7.4 Implement `OrderDetailView`: GET with `IsOrderParticipant` object permission, return full `OrderSerializer`
    - _Requirements: 4.1, 4.2, 4.3, 10.4_
  - [x] 7.5 Implement `OrderConfirmView`, `OrderDeclineView`, `OrderCompleteView` as PATCH views with `IsOrderFarmer` permission, delegating to `transition_order`; catch `OrderTransitionError` and return HTTP 400
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.2, 7.3, 10.3_
  - [ ]* 7.6 Write property test for role-based creation restriction
    - **Property 8: Role-based access — creation restricted to buyers**
    - **Validates: Requirements 2.2, 10.2**
    - Tag: `# Feature: order-management, Property 8: farmer cannot create order`
  - [ ]* 7.7 Write property test for ownership enforcement on state transitions
    - **Property 9: Ownership enforcement on state transitions**
    - **Validates: Requirements 5.3, 5.5, 7.2, 10.3**
    - Tag: `# Feature: order-management, Property 9: non-farmer cannot transition`
  - [x] 7.8 Update `backend/apps/orders/urls.py` to add routes for confirm, decline, and complete views; change `<int:pk>` to `<uuid:pk>`
    - _Requirements: 5.1, 5.2, 7.1_

- [x] 8. Register Order model in admin
  - Register `Order` and `OrderItem` in `backend/apps/orders/admin.py`
  - _Requirements: 1.1_

- [x] 9. Write integration tests
  - [x] 9.1 Write order creation integration tests in `backend/tests/test_order_api.py`: success (201), 401 unauthenticated, 403 farmer blocked, 404 product not found, 400 unavailable product, 400 invalid quantity
    - _Requirements: 11.1, 2.1, 2.2, 2.3, 2.4, 2.5, 2.9_
  - [x] 9.2 Write state machine integration tests: pending→confirmed, pending→declined, confirmed→paid (via mark_as_paid), paid→completed
    - _Requirements: 11.2, 5.1, 5.2, 6.1, 7.1_
  - [x] 9.3 Write invalid transition integration tests: verify all invalid combos return HTTP 400
    - _Requirements: 11.3, 8.2_
  - [x] 9.4 Write permission enforcement integration tests: non-farmer blocked from confirm/decline/complete, non-owner blocked from detail
    - _Requirements: 11.4, 10.3, 10.4_
  - [x] 9.5 Write order listing isolation integration tests: buyer sees only their orders, farmer sees only their orders
    - _Requirements: 11.5, 3.1, 3.2_
  - [x] 9.6 Write total_price computation integration test: verify total_price == quantity × unit_price on creation
    - _Requirements: 11.6, 2.7, 2.8_

- [x] 10. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests use `hypothesis[django]` — ensure it is installed before running
- Each property test must run a minimum of 100 iterations (Hypothesis default `max_examples=100`)
- All tests go in `backend/tests/` per AGENTS.md
- State transitions must use `select_for_update` for atomicity (Requirement 8.3)
- UUID primary keys are required on all models (Requirement 1.1, AGENTS.md §7)
