# API Documentation (Postman-ready)

For the **Studiothree Discover** backend. Use this doc to build and test requests in Postman and to integrate from mobile (iOS/Android) or web clients.

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
3. **POST** `{{baseUrl}}/api/auth/refresh` (no headers, cookies sent automatically) → New access token.
4. **POST** `{{baseUrl}}/api/auth/logout` or **POST** `{{baseUrl}}/api/auth/logout-all` (with Bearer token for logout-all).

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
  "message": "Studiothree Discover API running"
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

### Auth – Username check

**GET** `{{baseUrl}}/api/auth/username/check?username=maya_art&for_user_id=me`

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `{{baseUrl}}/api/auth/username/check` |
| **Query** | `username` (required); `for_user_id=me` (optional, requires Bearer token to exclude current user when changing username) |
| **Headers** | Optional: `Authorization: Bearer {{accessToken}}` when using `for_user_id=me` |

**Example response (200):**

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "available": true,
    "normalized": "maya_art",
    "reason": null,
    "message": "Username is available.",
    "suggestions": []
  }
}
```

When taken, `available` is `false`, `reason` is `"taken"` or `"reserved"`, and `suggestions` may include alternatives.

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
  "username": "maya_art",
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
      "username": "maya_art",
      "name": "John Doe",
      "email": "user@example.com",
      "emailVerified": true,
      "onboardingComplete": false,
      "role": null
    }
  }
}
```

Use **Tests** script from “Saving the access token” to set `accessToken`. Errors: `400` (validation / invalid OTP), `409` (username or email taken).

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
  "username": "maya_art",
  "password": "securePassword123"
}
```

**Example response (200):** Same shape as Register; server sets cookie `refreshToken`.

Errors: `400` (missing fields), `401` (invalid credentials).

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
    "user": { "name": "John Doe", "email": "user@example.com", "role": null }
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

## User & profile

### User – Get me (protected)

**GET** `{{baseUrl}}/api/user/me` — Bearer required. Returns full profile including `username`, `canChangeUsername`, `tastePreferences`, seller status.

### User – Update me (protected)

**PATCH** `{{baseUrl}}/api/user/me` — Body: `{ "name"?, "bio"?, "location"?, "profilePhotoUrl"?, "coverPhotoUrl"? }`

### User – Change username (protected)

**PATCH** `{{baseUrl}}/api/user/me/username` — Body: `{ "username": "new_handle" }`. 30-day cooldown between changes.

### User – Public profile

**GET** `{{baseUrl}}/api/user/:username` — Public profile by handle. Old reserved usernames return `redirectToUsername`.

### User – Onboarding (protected)

| Method | URL | Body |
|--------|-----|------|
| PATCH | `/api/user/me/role` | `{ "role": "artist" \| "collector" \| "enthusiast" }` |
| POST | `/api/user/me/onboarding/preferences` | `{ "mediums": [], "styles": [], "themes": [] }` (3+ each) |
| POST | `/api/user/me/onboarding/photos` | `{ "profilePhotoUrl"?, "coverPhotoUrl"? }` or `{ "skip": true }` |
| POST | `/api/user/me/onboarding/complete` | — |

### User – Seller mode (protected)

| Method | URL | Body |
|--------|-----|------|
| POST | `/api/user/me/seller/enable` | `{ "location": "...", "useProfileLocation"?: true }` |
| POST | `/api/user/me/seller/disable` | — (auto-delist for-sale pieces) |
| GET | `/api/user/me/seller` | — |

---

## Media

### Media – Presign upload (protected)

**POST** `{{baseUrl}}/api/media/presign`

```json
{
  "purpose": "profile",
  "contentType": "image/jpeg",
  "pieceId": "optional-uuid-for-piece",
  "postId": "optional-uuid-for-post"
}
```

`purpose`: `profile` | `cover` | `piece` | `post`

**Response:** `{ "presignedPutUrl", "url", "key", "devMode" }` — upload to `presignedPutUrl`, then pass `url` when creating/updating content.

---

## Pieces & posts

Content routes require completed onboarding (`onboardingComplete: true`).

### Pieces

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/pieces` | Bearer | Create piece; sale fields require seller mode |
| GET | `/api/pieces/:id` | — | Detail |
| PATCH | `/api/pieces/:id` | Bearer | Edit, toggle sale |
| GET | `/api/pieces/:id/related-posts` | — | Process posts linked to piece |
| GET | `/api/users/:username/pieces` | — | Profile Work tab |
| GET | `/api/users/:username/pieces/for-sale` | — | For Sale tab |

