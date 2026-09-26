# Zoho CRM API Integration

A production-ready Django integration with **Zoho CRM v3 APIs**. Built with dynamic OAuth 2.0 authentication, offline token refresh, full CRUD capabilities for leads, and comprehensive error handling.

**Tech Stack:** Python 3, Django 5, SQLite, Requests, python-dotenv

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Features](#architecture--features)
3. [Environment Configuration](#environment-configuration)
4. [Installation & Setup](#installation--setup)
5. [Zoho Developer Console Setup](#zoho-developer-console-setup)
6. [API Endpoints & Usage](#api-endpoints--usage)
7. [Example Requests & Responses](#example-requests--responses)
8. [Error Handling Demonstration](#error-handling-demonstration)
9. [Technical Deep-Dive & Architecture](#technical-deep-dive--architecture)
10. [AI Tools & Development Notes](#ai-tools--development-notes)

---

## Project Overview

This project provides an end-to-end integration between a Django backend service and **Zoho CRM v3 APIs**. 

The system implements a production-grade OAuth 2.0 authorization code flow (with offline token refresh handling), record retrieval, record insertion, record lookup by ID, and centralized error handling for Zoho API response states.

### Core Capabilities:
- **Zero Hardcoded Secrets / Tokens:** Access and refresh tokens are retrieved dynamically via OAuth 2.0 and securely persisted in the database.
- **Automatic Token Lifecycle Management:** The application detects expired access tokens and refreshes them silently via the stored `refresh_token` without user intervention.
- **CRUD Operations on Zoho CRM:** Read leads, insert new leads into Zoho CRM, and query individual records by ID.
- **Robust Error Handling:** Detects and formats HTTP 401 unauthorized/expired states, missing mandatory field errors, invalid modules, and upstream network failures into uniform JSON responses.

---

## Architecture & Features

```
[ Browser / Client ]
        |
        v
[ Django Backend (w3scloud_crm) ]
   ├── zoho_login           ---> Redirect to Zoho Accounts OAuth
   ├── zoho_callback        <--- Exchange Code for Access & Refresh Tokens
   │                             └─> Persist in SQLite (ZohoToken Model)
   ├── get_valid_access_token() -> Auto-checks expires_at; refreshes token if expired
   ├── list_leads           ---> GET  https://www.zohoapis.com/crm/v3/Leads
   ├── create_lead          ---> POST https://www.zohoapis.com/crm/v3/Leads
   ├── get_lead             ---> GET  https://www.zohoapis.com/crm/v3/Leads/{record_id}
   └── handle_zoho_error    ---> Centralized API error response formatter
```

### Database Model (`zoho/models.py`)
```python
class ZohoToken(models.Model):
    user_identifier = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    expires_at = models.DateTimeField()
```

---

## Environment Configuration

Create a `.env` file in the root directory (based on `.env.example`).

```env
# Zoho Developer Console Credentials
ZOHO_CLIENT_ID=your_zoho_client_id_here
ZOHO_CLIENT_SECRET=your_zoho_client_secret_here
ZOHO_REDIRECT_URI=http://localhost:8000/zoho/callback/
```

> **Security Note:** `.env` and `db.sqlite3` are strictly included in `.gitignore` to prevent any credentials or active tokens from leaking into source control.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10+
- `pip` package manager

### 2. Clone the Repository
```bash
git clone https://github.com/MSCRAFI/w3scloud_crm.git
cd w3scloud_crm
```

### 3. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Start the Server
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

---

## Zoho Developer Console Setup

1. Open the [Zoho Developer Console](https://api-console.zoho.com/).
2. Click **Add Client** and select **Server-based Applications**.
3. Fill in the details:
   - **Client Name:** `W3SCLOUD CRM Integration`
   - **Homepage URL:** `http://localhost:8000`
   - **Authorized Redirect URIs:** `http://localhost:8000/zoho/callback/`
4. Copy the generated **Client ID** and **Client Secret** into your `.env` file.
5. Required Scopes configured in the application:
   - `ZohoCRM.modules.leads.ALL`
   - `ZohoCRM.modules.contacts.READ`

---

## API Endpoints & Usage

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/zoho/login/` | Initiates Zoho OAuth 2.0 consent flow |
| `GET` | `/zoho/callback/` | Handles OAuth redirect, exchanges code for tokens, saves to DB |
| `GET` | `/zoho/leads/` | Retrieves leads list (Record ID, Name, Email, Phone) |
| `GET`/`POST` | `/zoho/leads/create/` | Creates a new Lead in Zoho CRM |
| `GET` | `/zoho/leads/<record_id>/` | Retrieves a specific Lead by Record ID |

---

## Example Requests & Responses

### 1. Authentication Flow
- **Step 1:** Visit `http://127.0.0.1:8000/zoho/login/` in your browser.
- **Step 2:** Zoho OAuth consent screen appears. Click **Accept**.
- **Step 3:** Redirects to `/zoho/callback/?code=...`. The system saves credentials and redirects directly to `/zoho/leads/`.

---

### 2. Read Leads (`GET /zoho/leads/`)
**Request:**
```http
GET http://127.0.0.1:8000/zoho/leads/
```

**Response (HTTP 200 OK):**
```json
{
  "leads": [
    {
      "id": "62489000000492001",
      "Last_Name": "Chowdhury",
      "Email": "salman@example.com",
      "Phone": "+8801700000000"
    }
  ]
}
```

---

### 3. Insert Lead (`GET /zoho/leads/create/`)
**Request:**
```http
GET http://127.0.0.1:8000/zoho/leads/create/
```

**Payload sent to Zoho CRM v3:**
```json
{
  "data": [
    {
      "First_Name": "Salman",
      "Last_Name": "Chowdhury",
      "Company": "ABC Ltd",
      "Email": "salman@example.com",
      "Phone": "+8801700000000"
    }
  ]
}
```

**Response (HTTP 200 OK):**
```json
{
  "created_id": "62489000000492001"
}
```

---

### 4. Retrieve Inserted Record by ID (`GET /zoho/leads/<record_id>/`)
**Request:**
```http
GET http://127.0.0.1:8000/zoho/leads/62489000000492001/
```

**Response (HTTP 200 OK):**
```json
{
  "data": [
    {
      "id": "62489000000492001",
      "First_Name": "Salman",
      "Last_Name": "Chowdhury",
      "Company": "ABC Ltd",
      "Email": "salman@example.com",
      "Phone": "+8801700000000",
      "Created_Time": "2026-09-26T11:20:00+06:00"
    }
  ]
}
```

---

## Error Handling Demonstration

The application implements `handle_zoho_error(resp)` to map and capture Zoho CRM error scenarios:

### 1. Token Expired / Invalid (HTTP 401)
If the token is revoked or corrupted:
```json
{
  "error": "Token invalid/expired",
  "detail": {
    "code": "INVALID_OAUTH_TOKEN",
    "message": "Access token has expired or is invalid",
    "status": "error"
  }
}
```

### 2. Missing Mandatory Field (HTTP 400)
When attempting to insert a Lead without `Last_Name`:
```json
{
  "error": "Missing required field",
  "detail": {
    "code": "MANDATORY_NOT_FOUND",
    "details": { "api_name": "Last_Name" },
    "message": "required field not found",
    "status": "error"
  }
}
```

### 3. Invalid Module Name (HTTP 400)
When targeting an invalid or disabled module:
```json
{
  "error": "Invalid module name",
  "detail": {
    "code": "INVALID_MODULE",
    "message": "the module name given seems to be invalid",
    "status": "error"
  }
}
```

---

## Technical Deep-Dive & Architecture

### Q1. OAuth — Explain Client ID, Client Secret, Access Token, and Refresh Token, and how they are used in an API integration.
- **Client ID:** A unique public identifier assigned to the application by Zoho Developer Console. Identifies which client is initiating the request.
- **Client Secret:** A confidential cryptographic secret known only to the application backend and Zoho's authorization server. Used during the token exchange to authenticate client identity.
- **Access Token:** A short-lived bearer credential (typically valid for 1 hour). Passed in the `Authorization: Zoho-oauthtoken <token>` HTTP header to authorize API calls against CRM endpoints.
- **Refresh Token:** A long-lived credential issued during initial user consent (`access_type=offline`). It is used exclusively to obtain fresh access tokens when old ones expire without re-prompting user login.

---

### Q2. Token Expiration — Your application works today but tomorrow returns an authentication error. What could cause this? How would you avoid asking the user to authorize every time?
- **Cause:** Zoho CRM access tokens expire after 3600 seconds (1 hour). Tomorrow, the stored access token is expired, causing Zoho to return `HTTP 401 INVALID_OAUTH_TOKEN`.
- **Solution:** 
  1. During initial OAuth authorization, request `access_type=offline` and `prompt=consent` to receive a `refresh_token`.
  2. Persist the `refresh_token` and `expires_at` timestamp in the database.
  3. Before every outbound API call, compare `timezone.now()` with `expires_at`.
  4. If expired (or expiring within 5 minutes), perform an automated POST request to `https://accounts.zoho.com/oauth/v2/token` with `grant_type=refresh_token`, update the stored access token, and proceed with the API call seamlessly.

---

### Q3. API Field Names — A CRM field is displayed as "Customer Type" but the API expects "Customer_Type". Why does this matter? How would you find the correct API field name?
- **Why it matters:** UI display labels are human-readable, translatable, and customizable by CRM admins. The underlying API expects the immutable programmatic field identifier (`api_name`). Supplying display labels causes the API to ignore the parameter or fail with `INVALID_DATA`.
- **How to find the correct API field name:**
  1. **Zoho CRM UI:** Go to **Setup** ➔ **Customization** ➔ **Modules and Fields** ➔ Select Module (e.g. Leads) ➔ Click **Fields** ➔ Click the three dots icon ➔ **Field API Names**.
  2. **Metadata API:** Query the Zoho Fields Metadata API endpoint:
     ```http
     GET https://www.zohoapis.com/crm/v3/settings/fields?module=Leads
     ```
     Inspect the JSON response for the exact `api_name` property.

---

### Q4. Insert Record — Explain how you would insert a Lead using an HTTP API. Cover HTTP method, URL structure, authorization, request body, required fields, and expected response.
- **HTTP Method:** `POST`
- **URL Structure:** `https://www.zohoapis.com/crm/v3/Leads`
- **Authorization:** `Authorization: Zoho-oauthtoken <access_token>` header with `Content-Type: application/json`.
- **Request Body:**
  ```json
  {
    "data": [
      {
        "First_Name": "Jane",
        "Last_Name": "Doe",
        "Company": "Acme Corp",
        "Email": "jane.doe@example.com",
        "Phone": "+15551234567"
      }
    ]
  }
  ```
- **Required Fields:** `Last_Name` is standard mandatory in Zoho CRM (and `Company` in default Lead layouts).
- **Expected Response (HTTP 201 Created / 200 OK):**
  ```json
  {
    "data": [
      {
        "code": "SUCCESS",
        "details": {
          "id": "62489000000492100",
          "created_time": "2026-09-26T11:30:00+06:00"
        },
        "message": "record added",
        "status": "success"
      }
    ]
  }
  ```

---

### Q5. GET vs Search — What is the difference between retrieving records and searching records? Give an example of when you would use each.
- **GET (Listing / By ID):**
  - **Endpoint:** `GET /crm/v3/Leads` or `GET /crm/v3/Leads/{id}`
  - **Purpose:** Fetches records by sequential pagination or direct unique Record ID lookup.
  - **When to use:** Nightly data warehouse syncs, building paginated lead tables, or fetching full details of a known record after creation.
- **Search:**
  - **Endpoint:** `GET /crm/v3/Leads/search?(email=...|phone=...|criteria=...)`
  - **Purpose:** Queries CRM indices for records matching specific field criteria, email addresses, phone numbers, or free-text keywords.
  - **When to use:** Deduplication check when a user submits a web contact form to verify if `john@example.com` already exists in CRM before inserting.

---

### Q6. Duplicate Handling — Your application receives the same customer twice. How would you prevent duplicate CRM records?
1. **Search Before Insert:** Prior to record creation, query `GET /crm/v3/Leads/search?email=<email>`. If a record matches, update the existing record (`PUT /crm/v3/Leads/{id}`) instead of creating a new one.
2. **Zoho Upsert API:** Use `POST /crm/v3/Leads/upsert` specifying `duplicate_check_fields: ["Email"]`. Zoho CRM will automatically update if the email exists, or insert if new.
3. **Application Deduplication Cache:** Implement an idempotency key or hash check (e.g. SHA-256 of `email + phone`) stored in Redis with a TTL of 10 minutes to reject duplicate webhook submissions.

---

### Q7. Error Handling — The API returns HTTP 401 / OAUTH_SCOPE_MISMATCH. What does it mean? How would you investigate and fix it?
- **Meaning:** The access token is valid and authenticated, but the granted scopes during the original OAuth consent flow do not include the permission required for this specific API endpoint or operation (e.g., trying to write to Contacts when only `ZohoCRM.modules.leads.ALL` was granted).
- **Investigation:**
  1. Check Zoho CRM API documentation for the endpoint being called to identify the exact mandatory scope.
  2. Inspect the `scope` query parameter passed in your OAuth login URL (`zoho_login`).
- **Fix:**
  1. Add the missing scope (e.g. `ZohoCRM.modules.contacts.ALL`) to the `scope` parameter in `zoho_login`.
  2. Re-trigger user consent with `prompt=consent` to issue a new authorization code and refresh token containing the updated scope set.

---

### Q8. Production Architecture — A Node.js / Python application connects to multiple clients' CRM accounts. How would you store OAuth credentials securely and keep each customer's data isolated?
1. **Multi-Tenant Schema Isolation:**
   - Store OAuth records with a strict `tenant_id` foreign key:
     `TenantOAuthCredentials(tenant_id, client_id, encrypted_client_secret, access_token, refresh_token, token_expiry)`.
   - Enforce database Row-Level Security (RLS) or tenant isolation middleware ensuring database queries filter by tenant context.
2. **Envelope Encryption at Rest:**
   - Encrypt Client Secrets, Access Tokens, and Refresh Tokens using AES-256-GCM or AWS KMS / HashiCorp Vault. Master encryption keys should reside in a secure Key Management Service, never in code.
3. **Tenant-Scoped Context:**
   - Resolve tenant identity from authenticated session / JWT token on every inbound request; instantiate CRM client instances exclusively with the tenant's isolated credentials.

---

### Q9. Large Data — A client needs 200,000 CRM records synchronized with an external system. Explain pagination, batching, rate limits, retries, failed records, logging, and resume/retry design.
- **Bulk API vs REST Pagination:** Instead of making 1,000 REST requests (200 records/page max), use **Zoho CRM Bulk Read API** (`/crm/v3/bulk/read`). It creates an asynchronous export job, exporting 200,000 records into a compressed CSV download without exhausting API call credits.
- **Batching:** When inserting/updating via REST, batch 100 records per request (Zoho's maximum batch size for `/crm/v3/Leads`).
- **Rate Limits & Throttling:** Implement a token bucket or queue limiter (e.g., Celery / BullMQ + Redis) to stay within Zoho's concurrency and daily request quotas.
- **Retries & Backoff:** On `HTTP 429 Too Many Requests` or `HTTP 5xx`, apply jittered exponential backoff (`delay = 2^retry_count + random_jitter`).
- **Failed Records & Dead Letter Queue (DLQ):** Zoho returns per-record success/failure arrays. Parse `data[i].status == "error"`, write failed payloads with error descriptions to a Dead Letter Queue / database audit table for manual inspection.
- **Resume / Checkpoint State:** Track the sync state using high-watermark timestamps (`last_modified_time`) or cursor tokens stored in a sync job database. If interrupted, the sync worker resumes from the last committed checkpoint.

---

### Q10. End-to-End Integration Scenario — Design External Website ➔ Node.js API ➔ Zoho CRM for `{ name: 'John Smith', email: 'john@example.com', company: 'ABC Ltd', phone: '+8801XXXXXXXXX' }`.
```
[ External Website ]
       │  (HTTPS POST /api/v1/leads + API Key / Recaptcha)
       ▼
[ Node.js API Gateway ]
  ├─ 1. Payload Validation (Joi / Zod: email regex, E.164 phone, length check)
  ├─ 2. Split Name -> First_Name: "John", Last_Name: "Smith"
  ├─ 3. In-Memory / Redis Lock (Prevent concurrent duplicate submissions)
  ├─ 4. Check Queue (BullMQ / RabbitMQ for resilience against CRM outages)
       │
       ▼ (Worker Thread)
[ Zoho CRM Service Module ]
  ├─ 5. Obtain valid tenant token (Auto-refreshed via Refresh Token)
  ├─ 6. Upsert to Zoho CRM v3: POST /crm/v3/Leads/upsert (duplicate_check: ["Email"])
  ├─ 7. Handle Response / Outage:
  │     - If Zoho is down (HTTP 500/503/429): Retries via exponential backoff queue
  │     - If success: Acknowledge job and record CRM Record ID
  └─ 8. Structured Logging: JSON logs with correlation_id, execution time, masked PII
       │
       ▼
[ Client Response ]
  HTTP 200 OK: { "status": "success", "lead_id": "62489000000492001", "transaction_id": "tx_9812" }
```

---

## AI Tools & Development Notes

Overview of AI tools utilized during development:

### 1. Claude AI (Anthropic)
- **What it helped with:** Figuring out the Zoho CRM v3 API documentation, OAuth 2.0 authorization code flow requirements, and drafting the initial structure for the Django views (`zoho_login`, `zoho_callback`, `list_leads`, `create_lead`, `get_lead`, and `handle_zoho_error`).
- **What was changed / customized:** Adapted the OAuth callback and token refresh logic to persist state in Django's SQLite database (`ZohoToken` model) with timezone-aware expiration handling. Refined the views to cleanly return structured JSON responses and aligned error handling with Zoho's API error codes.
- **Problems solved:** Accelerated the learning curve for Zoho CRM's OAuth token exchange parameters, headers (`Zoho-oauthtoken`), and endpoint payload formats.

### 2. GitHub Copilot
- **What it helped with:** In-editor inline autocompletion while writing Django models, URL routing, request parameters, dictionary mappings, and repetitive boilerplate.
- **What was changed / customized:** Reviewed and adjusted suggested completions to conform to Zoho CRM API field naming conventions (e.g. `Last_Name`, `First_Name`) and proper Python type practices.
- **Problems solved:** Sped up code authoring, reduced repetitive typing, and prevented syntax errors.

### 3. Google Antigravity
- **What it helped with:** Structuring and drafting the project's `README.md` file according to the technical assessment specifications and instructions.
- **What was changed / customized:** Compiled project setup steps, environment configuration, and API endpoint documentation into clear markdown formatting.
- **Problems solved:** Saved time on documentation formatting, ensuring installation steps, API endpoints, and usage examples were neatly organized.



