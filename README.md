# AfyaCapital Backend Module

> **Python/Django backend implementation of AfyaCapital — an embedded financing module for openIMIS.**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.x-success)
![GraphQL](https://img.shields.io/badge/GraphQL-enabled-e10098)
![FHIR](https://img.shields.io/badge/FHIR-R4-orange)
![openIMIS](https://img.shields.io/badge/openIMIS-v25.10-blue)
![Hackathon](https://img.shields.io/badge/openIMIS-Hackathon%202026-success)

---

# Project Overview

AfyaCapital is a healthcare claims financing solution built as an extension to **openIMIS**.

Rather than replacing the existing claims management workflow, this backend introduces a financing layer that monitors adjudicated claims and identifies healthcare providers that are eligible for working capital financing.

The backend integrates directly with openIMIS Claims Management through GraphQL and FHIR resources, allowing financing decisions to be based only on verified, adjudicated claims.

---

# Repository Purpose

This repository contains the Django backend responsible for:

- Claims eligibility evaluation
- Financing business logic
- Risk score calculation
- GraphQL resolvers
- REST endpoints
- Integration with openIMIS Claims
- FHIR interoperability
- Communication with external financing partners (mock API)

---

# The Problem

Healthcare providers often wait several weeks—or even months—to receive reimbursement after submitting claims to the Social Health Authority (SHA).

Although claims may already be approved, hospitals still need money to:

- Pay healthcare workers
- Purchase medicines
- Maintain medical equipment
- Continue providing patient care

The challenge is not whether payment will arrive—it is **when**.

AfyaCapital addresses this liquidity gap by enabling providers to access financing against approved but unpaid claims.

---

# Our Solution

AfyaCapital extends openIMIS by introducing a financing workflow after claims have been successfully adjudicated.

The backend continuously monitors claims that satisfy financing requirements.

Eligible claims are transformed into financing opportunities that can be presented to healthcare facilities.

The financing workflow follows this sequence:

```
Hospital

↓

Claim submitted

↓

openIMIS Claims Module

↓

Claim Checked / Approved

↓

AfyaCapital Eligibility Engine

↓

Risk Assessment

↓

Financing Offer

↓

Partner Bank API (Mock)

↓

Advance Approved
```

---

# Backend Responsibilities

The backend performs the following core functions.

## Claim Monitoring

Reads claim status from openIMIS.

Only claims that have successfully completed adjudication are considered.

---

## Eligibility Engine

Evaluates whether claims satisfy financing rules.

Example conditions:

- Claim status = Checked
- Claim approved
- Payment not yet received
- No existing financing

---

## Risk Engine

Calculates a financing risk score using factors such as:

- Claim approval history
- Facility profile
- Historical rejection rate
- Approved claim value
- Outstanding financed claims

---

## Financing Engine

Calculates available financing.

Example:

```
Advance Amount =
Approved Claim Amount × Advance Percentage
```

Example:

Approved Claim:

KES 500,000

Advance Rate:

70%

Available Advance:

KES 350,000

---

# Minimum Viable Product

For the hackathon, this backend powers a simple financing workflow.

1. Retrieve approved claims from openIMIS.
2. Calculate financing eligibility.
3. Generate a risk score.
4. Return financing offers through GraphQL.
5. Simulate financing approval through a mock banking endpoint.

No real financial transactions occur.

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.11 |
| Framework | Django |
| API | GraphQL |
| REST | Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT |
| Interoperability | FHIR R4 |
| Claims Engine | openIMIS v25.10 |

---

# Architecture

(Add your architecture diagram here.)

```
Hospital
        │
        ▼
openIMIS Claims
        │
        ▼
Claim Adjudication
        │
        ▼
AfyaCapital Backend
        │
 ┌──────────────┐
 │Eligibility   │
 │Risk Engine   │
 │Financing API │
 └──────────────┘
        │
        ▼
Partner Bank (Mock)
```

---

# GraphQL

Primary endpoint

```
http://localhost:8000/api/graphql
```

Example query

```graphql
query {
  claims {
    edges {
      node {
        id
        status
        total
      }
    }
  }
}
```

Future queries include

- eligibleClaims
- financingOffers
- facilityRiskScore

---

# REST API

Example endpoints

```
GET /api/eligible-claims
```

Returns all financing-eligible claims.

---

```
POST /api/request-financing
```

Creates a financing request.

---

```
GET /api/risk-score/{facility}
```

Returns calculated facility risk.

---

# FHIR Integration

AfyaCapital relies on FHIR resources for interoperability.

Resources consumed include:

- Claim
- ClaimResponse
- Organization
- Coverage

FHIR allows the financing engine to remain interoperable with existing digital health systems.

---

# Security

The backend follows these principles:

- JWT Authentication
- Role-based access
- GraphQL authorization
- Patient information remains inside openIMIS
- Banks receive only financing-related information

Shared with financing partners:

- Claim ID
- Facility
- Approved Amount
- Financing Amount
- Risk Score

Not shared:

- Patient demographics
- Diagnosis
- Clinical history
- Treatment information

---

# Running the Backend

Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_HANDLE/openimis-be_py.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Start development server

```bash
python manage.py runserver
```

For the complete Docker deployment, refer to the **openimis-dist_dkr** repository.

---

# Project Structure

```
openimis-be_py/

modules/
graphql/
api/
services/
models/
serializers/
views/
signals/
tests/
```

---

# Future Improvements

- Automated repayment after SHA reimbursement
- Bank API integration
- Machine learning risk scoring
- Multiple financing partners
- Loan portfolio dashboard
- Notification service
- Audit logging

---

# Known Limitations

- Financing approval is simulated.
- Bank integration is mocked.
- Risk scoring uses simplified logic for demonstration.
- Claims repayment automation is not implemented during the hackathon.

---

# Contributing

Create a feature branch

```bash
git checkout -b feature/afyacapital
```

Commit changes

```bash
git commit -m "feat: add financing backend"
```

Push

```bash
git push origin feature/afyacapital
```

Create a Draft Pull Request against the official openIMIS backend repository.

---

# License

This project was developed for the **openIMIS Hackathon 2026**.

It follows the licensing terms of the openIMIS project.

---

# Team

**Project:** AfyaCapital

Built for the **openIMIS Hackathon 2026**

Transforming approved healthcare claims into timely working capital for healthcare providers.