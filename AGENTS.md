# AGENTS.md
Agent Operating Guide for the AgroNet Backend Repository

This document defines how AI agents must operate inside this repository.

Agents must follow the rules defined here before performing any code changes.

---

# 1. Core Principle: Iterative Development

AgroNet is built **iteratively**.

Agents must NEVER attempt to build the entire system at once.

Agents may only implement **the specific task that the developer has assigned**.

The workflow is:

Developer selects issue  
↓  
Agent implements only that issue  
↓  
Agent stops and waits for the next instruction

Agents must not:

- implement future features
- refactor unrelated modules
- expand scope beyond the issue

---

# 2. Task Execution Rules

Agents may only work on:

• the **explicit task provided in the prompt**
OR  
• a **GitHub issue referenced in the prompt**

Example:

Valid instruction

> Implement issue #12: Create Product Model

Invalid behavior

Agent implementing:

- orders API
- payment system
- chat system

when the issue only concerns the **product model**.

---

# 3. One Task Rule

Agents must follow the **One Task Rule**.

An agent session may only:

• implement **ONE feature**
• modify **relevant files only**

After completion, the agent must stop.

---

# 4. Scope Guard

Agents must verify scope before making changes.

Before coding, the agent must determine:

What feature is being implemented  
What files are relevant  
What files must NOT be touched

If a change affects unrelated modules, the agent must stop and ask for clarification.

Example:

Working on:

Product API

Allowed changes:

products/models.py  
products/serializers.py  
products/views.py  

Not allowed:

orders/  
payments/  
ai/

---

# CONTEXT

Product context for AgroNet.

---

# Product Vision

AgroNet connects farmers directly to buyers,
removing middlemen from the agricultural supply chain.

Farmers can list produce.
Buyers can search listings and make offers.

---

# Core User Types

Farmer

Posts produce listings.
Accepts or rejects offers.

Buyer

Searches produce listings.
Makes offers and pays for orders.

---

# Core Flow

Farmer signs up
→ posts produce listing

Buyer searches marketplace
→ makes offer

Farmer accepts offer

Buyer pays using Interswitch

Order completed

---

# MVP Features

Authentication
Product listings
Offer negotiation
Payment processing
AI price prediction
Image classification

---

# Non-MVP

Delivery logistics
Wallet
Cooperative accounts
Admin dashboard

# 5. Repository Structure

Agents must follow this repository structure.

backend/
apps/
users/
products/
orders/
payments/
ai/
utils/

config/
tests/

Agents must not create new root directories.

---

# 6. Architecture Rules

Backend architecture:

Controller Layer  
(API Views)

↓

Service Layer  
(Business Logic)

↓

Repository Layer  
(Database Models)

Rules:

• No business logic in views  
• Views call services  
• Services handle workflows  
• Models only represent data

---

# 7. Database Rules

Database: PostgreSQL

Primary entities:

Users  
Products  
Orders  
Payments  

Rules:

• Use UUID primary keys  
• Add indexes to foreign keys  
• Create migrations for schema changes  
• Never modify schema without migrations

---

# 8. API Conventions

Base path

/api/

Example endpoints

GET /api/products  
POST /api/products  
GET /api/products/{id}  

POST /api/orders  
PATCH /api/orders/{id}

All responses must be JSON.

---

# 9. Authentication

Authentication uses JWT.

Header format:

Authorization: Bearer <token>

Roles:

farmer  
buyer

Agents must enforce RBAC permissions.

---

# 10. Order Lifecycle

Orders must follow this state machine:

pending  
→ confirmed  
→ paid  
→ completed  

OR

pending  
→ declined

Agents must not bypass states.

---

# 11. External Integrations

External services used:

Interswitch → payments  
Google Vision → image recognition  
TensorFlow → price prediction  
OneSignal → notifications

Agents must isolate external API calls inside service modules.

---

# 12. Coding Standards

Language: Python 3.11+

Formatting: PEP8

Rules:

• Use type hints  
• Write small functions  
• Add docstrings  
• Avoid deep nesting

---

# 13. Testing

All features must include tests.

Tests must be placed in:

tests/

Test types:

Unit tests  
Integration tests

---

# 14. Security Rules

Agents must never:

• commit secrets  
• store plaintext passwords  
• bypass authentication  
• log sensitive information

Secrets must always use environment variables.

---

# 15. Definition of Done

A task is complete when:

• feature works  
• migrations created if needed  
• tests added  
• code passes linting

After completing the task, the agent must **stop and wait for the next instruction**.

---

# 16. Agent Stop Condition

Agents must stop immediately after completing the requested task.

Agents must not:

• start the next feature  
• anticipate future tasks  
• refactor unrelated code

The developer controls task progression.
