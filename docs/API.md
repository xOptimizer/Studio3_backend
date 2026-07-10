# API Documentation (Postman-ready)

For the **Studiothree Discover** backend. Use this doc to build and test requests in Postman and to integrate from mobile (iOS/Android) or web clients.

**Terminology:** UI **Scenes** map to the API `posts` resource (`/api/posts`, feed `type: "post"`, presign `purpose: "post"`).

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
  "otp": "123456",
  "phone": "+12145551234"
}
```

`phone` is optional.

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
      "phone": "+12145551234",
      "emailVerified": true,
      "onboardingComplete": false,
      "role": null,
      "sellerEnabled": false,
      "followersCount": 0,
      "followingCount": 0,
      "piecesCount": 0,
      "savesCount": 0,
      "collectedCount": 0,
      "isFollowing": false,
      "savedPieces": []
    }
  }
}
```

`phone` is optional in the request body and stored but not required — older clients that omit it still work. The `user` object also includes legacy alias keys the Flutter client's fallback parser accepts: `following`, `followers`, `pieces`, `saves`, `collected`, `isSeller`, `saved` (mirrors `followingCount`, `followersCount`, `piecesCount`, `savesCount`, `collectedCount`, `sellerEnabled`, `savedPieces` respectively). `collectedCount`/`collected` are always `0` — there is no Orders domain yet to compute real purchase counts.

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

The `username` field accepts **username or email**.

```json
{
  "username": "maya_art",
  "password": "securePassword123"
}
```

Email example:

