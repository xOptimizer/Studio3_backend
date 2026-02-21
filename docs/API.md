# API Documentation (Postman-ready)

For the Flask backend. Use this doc to build and test requests in Postman and to integrate from the frontend.

---

## Postman setup

### 1. Environment variables

Create a Postman **Environment** (e.g. "Backend Local") with:

| Variable      | Initial / Current value   | Description                    |
|---------------|----------------------------|--------------------------------|
| `baseUrl`     | `http://localhost:9000`    | API base URL (no trailing `/`) |
| `accessToken` | *(leave empty)*            | Set automatically after login/register (see below) |

Use `{{baseUrl}}` and `{{accessToken}}` in requests.

### 2. Saving the access token

After **Login** or **Register**, the response body contains `data.accessToken`. To reuse it for protected routes:

1. Open the **Login** (or **Register**) request in Postman.
2. Go to the **Tests** tab.
3. Add:

```javascript
var json = pm.response.json();
if (json.data && json.data.accessToken) {
  pm.environment.set("accessToken", json.data.accessToken);
}
```

4. Run Login/Register; `accessToken` will be set in your environment. Protected requests that use `Authorization: Bearer {{accessToken}}` will then work.

### 3. Cookies (refresh / logout)

The server sets an httpOnly cookie `refreshToken` on **Login**, **Register**, and **Refresh**. Postman sends stored cookies automatically for the same domain.

- **Refresh:** Send a **POST** to `/api/auth/refresh` with no body and no auth header. If you previously called Login/Register from the same Postman session, the `refreshToken` cookie will be sent and you’ll get a new `accessToken` (and new cookie).
- **Logout / Logout-all:** Same idea: cookie is sent automatically if it was set earlier.

### 4. Suggested flow for testing

1. **GET** `{{baseUrl}}/` → Health check.
2. **POST** `{{baseUrl}}/api/auth/login` (or register) → Get token; use the Tests script above to set `accessToken`.
3. **GET** `{{baseUrl}}/api/user/getall` with header `Authorization: Bearer {{accessToken}}` → Protected route.
4. **POST** `{{baseUrl}}/api/auth/refresh` (no headers, cookies sent automatically) → New access token.
5. **POST** `{{baseUrl}}/api/auth/logout` or **POST** `{{baseUrl}}/api/auth/logout-all` (with Bearer token for logout-all).

---

## Response format

**Success:**

```json
{
  "success": true,
  "message": "<message>",
  "data": { ... }
}
```

**Error:**

```json
{
  "success": false,
  "message": "<error message>"
}
```

Common status codes: `200`/`201` success, `400` bad request, `401` unauthorized, `409` conflict, `429` too many requests, `500` server error.

**Protected routes:** Send header:

```http
Authorization: Bearer {{accessToken}}
```

---

## Endpoints (copy into Postman)

### Health

**GET** `{{baseUrl}}/`

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `{{baseUrl}}/` |
| **Headers** | *(none)* |
| **Body** | *(none)* |

**Example response (200):**

```json
{
  "message": "Virtual Instructor Backend Running"
}
```

---

### Auth – OTP generate

**POST** `{{baseUrl}}/api/auth/otp/generate`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/otp/generate` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw JSON |

```json
{
  "email": "user@example.com"
}
```

**Example response (200):**

```json
{
  "success": true,
  "message": "OTP sent successfully.",
  "data": { "message": "OTP sent successfully." }
}
```

---

### Auth – OTP resend

**POST** `{{baseUrl}}/api/auth/otp/resend`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/otp/resend` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw JSON |

```json
{
  "email": "user@example.com"
}
```

Response same as OTP generate. Possible `429` if rate/resend limit exceeded.

---

### Auth – Register

**POST** `{{baseUrl}}/api/auth/register`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/register` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw JSON |

```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "securePassword123",
  "otp": "123456"
}
```

**Example response (200):** Server sets cookie `refreshToken`.

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "name": "John Doe",
      "email": "user@example.com"
    }
  }
}
```

Use **Tests** script from “Saving the access token” to set `accessToken`. Errors: `400` (validation / invalid OTP), `409` (email already exists).

---

### Auth – Login

**POST** `{{baseUrl}}/api/auth/login`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/login` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw JSON |

```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Example response (200):** Same shape as Register; server sets cookie `refreshToken`.

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "name": "John Doe",
      "email": "user@example.com"
    }
  }
}
```

Use **Tests** script to set `accessToken`. Errors: `400` (missing fields), `401` (invalid credentials).

---

### Auth – Refresh

**POST** `{{baseUrl}}/api/auth/refresh`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/refresh` |
| **Headers** | *(none)* |
| **Body** | *(none)* |

