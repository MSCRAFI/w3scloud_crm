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
9. [AI Tools & Development Notes](#ai-tools--development-notes)

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
| `POST` / `GET` | `/zoho/leads/create/` | Creates a new Lead in Zoho CRM (accepts custom JSON body or falls back to sample defaults) |
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
      "id": "7633822000000707001",
      "Last_Name": "Smith",
      "Email": "john.smith@example.com",
      "Phone": "+8801700000000"
    }
  ]
}
```

---

### 3. Insert Lead (`POST /zoho/leads/create/`)

The endpoint accepts a custom JSON body from Postman (or clients). If called with no body or via `GET` in a browser, it gracefully falls back to default sample values.

**Request (Postman `POST`):**
```http
POST http://127.0.0.1:8000/zoho/leads/create/
Content-Type: application/json

{
  "First_Name": "John",
  "Last_Name": "Smith",
  "Company": "ABC Ltd",
  "Email": "john.smith@example.com",
  "Phone": "+8801700000000"
}
```

**Payload Sent to Zoho CRM v3:**
```json
{
  "data": [
    {
      "First_Name": "John",
      "Last_Name": "Smith",
      "Company": "ABC Ltd",
      "Email": "john.smith@example.com",
      "Phone": "+8801700000000"
    }
  ]
}
```

**Response (HTTP 200 OK):**
```json
{
  "created_id": "7633822000000708001"
}
```

---

### 4. Retrieve Inserted Record by ID (`GET /zoho/leads/<record_id>/`)
**Request:**
```http
GET http://127.0.0.1:8000/zoho/leads/7633822000000708001/
```

**Response (HTTP 200 OK):**
```json
{
  "data": [
    {
      "id": "7633822000000708001",
      "First_Name": "John",
      "Last_Name": "Smith",
      "Company": "ABC Ltd",
      "Email": "john.smith@example.com",
      "Phone": "+8801700000000",
      "Created_Time": "2026-09-26T12:46:03+06:00"
    }
  ]
}
```

---

## Error Handling Demonstration

The application implements `handle_zoho_error(resp)` to map and capture Zoho CRM error scenarios into uniform, clean JSON responses:

### 1. Missing Mandatory Field (HTTP 400 Bad Request)
When attempting to insert a Lead without the required `Last_Name` field:

**Request (Postman `POST`):**
```http
POST http://127.0.0.1:8000/zoho/leads/create/
Content-Type: application/json

{
  "First_Name": "John",
  "Last_Name": null,
  "Company": "ABC Ltd"
}
```

**Response (HTTP 400 Bad Request):**
```json
{
  "error": "Missing required field",
  "detail": {
    "data": [
      {
        "code": "MANDATORY_NOT_FOUND",
        "details": {
          "api_name": "Last_Name",
          "json_path": "$.data[0].Last_Name"
        },
        "message": "required field not found",
        "status": "error"
      }
    ]
  }
}
```

---

### 2. Invalid Record ID / URL Pattern (HTTP 400 Bad Request)
When querying a non-existent or invalid record ID:

**Request:**
```http
GET http://127.0.0.1:8000/zoho/leads/9999999999999999999/
```

**Response (HTTP 400 Bad Request):**
```json
{
  "error": "Zoho API error",
  "detail": {
    "code": "INVALID_URL_PATTERN",
    "message": "Please check if the URL trying to access is a correct one",
    "status": "error"
  }
}
```

---

### 3. Token Expired / Invalid (HTTP 401 Unauthorized)
If an access token is revoked, invalid, or expired:

**Response (HTTP 401 Unauthorized):**
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

---

### 4. Invalid Module Name (HTTP 400 Bad Request)
When targeting an invalid or disabled CRM module:

**Response (HTTP 400 Bad Request):**
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