```json
{
  "username": "maya@example.com",
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
    "user": { "username": "maya_art", "name": "John Doe", "email": "user@example.com", "role": null, "...": "same shape as Register/Login" }
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

## User & profile

### User – Get me (protected)

**GET** `{{baseUrl}}/api/user/me` — Bearer required. Returns full profile: `username`, `name`, `email`, `phone`, `bio`, `location`, `profilePhotoUrl`, `coverPhotoUrl`, `role`, `sellerEnabled`, `onboardingComplete`, `emailVerified`, `canChangeUsername`, `tastePreferences`, `lastUsernameChangeAt`, plus counts (`followersCount`, `followingCount`, `piecesCount`, `savesCount`, `collectedCount`), `isFollowing` (always `false` for self), and `savedPieces` (first 20, enriched piece objects — see the Pieces section below). Also includes legacy alias keys `following`/`followers`/`pieces`/`saves`/`collected`/`isSeller`/`saved` for backward-compatible client parsing.

### User – Update me (protected)

**PATCH** `{{baseUrl}}/api/user/me` — Body: `{ "name"?, "bio"?, "location"?, "profilePhotoUrl"?, "coverPhotoUrl"? }`

### User – Change username (protected)

**PATCH** `{{baseUrl}}/api/user/me/username` — Body: `{ "username": "new_handle" }`. 30-day cooldown between changes.

### User – Public profile

**GET** `{{baseUrl}}/api/user/:username` — Public profile by handle. Optional Bearer token: when present, `isFollowing` reflects whether the caller follows this user; omitted/anonymous requests get `isFollowing: false`. Old reserved usernames return `redirectToUsername`. Does not include private fields (`email`, `phone`, `tastePreferences`, `savedPieces`, etc.) — only the public subset plus counts/`isFollowing`.

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

### User – Seller analytics (protected)

**GET** `{{baseUrl}}/api/user/me/seller/analytics`

```json
{
  "data": {
    "savesCount": 42,
    "likesCount": 128,
    "inquiriesCount": null,
    "salesCount": null,
    "period": "all_time"
  }
}
```

`savesCount`/`likesCount` aggregate across all of the caller's pieces. `salesCount`/`inquiriesCount` are always `null` — there is no Orders or Inquiries domain yet, so these are intentionally not fabricated as `0`.

### User – Saved pieces (protected)

**GET** `{{baseUrl}}/api/user/me/saved/pieces` — Pieces the current user has saved, each enriched the same way as `GET /api/pieces/:id` below (`author`, `series`, `relatedPosts`, `likeCount`, `commentCount`, `isLiked`, `isSaved`).

### User – Saved scenes (protected)

**GET** `{{baseUrl}}/api/user/me/saved/posts` — Scenes the current user has saved, each enriched the same way as `GET /api/posts/:id` below.

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

`purpose`: `profile` | `cover` | `piece` | `post`. `contentType`: `image/jpeg`, `image/png`, `image/webp` (max 20MB), or `video/mp4` (max 100MB) — video is supported for any purpose today.

**Response:** `{ "presignedPutUrl", "url", "key", "devMode" }` — upload to `presignedPutUrl`, then pass `url` when creating/updating content. `devMode: true` when S3 isn't configured (local dev) — `presignedPutUrl` is `null` and `url` is a placeholder.

---

## Pieces & scenes

Create/edit routes require completed onboarding (`onboardingComplete: true`). Detail (`GET /:id`) routes accept an **optional** Bearer token (`optional_auth`) — send one to get viewer-specific `isLiked`/`isSaved`/`author.isFollowing`; omit it for anonymous access (those fields default to `false`).

UI **Scenes** map to the API `posts` resource (see product terminology in Content Model & Posting Workflow).

### Pieces

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/pieces` | Bearer | Create piece; sale fields require seller mode |
| GET | `/api/pieces/:id` | Optional Bearer | Enriched detail |
| PATCH | `/api/pieces/:id` | Bearer | Edit, toggle sale |
| GET | `/api/pieces/:id/related-posts` | — | Scenes linked to piece |
| GET | `/api/pieces/:id/comments` | — | Cursor-paginated comment thread |
| GET | `/api/users/:username/pieces` | — | Profile Work tab |
| GET | `/api/users/:username/pieces/for-sale` | — | For Sale tab |
| GET | `/api/user/me/saved/pieces` | Bearer | Pieces the caller has saved (see User & profile section above) |

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
  "shippingRegion": "US",
  "yearCreated": 2024,
  "framingMounting": "Framed, ready to hang",
  "provenance": "Direct from artist",
  "handlingNotes": "Keep away from direct sunlight"
}
```

`yearCreated`, `framingMounting`, `provenance`, `handlingNotes` are optional first-class fields (replace the old caption-JSON workaround). All of `materials[]`, `styleTags[]`, `aiDisclosed`, `altText` are also accepted on create and are returned on every piece response. `PATCH` accepts the same field set (plus `status`) for editing.

**Get piece response** (`GET /api/pieces/:id`) — every piece field above, plus:

```json
{
  "data": {
    "...": "all Create Piece fields, plus:",
    "status": "live",
    "createdAt": "2026-07-08T12:00:00Z",
    "author": {
      "username": "maya_art",
      "name": "Maya",
      "profilePhotoUrl": "https://...",
      "isFollowing": false
    },
    "likeCount": 12,
    "commentCount": 3,
    "isLiked": false,
    "isSaved": false,
    "series": {
      "id": "uuid",
      "name": "Riverwalk Dream",
      "pieceCount": 3,
      "previewPieces": [{ "id": "...", "mediaUrl": "...", "title": "..." }],
      "pieceIds": ["...", "...", "..."]
    },
    "relatedPosts": []
  }
}
```

`series` is `null` if the piece doesn't belong to one. `GET /api/user/me/saved/pieces` and `GET /api/users/:username/pieces` / `.../pieces/for-sale` return arrays of this same enriched shape (list endpoints under `/api/users/:username/*` are unauthenticated, so `isLiked`/`isSaved`/`author.isFollowing` are always `false` there).

### Scenes (API: posts)

UI **Scenes** map to the `posts` resource. Scenes may be **image** or **video** (`mediaType`). They are not collectible.

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/posts` | Bearer | Create scene (image or video); no sale fields |
| GET | `/api/posts/:id` | Optional Bearer | Enriched detail |
| PATCH | `/api/posts/:id` | Bearer | Edit, link/unlink piece |
| GET | `/api/posts/:id/comments` | — | Cursor-paginated comment thread |
| GET | `/api/users/:username/posts` | — | Profile **Scenes** tab |
| GET | `/api/user/me/saved/posts` | Bearer | Saved scenes |

**Create scene (image):** `{ "mediaUrl", "mediaType": "image", "caption"? }`

**Create scene (video):** `{ "mediaUrl", "mediaType": "video", "caption"? }`

`mediaType` must be `image` or `video`. `isProcess` defaults to `false` when omitted.

**Get scene response** (`GET /api/posts/:id`) — base fields (`id`, `userId`, `mediaUrl`, `mediaType`, `caption`, `isProcess`, `linkedPieceId`, `status`, `createdAt`) plus enrichment: `author`, `likeCount`, `commentCount`, `isLiked`, `isSaved`, and `piece` (linked piece when set).

---

## Social

Like/save/comment-create/follow mutation routes require Bearer + completed onboarding. Comment **reads** are public (no auth).

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/users/:username/follow` | Follow user |
| DELETE | `/api/users/:username/follow` | Unfollow |
| POST | `/api/pieces/:id/like` | Like piece |
| DELETE | `/api/pieces/:id/like` | Unlike piece |
| POST | `/api/posts/:id/like` | Like scene |
| DELETE | `/api/posts/:id/like` | Unlike scene |
| POST | `/api/pieces/:id/save` | Save piece |
| DELETE | `/api/pieces/:id/save` | Unsave piece |
| POST | `/api/posts/:id/save` | Save scene |
| DELETE | `/api/posts/:id/save` | Unsave scene |
| POST | `/api/pieces/:id/comments` | Body: `{ "body": "..." }` |
| POST | `/api/posts/:id/comments` | Body: `{ "body": "..." }` |
| GET | `/api/pieces/:id/comments` | Query: `cursor?`, `limit?` (default 50, max 100) |
| GET | `/api/posts/:id/comments` | Query: `cursor?`, `limit?` (default 50, max 100) |

**Get comments response:**

```json
{
  "data": {
    "items": [
      {
        "id": "uuid",
        "body": "Beautiful work!",
        "author": { "username": "alex_chen", "name": "Alex Chen", "profilePhotoUrl": "https://..." },
        "createdAt": "2026-07-08T12:00:00Z"
      }
    ],
    "nextCursor": "2026-07-08T11:00:00+00:00"
  }
}
```

Pass `nextCursor` back as `?cursor=` to fetch the next (older) page. `nextCursor` is `null` when there are no more comments.

---

## Feeds

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| GET | `/api/feed/following` | Bearer + onboarding | Chronological pieces + scenes from followed users |
| GET | `/api/feed/explore` | Optional Bearer | Recent public pieces + scenes; `?medium=painting` filters pieces; `?medium=video` returns video scenes |
| GET | `/api/feed/for-you` | Bearer + onboarding | Stub: wraps explore (full personalization engine deferred) |

All three are cursor-paginated: query params `?cursor=` and `?limit=` (default 20, max 50). Response:

```json
{
  "data": {
    "items": [
      {
        "type": "piece",
        "...": "full enriched piece or scene fields (author, likeCount, isLiked, isSaved)"
      }
    ],
    "nextCursor": "<opaque-cursor-string-or-null>"
  }
}
```

`type` is `"piece"` or `"post"`. Pass `nextCursor` back as `?cursor=` for the next page; `null` means no more items. Default `explore` returns **pieces and scenes** merged by recency. `?medium=video` returns video scenes only. Anonymous requests to `explore` get `isLiked`/`isSaved`/`author.isFollowing` defaulted to `false`; send a Bearer token for viewer-specific values.

---

## Series

Piece grouping for an artist's profile "Series" tab. Mutation routes require Bearer + completed onboarding; reads are public. A piece belongs to at most one series — adding it to a second series is rejected with `400`.

| Method | URL | Auth | Body |
|--------|-----|------|------|
| GET | `/api/users/:username/series` | — | — (only series with `pieceCount > 1` are returned) |
| GET | `/api/series/:id` | — | — |
| POST | `/api/series` | Bearer | `{ "name": "...", "pieceIds"?: ["..."] }` |
| PATCH | `/api/series/:id` | Bearer | `{ "name"?: "...", "pieceOrder"?: ["pieceId", ...] }` |
| POST | `/api/series/:id/pieces` | Bearer | `{ "pieceId": "..." }` |
| DELETE | `/api/series/:id/pieces/:pieceId` | Bearer | — |

**Series object** (list — `GET /api/users/:username/series`):

```json
{ "id": "uuid", "name": "Riverwalk Dream", "pieceCount": 3, "previewPieces": [{ "id": "...", "mediaUrl": "...", "title": "..." }] }
```

**Series detail** (`GET /api/series/:id`, and `create`/`patch`/`add-piece`/`remove-piece` responses) — same shape plus `pieceIds: ["...", "...", "..."]` (full ordered list, matches the `series` field embedded in piece detail).

---

## Quick reference

| Method | URL | Auth | Body |
|--------|-----|------|------|
| GET | `{{baseUrl}}/` | — | — |
| GET | `{{baseUrl}}/api/auth/username/check` | Optional | Query: `username`, `for_user_id=me` |
| POST | `{{baseUrl}}/api/auth/otp/generate` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/otp/resend` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/register` | — | `{ "username", "name", "email", "password", "otp" }` |
| POST | `{{baseUrl}}/api/auth/login` | — | `{ "username", "password" }` — `username` is username or email |
| POST | `{{baseUrl}}/api/auth/refresh` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout-all` | Bearer | — |
| POST | `{{baseUrl}}/api/auth/forget-password` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/reset-password` | — | `{ "token", "newPassword" }` |
| GET | `{{baseUrl}}/api/user/me` | Bearer | — |
| PATCH | `{{baseUrl}}/api/user/me` | Bearer | Profile fields |
| PATCH | `{{baseUrl}}/api/user/me/username` | Bearer | `{ "username" }` |
| GET | `{{baseUrl}}/api/user/:username` | Optional Bearer | — |
| PATCH | `{{baseUrl}}/api/user/me/role` | Bearer | `{ "role" }` |
| POST | `{{baseUrl}}/api/user/me/onboarding/*` | Bearer | See above |
| POST | `{{baseUrl}}/api/user/me/seller/*` | Bearer | See above |
| GET | `{{baseUrl}}/api/user/me/seller/analytics` | Bearer | — |
| GET | `{{baseUrl}}/api/user/me/saved/pieces` | Bearer | — |
| GET | `{{baseUrl}}/api/user/me/saved/posts` | Bearer | Saved scenes |
| POST | `{{baseUrl}}/api/media/presign` | Bearer | `{ "purpose", "contentType" }` |
| POST/PATCH/GET | `{{baseUrl}}/api/pieces/*` | Varies | See above |
| GET | `{{baseUrl}}/api/pieces/:id/comments` | — | Query: `cursor?`, `limit?` |
| POST/PATCH/GET | `{{baseUrl}}/api/posts/*` | Varies | See above |
| GET | `{{baseUrl}}/api/posts/:id/comments` | — | Query: `cursor?`, `limit?` |
| GET | `{{baseUrl}}/api/users/:username/pieces` | — | — |
| GET | `{{baseUrl}}/api/users/:username/posts` | — | Profile Scenes tab |
| GET | `{{baseUrl}}/api/users/:username/series` | — | — |
| POST/PATCH/GET/DELETE | `{{baseUrl}}/api/series/*` | Varies | See above |
| POST/DELETE | `{{baseUrl}}/api/users/:username/follow` | Bearer | — |
| POST/DELETE | `{{baseUrl}}/api/pieces/:id/like` | Bearer | — |
| GET | `{{baseUrl}}/api/feed/following` | Bearer | Query: `cursor?`, `limit?` |
| GET | `{{baseUrl}}/api/feed/explore` | Optional Bearer | Query: `medium?`, `cursor?`, `limit?` |
| GET | `{{baseUrl}}/api/feed/for-you` | Bearer | Query: `cursor?`, `limit?` |


**Auth column:** “Bearer” = `Authorization: Bearer {{accessToken}}` required; “Optional Bearer” = works without a token but returns viewer-specific fields (`isLiked`/`isSaved`/`isFollowing`) when one is sent; “Cookie” = send cookies (Postman does this automatically after login/register/refresh).