Postman sends the `refreshToken` cookie automatically if it was set by Login/Register/Refresh earlier.

**Example response (200):** New access token and new refresh cookie.

```json
{
  "success": true,
  "message": "Token refreshed.",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": { "name": "John Doe", "email": "user@example.com" }
  }
}
```

You can use the same **Tests** script to update `accessToken`. Error: `401` if cookie missing/invalid/expired.

---

### Auth – Logout

**POST** `{{baseUrl}}/api/auth/logout`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/logout` |
| **Headers** | *(none)* |
| **Body** | *(none)* |

Cookie `refreshToken` is sent automatically if present; server clears it.

**Example response (200):**

```json
{
  "success": true,
  "message": "Logout successful.",
  "data": { "message": "Logout successful." }
}
```

---

### Auth – Logout all (protected)

**POST** `{{baseUrl}}/api/auth/logout-all`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/logout-all` |
| **Headers** | `Content-Type: application/json`<br>`Authorization: Bearer {{accessToken}}` |
| **Body** | *(none)* |

**Example response (200):**

```json
{
  "success": true,
  "message": "Logged out from all devices.",
  "data": { "message": "Logged out from all devices." }
}
```

Error: `401` if not authenticated.

---

### Auth – Forget password

**POST** `{{baseUrl}}/api/auth/forget-password`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/forget-password` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw JSON |

```json
{
  "email": "user@example.com"
}
```

**Example response (200):**

```json
{
  "success": true,
  "message": "If an account exists with this email, you will receive a password reset link.",
  "data": { "message": "If an account exists with this email, you will receive a password reset link." }
}
```

---

### Auth – Reset password

**POST** `{{baseUrl}}/api/auth/reset-password`

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `{{baseUrl}}/api/auth/reset-password` |
| **Headers** | `Content-Type: application/json` |
| **Body** | raw JSON |

```json
{
  "token": "<token_from_reset_email_link>",
  "newPassword": "newSecurePassword123"
}
```

**Example response (200):**

```json
{
  "success": true,
  "message": "Password has been reset successfully.",
  "data": { "message": "Password has been reset successfully." }
}
```

Error: `400` if token invalid/expired or `newPassword` missing.

---

### Auth – Google OAuth (browser)

**GET** `{{baseUrl}}/api/auth/google` – redirects user to Google. Not meant to be called from Postman as a normal API request; use in the browser or a frontend app.

**GET** `{{baseUrl}}/api/auth/google/callback?code=...&state=...` – callback URL; server redirects to frontend with `#access_token=...` and sets refresh cookie. Test OAuth in the app, not in Postman.

---

### User – Get all (protected)

**GET** `{{baseUrl}}/api/user/getall`

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `{{baseUrl}}/api/user/getall` |
| **Headers** | `Authorization: Bearer {{accessToken}}` |
| **Body** | *(none)* |

**Example response (200):**

```json
{
  "success": true,
  "message": "Users fetched successfully.",
  "data": {
    "users": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "name": "John Doe",
        "image": null,
        "email_verified": true,
        "created_at": "2025-02-20T12:00:00+00:00"
      }
    ],
    "count": 1
  }
}
```

Error: `401` if token missing/invalid or session expired.

---

## Quick reference

| Method | URL | Auth | Body |
|--------|-----|------|------|
| GET | `{{baseUrl}}/` | — | — |
| POST | `{{baseUrl}}/api/auth/otp/generate` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/otp/resend` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/register` | — | `{ "name", "email", "password", "otp" }` |
| POST | `{{baseUrl}}/api/auth/login` | — | `{ "email", "password" }` |
| POST | `{{baseUrl}}/api/auth/refresh` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout-all` | Bearer | — |
| POST | `{{baseUrl}}/api/auth/forget-password` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/reset-password` | — | `{ "token", "newPassword" }` |
| GET | `{{baseUrl}}/api/auth/google` | — | Browser redirect |
| GET | `{{baseUrl}}/api/auth/google/callback` | — | OAuth callback |
| GET | `{{baseUrl}}/api/user/getall` | Bearer | — |

**Auth column:** “Bearer” = `Authorization: Bearer {{accessToken}}`; “Cookie” = send cookies (Postman does this automatically after login/register/refresh).