**Create piece body (example):**

```json
{
  "title": "Sunset Study",
  "mediaUrl": "https://bucket.s3.amazonaws.com/maya_art/pieces/abc.jpg",
  "mediaType": "image",
  "caption": "Oil on canvas",
  "medium": "painting",
  "isForSale": true,
  "priceCents": 25000,
  "dimensions": "24x36 in",
  "shippingRegion": "US"
}
```

### Posts

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/posts` | Bearer | WIP/process only — no sale fields |
| GET | `/api/posts/:id` | — | Detail |
| PATCH | `/api/posts/:id` | Bearer | Edit, link/unlink piece |
| GET | `/api/users/:username/posts` | — | Profile Process tab |

---

## Social

All social mutation routes require Bearer + completed onboarding.

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/users/:username/follow` | Follow user |
| DELETE | `/api/users/:username/follow` | Unfollow |
| POST | `/api/pieces/:id/like` | Like piece |
| DELETE | `/api/pieces/:id/like` | Unlike piece |
| POST | `/api/posts/:id/like` | Like post |
| DELETE | `/api/posts/:id/like` | Unlike post |
| POST | `/api/pieces/:id/save` | Save piece |
| DELETE | `/api/pieces/:id/save` | Unsave piece |
| POST | `/api/posts/:id/save` | Save post |
| DELETE | `/api/posts/:id/save` | Unsave post |
| POST | `/api/pieces/:id/comments` | Body: `{ "body": "..." }` |
| POST | `/api/posts/:id/comments` | Body: `{ "body": "..." }` |

---

## Feeds

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/feed/following` | Bearer + onboarding | Chronological pieces + posts from followed users |
| GET | `/api/feed/explore` | — | Recent public pieces; `?medium=painting` filter |
| GET | `/api/feed/for-you` | Bearer + onboarding | Stub: blends explore (full engine deferred) |

---

## Quick reference

| Method | URL | Auth | Body |
|--------|-----|------|------|
| GET | `{{baseUrl}}/` | — | — |
| GET | `{{baseUrl}}/api/auth/username/check` | Optional | Query: `username`, `for_user_id=me` |
| POST | `{{baseUrl}}/api/auth/otp/generate` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/otp/resend` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/register` | — | `{ "username", "name", "email", "password", "otp" }` |
| POST | `{{baseUrl}}/api/auth/login` | — | `{ "username", "password" }` |
| POST | `{{baseUrl}}/api/auth/refresh` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout-all` | Bearer | — |
| POST | `{{baseUrl}}/api/auth/forget-password` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/reset-password` | — | `{ "token", "newPassword" }` |
| GET | `{{baseUrl}}/api/auth/google` | — | Browser redirect |
| GET | `{{baseUrl}}/api/auth/google/callback` | — | OAuth callback |
| GET | `{{baseUrl}}/api/user/me` | Bearer | — |
| PATCH | `{{baseUrl}}/api/user/me` | Bearer | Profile fields |
| PATCH | `{{baseUrl}}/api/user/me/username` | Bearer | `{ "username" }` |
| GET | `{{baseUrl}}/api/user/:username` | — | — |
| PATCH | `{{baseUrl}}/api/user/me/role` | Bearer | `{ "role" }` |
| POST | `{{baseUrl}}/api/user/me/onboarding/*` | Bearer | See above |
| POST | `{{baseUrl}}/api/user/me/seller/*` | Bearer | See above |
| POST | `{{baseUrl}}/api/media/presign` | Bearer | `{ "purpose", "contentType" }` |
| POST/PATCH/GET | `{{baseUrl}}/api/pieces/*` | Varies | See above |
| POST/PATCH/GET | `{{baseUrl}}/api/posts/*` | Varies | See above |
| GET | `{{baseUrl}}/api/users/:username/pieces` | — | — |
| GET | `{{baseUrl}}/api/users/:username/posts` | — | — |
| POST/DELETE | `{{baseUrl}}/api/users/:username/follow` | Bearer | — |
| POST/DELETE | `{{baseUrl}}/api/pieces/:id/like` | Bearer | — |
| GET | `{{baseUrl}}/api/feed/following` | Bearer | — |
| GET | `{{baseUrl}}/api/feed/explore` | — | — |


**Auth column:** “Bearer” = `Authorization: Bearer {{accessToken}}`; “Cookie” = send cookies (Postman does this automatically after login/register/refresh).
