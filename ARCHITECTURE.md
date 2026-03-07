# ARCHITECTURE.md

System Architecture for AgroNet Backend

---

# 1. Overview

AgroNet backend is a REST API built with:

Django REST Framework  
PostgreSQL  
JWT Authentication

The API serves a mobile client.

---

# 2. System Modules

users
authentication and role management

products
farmer produce listings

orders
buyer offers and order lifecycle

payments
Interswitch integration

ai
price prediction and image classification

utils
shared utilities

---

# 3. Data Model

Core entities

User
Product
Order
Payment

Relationships

Farmer → Products  
Buyer → Orders  
Product → Orders  
Order → Payment

---

# 4. Order Lifecycle

Orders follow this strict state machine

pending  
→ confirmed  
→ paid  
→ completed  

or

pending  
→ declined

Agents must enforce these transitions.

---

# 5. External Services

Payments → Interswitch  
Image recognition → Google Vision  
AI prediction → TensorFlow  
Notifications → OneSignal

---

# 6. API Layer

API endpoints follow this format

/api/auth/*
/api/products/*
/api/orders/*
/api/payments/*
/api/ai/*

All responses return JSON.