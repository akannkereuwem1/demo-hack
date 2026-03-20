# Payment Processing — Technical Reference

## What We Built

A complete payment processing feature for AgroNet using **Interswitch** as the payment gateway. Buyers can pay for confirmed orders, verify payment outcomes, and Interswitch can notify the system of payment results via webhooks.

---

## Architecture

The feature follows AgroNet's strict three-layer pattern:

```
HTTP Request
    ↓
views.py          ← Controller layer: parses request, enforces auth, returns response
    ↓
services.py       ← Service layer: all business logic lives here
    ↓
interswitch.py    ← External client: all Interswitch HTTP calls isolated here
    ↓
models.py         ← Data layer: Payment model persisted to PostgreSQL
```

**Rule:** Views never contain business logic. Services never return HTTP responses. The Interswitch client never touches the database.

---

## Files Created / Modified

| File | Purpose |
|------|---------|
| `backend/apps/payments/models.py` | Payment model + PaymentStatus choices |
| `backend/apps/payments/migrations/0001_initial.py` | DB migration for Payment table |
| `backend/apps/payments/interswitch.py` | Interswitch HTTP client (initiate, verify, webhook sig) |
| `backend/apps/payments/services.py` | Business logic: initiate_payment, verify_payment, handle_webhook |
| `backend/apps/payments/serializers.py` | Input/output serializers for the 3 endpoints |
| `backend/apps/payments/permissions.py` | Re-exports IsBuyer permission |
| `backend/apps/payments/views.py` | 3 API views wired to services |
| `backend/apps/payments/urls.py` | URL routing for initiate/, verify/, webhook/ |
| `backend/tests/test_payments.py` | 40 tests: 13 property-based + 27 integration |

---

## The Payment Model

```python
class Payment(models.Model):
    id                    # UUID primary key
    order                 # OneToOneField → Order (one payment per order)
    transaction_reference # Unique string, format: AGN-<UUID_HEX>
    amount                # DecimalField — copied from order.total_price at initiation
    status                # pending | successful | failed
    provider_response     # JSONField — raw Interswitch response stored for audit
    created_at / updated_at
```

**Key constraint:** One order can only have one Payment record (OneToOneField).

---

## Payment Status State Machine

```
[Order: confirmed]
        ↓
  POST /initiate/
        ↓
  Payment: pending
        ↓
  POST /verify/  OR  POST /webhook/
        ↓                ↓
  Payment: successful   Payment: failed
        ↓
  Order: paid
```

---

## The Three Endpoints

### 1. POST /api/payments/initiate/

**Auth:** JWT Bearer token, buyer role only

**What it does:**
1. Validates the order exists and belongs to the authenticated buyer
2. Rejects if order status is not `confirmed`
3. Rejects if a pending/successful payment already exists for this order
4. Generates a unique `transaction_reference` (format: `AGN-<UUID_HEX>`)
5. Calls Interswitch `POST /api/v2/purchases`
6. Creates a `Payment` record with `status=pending`
7. Returns 201 with the payment data + Interswitch checkout params

**Request body:**
```json
{ "order_id": "uuid-of-confirmed-order" }
```

**Success response (201):**
```json
{
  "transaction_reference": "AGN-ABC123...",
  "amount": "5000.00",
  "status": "pending",
  "order_id": "uuid-of-order",
  "checkout_params": { "checkoutUrl": "https://pay.interswitch.com/..." }
}
```

---

### 2. POST /api/payments/verify/

**Auth:** JWT Bearer token, buyer role only

**What it does:**
1. Looks up the Payment by `transaction_reference`
2. Verifies the authenticated buyer owns the order
3. If already `successful` — returns immediately (idempotent, no Interswitch call)
4. Calls Interswitch `GET /api/v2/purchases/{reference}`
5. Inside `transaction.atomic()`: updates Payment status + calls `order_mark_as_paid()` on success
6. Always persists the raw Interswitch response to `provider_response`
7. Returns 200 on success, 400 if Interswitch says the transaction failed

**Request body:**
```json
{ "transaction_reference": "AGN-ABC123..." }
```

