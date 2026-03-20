# Manual Testing Guide — Payment Processing

## Prerequisites

1. Server running from the correct directory:
```bash
cd C:\Users\WELCOME\Desktop\workspace\demo-hack-payment\backend
C:\Users\WELCOME\Desktop\workspace\demo-hack-env\Scripts\python.exe manage.py runserver
```

2. `backend/.env` has Interswitch vars set:
```
INTERSWITCH_BASE_URL=https://sandbox.interswitchng.com
INTERSWITCH_CLIENT_ID=your_client_id
INTERSWITCH_CLIENT_SECRET=your_client_secret
```

3. Swagger UI open at: `http://127.0.0.1:8000/api/schema/swagger-ui/`

---

## Step 1 — Register a Buyer

**POST /api/users/register/**
```json
{
  "email": "buyer@test.com",
  "password": "pass1234",
  "role": "buyer"
}
```

---

## Step 2 — Register a Farmer

**POST /api/users/register/**
```json
{
  "email": "farmer@test.com",
  "password": "pass1234",
  "role": "farmer"
}
```

---

## Step 3 — Get a JWT Token (as Buyer)

**POST /api/token/** (or your login endpoint)
```json
{
  "email": "buyer@test.com",
  "password": "pass1234"
}
```

Copy the `access` token. In Swagger click **Authorize** → enter `Bearer <token>`.

---

## Step 4 — Create a Confirmed Order

You need an order with `status: confirmed`. Depending on what's already in the DB, either:

- Use an existing confirmed order UUID from the admin panel at `http://127.0.0.1:8000/admin/`
- Or go through the full offer flow: create product → make offer → farmer accepts → order becomes confirmed

---

## Step 5 — Initiate Payment

**POST /api/payments/initiate/**

Make sure you're authenticated as the buyer who owns the order.

```json
{
  "order_id": "paste-confirmed-order-uuid-here"
}
```

**Expected:** `201` response with:
```json
{
  "transaction_reference": "AGN-...",
  "amount": "5000.00",
  "status": "pending",
  "order_id": "...",
  "checkout_params": { ... }
}
```

Copy the `transaction_reference` for the next step.

---

## Step 6 — Verify Payment

**POST /api/payments/verify/**

```json
{
  "transaction_reference": "AGN-paste-from-step-5"
}
```

**Expected with real sandbox credentials:** `200` with `status: successful` if Interswitch confirms it.

**Expected without real credentials:** `500` InterswitchError (the call reaches Interswitch but auth fails — this is correct behavior).

---

## Testing Error Scenarios

### 401 — No token
Hit `/api/payments/initiate/` without clicking Authorize in Swagger.
Expected: `401 {"success": false, "error": {"status_code": 401, ...}}`

### 403 — Wrong buyer
Log in as a different buyer, try to initiate payment on an order you don't own.
Expected: `403`

### 403 — Farmer trying to pay
Log in as a farmer, try to initiate.
Expected: `403`

### 404 — Order doesn't exist
```json
{ "order_id": "00000000-0000-0000-0000-000000000000" }
```
Expected: `404`

### 400 — Order not confirmed
Use an order with `status: pending` or `status: paid`.
Expected: `400`

### 400 — Duplicate payment
Initiate twice on the same order.
Expected: second call returns `400`

### 400 — Invalid UUID
```json
{ "order_id": "not-a-uuid" }
```
Expected: `400`

---

## Checking the Database

Use Django admin at `http://127.0.0.1:8000/admin/` to inspect:
- `Payments` table — see Payment records, their status, and raw `provider_response`
- `Orders` table — verify order status transitions to `paid` after successful payment

---

## Webhook Testing (Advanced)

The webhook endpoint requires a valid HMAC-SHA512 signature. To test it manually you need to compute the signature yourself. Use this Python snippet:

```python
import hashlib, hmac, json, os

secret = "your_client_secret"
payload = {"transactionReference": "AGN-YOUR-REF", "responseCode": "00"}
body = json.dumps(payload, sort_keys=True).encode()
sig = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
print(sig)
```

Then POST to `/api/payments/webhook/` with:
- Body: the same JSON payload
- Header: `X-Interswitch-Signature: <sig from above>`

In production, Interswitch sends this automatically.