**Success response (200):**
```json
{
  "transaction_reference": "AGN-ABC123...",
  "amount": "5000.00",
  "status": "successful",
  "order_id": "uuid-of-order",
  "checkout_params": { "responseCode": "00", ... }
}
```

---

### 3. POST /api/payments/webhook/

**Auth:** None (Interswitch calls this directly). Validated via HMAC-SHA512 signature.

**What it does:**
1. Reads raw request body bytes
2. Computes HMAC-SHA512 of body using `INTERSWITCH_CLIENT_SECRET`
3. Compares to `X-Interswitch-Signature` header — returns 400 if invalid
4. Looks up Payment by `transactionReference` in payload — silently returns 200 if unknown
5. Skips if Payment is already terminal (idempotent)
6. Inside `transaction.atomic()`: updates Payment status + calls `order_mark_as_paid()` on success
7. Always returns 200 (prevents Interswitch retry storms)

---

## Interswitch Client (`interswitch.py`)

Three functions, all credentials from env vars only:

```python
initiate_transaction(order_id, amount, reference) -> dict
    # POST {INTERSWITCH_BASE_URL}/api/v2/purchases
    # Raises InterswitchError on non-2xx

verify_transaction(reference) -> dict
    # GET {INTERSWITCH_BASE_URL}/api/v2/purchases/{reference}
    # Raises InterswitchError on non-2xx

validate_webhook_signature(payload: bytes, signature_header: str) -> bool
    # HMAC-SHA512 of raw body bytes using INTERSWITCH_CLIENT_SECRET
    # Constant-time compare via hmac.compare_digest (prevents timing attacks)
```

**Success detection:** Interswitch returns `responseCode: "00"` for successful transactions.

---

## Atomicity

Payment status updates and order state transitions are always wrapped together:

```python
with transaction.atomic():
    payment.status = PaymentStatus.SUCCESSFUL
    payment.save()
    order_mark_as_paid(payment.order_id)  # if this raises, payment.save() rolls back
```

If `order_mark_as_paid` fails, the Payment status change is rolled back. The order and payment are always consistent.

---

## Environment Variables Required

Add these to `backend/.env`:

```
INTERSWITCH_BASE_URL=https://sandbox.interswitchng.com
INTERSWITCH_CLIENT_ID=your_client_id
INTERSWITCH_CLIENT_SECRET=your_client_secret
```

---

## Error Response Format

All errors use the project's custom envelope:

```json
{
  "success": false,
  "error": {
    "status_code": 400,
    "message": "Human-readable message",
    "details": {}
  }
}
```

---

## Test Suite (40 tests)

### Property-based tests (Hypothesis)
Tests that verify correctness properties hold across many random inputs:

| Property | What it proves |
|----------|---------------|
| Property 1 | Payment status is always one of pending/successful/failed |
| Property 2 | Transaction references are always unique |
| Property 3 | Payment amount always matches order total |
| Property 4 | Non-confirmed orders are always rejected |
| Property 5 | Duplicate initiation is always rejected |
| Property 6 | `mark_as_paid` called if and only if payment succeeds |
| Property 7 | Atomicity: `mark_as_paid` failure rolls back payment status |
| Property 8 | Idempotent verify: already-successful payments never re-query Interswitch |
| Property 9 | `provider_response` always populated after any Interswitch interaction |
| Property 10 | Interswitch client always raises `InterswitchError` on non-2xx responses |
| Property 11 | Verify response always contains required fields |
| Property 12 | All error responses use the custom envelope format |
| Property 13 | Non-owner access always returns 403 |

### Integration tests
- `PaymentInitiateTests` — 9 tests covering 201, 401, 403, 404, 400 scenarios
- `PaymentVerifyTests` — 6 tests covering 200, 404, 403, 400, idempotency, atomicity
- `PaymentWebhookTests` — 7 tests covering valid sig, invalid sig, unknown ref, idempotency

### Run tests
```bash
cd C:\Users\WELCOME\Desktop\workspace\demo-hack-payment
C:\Users\WELCOME\Desktop\workspace\demo-hack-env\Scripts\python.exe -m pytest backend/tests/test_payments.py -v
```
