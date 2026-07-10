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

- **Refresh:** Send a **POST** to `/api/auth/refresh` with no body and no auth header. If you previously called Login/Register from the same Postman session, the `refreshToken` cookie will be sent and you'll get a new `accessToken` (and new cookie).
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

Common status codes: `200`/`201` success, `400` bad request, `401` unauthorized, `403` forbidden, `404` not found, `409` conflict, `429` too many requests, `500` server error, `501` not implemented (payment provider).

**Protected routes:** Send header:

```http
Authorization: Bearer {{accessToken}}
```

**Optional-auth routes:** work without a token, but return viewer-specific fields (`isLiked`/`isSaved`/`isFollowing`) when a valid token is sent.

---

## Endpoints (copy into Postman)

### Health

**GET** `{{baseUrl}}/` → `{ "message": "Studiothree Discover API running" }`

---

### Auth – OTP generate / resend

**POST** `{{baseUrl}}/api/auth/otp/generate` and `{{baseUrl}}/api/auth/otp/resend` — body `{ "email" }`. `429` if rate/resend limit exceeded.

### Auth – Username check

**GET** `{{baseUrl}}/api/auth/username/check?username=maya_art&for_user_id=me` — `for_user_id=me` (optional, requires Bearer) excludes the current user when changing username.

```json
{ "data": { "available": true, "normalized": "maya_art", "reason": null, "message": "Username is available.", "suggestions": [] } }
```

### Auth – Register

**POST** `{{baseUrl}}/api/auth/register`

```json
{ "username": "maya_art", "name": "John Doe", "email": "user@example.com", "password": "securePassword123", "otp": "123456", "phone": "+12145551234" }
```

`phone` is optional (stored but not required — older clients omitting it still work). Sets cookie `refreshToken`. Response:

```json
{
  "data": {
    "accessToken": "eyJ...",
    "user": {
      "username": "maya_art", "name": "John Doe", "email": "user@example.com", "phone": "+12145551234",
      "emailVerified": true, "onboardingComplete": false, "role": null, "sellerEnabled": false,
      "followersCount": 0, "followingCount": 0, "piecesCount": 0, "savesCount": 0, "collectedCount": 0,
      "isFollowing": false, "savedPieces": []
    }
  }
}
```

`collectedCount` is the number of pieces this user has successfully bought (orders in `paid`/`shipped`/`completed` status — see [Orders](#orders--checkout--addresses)); `pending_payment`/`cancelled` orders don't count. The `user` object also includes legacy alias keys the client's fallback parser accepts: `following`, `followers`, `pieces`, `saves`, `collected`, `isSeller`, `saved` (mirroring the canonical keys). Errors: `400` (validation/invalid OTP), `409` (username/email taken).

### Auth – Login

**POST** `{{baseUrl}}/api/auth/login`

```json
{ "username": "maya_art", "password": "securePassword123" }
```

The `username` field accepts **either a username or an email address** (detected by the presence of `@`). Example with email:

```json
{ "username": "maya@example.com", "password": "securePassword123" }
```

Same response shape as Register. Errors: `400` (missing fields), `401` (invalid credentials).

### Auth – Refresh / Logout / Logout-all

- **POST** `/api/auth/refresh` — cookie only, no body. Returns new `accessToken` + refresh cookie. `401` if cookie missing/invalid/expired.
- **POST** `/api/auth/logout` — cookie only. Clears refresh cookie.
- **POST** `/api/auth/logout-all` — Bearer required. Revokes all sessions. `401` if not authenticated.

### Auth – Forget / Reset password

- **POST** `/api/auth/forget-password` — `{ "email" }`.
- **POST** `/api/auth/reset-password` — `{ "token", "newPassword" }`. `400` if token invalid/expired or `newPassword` missing.

---

## User & profile

### Get me / Update me (protected)

**GET** `{{baseUrl}}/api/user/me` — Bearer required. Full profile: `username`, `name`, `email`, `phone`, `bio`, `location`, `profilePhotoUrl`, `coverPhotoUrl`, `role`, `sellerEnabled`, `onboardingComplete`, `emailVerified`, `canChangeUsername`, `tastePreferences`, `lastUsernameChangeAt`, counts (`followersCount`/`followingCount`/`piecesCount`/`savesCount`/`collectedCount`), `isFollowing` (always `false` for self), `savedPieces` (first 20, enriched — see [Pieces](#pieces)). Also includes the legacy alias keys `following`/`followers`/`pieces`/`saves`/`collected`/`isSeller`/`saved` for backward-compatible client parsing.

**PATCH** `{{baseUrl}}/api/user/me` — body: `{ "name"?, "bio"?, "location"?, "profilePhotoUrl"?, "coverPhotoUrl"?, "latitude"?, "longitude"? }`. `latitude`/`longitude` are optional — both-or-neither (400 if only one is sent); used for [seller "near me" discovery](#geo-near-me-discovery).

### Change username / Public profile

- **PATCH** `/api/user/me/username` — `{ "username" }`. 30-day cooldown between changes.
- **GET** `/api/user/:username` — Optional Bearer (populates `isFollowing`; omitted/anonymous gets `isFollowing: false`). Public subset only (no `email`/`phone`/`tastePreferences`/`savedPieces`). Supports `redirectToUsername` for renamed handles.

### Onboarding (protected)

| Method | URL | Body |
|--------|-----|------|
| PATCH | `/api/user/me/role` | `{ "role": "artist" \| "collector" \| "enthusiast" }` |
| POST | `/api/user/me/onboarding/preferences` | `{ "mediums": [], "styles": [], "themes": [] }` (3+ each) |
| POST | `/api/user/me/onboarding/photos` | `{ "profilePhotoUrl"?, "coverPhotoUrl"? }` or `{ "skip": true }` |
| POST | `/api/user/me/onboarding/complete` | — |

### Seller mode & analytics (protected)

| Method | URL | Body |
|--------|-----|------|
| POST | `/api/user/me/seller/enable` | `{ "location", "useProfileLocation"?: true }` |
| POST | `/api/user/me/seller/disable` | — (auto-delists for-sale pieces) |
| GET | `/api/user/me/seller` | — |
| GET | `/api/user/me/seller/analytics` | — |

**Seller analytics response:**
```json
{ "data": { "savesCount": 42, "likesCount": 128, "inquiriesCount": 7, "salesCount": 3, "period": "all_time" } }
```
`savesCount`/`likesCount` aggregate across all of the caller's pieces. `inquiriesCount` is the number of inquiry threads received (see [Inquiries](#inquiries)). `salesCount` is the number of completed sales (orders in `paid`/`shipped`/`completed` status, see [Orders](#orders--checkout--addresses)).

### Saved pieces / Saved scenes (protected)

- **GET** `{{baseUrl}}/api/user/me/saved/pieces` — pieces the caller has saved, each enriched like `GET /api/pieces/:id`.
- **GET** `{{baseUrl}}/api/user/me/saved/posts` — scenes the caller has saved, each enriched like `GET /api/posts/:id`.

### Devices (push notifications, protected)

- **POST** `{{baseUrl}}/api/user/me/devices` — body `{ "platform": "ios"|"android"|"web", "pushToken": "..." }`. Upserts by token — a token belongs to one app install, so registering it under a new user reassigns it (handles device-sharing/logout-login).
- **DELETE** `{{baseUrl}}/api/user/me/devices` — body `{ "pushToken" }`. Deletes the token registration (call on logout).

### Addresses (protected)

Saved shipping address book (Zomato/Swiggy-style — multiple labeled addresses, map-pick lat/lng + full manual entry; the backend never geocodes, the client resolves the address and sends it fully formed).

| Method | URL | Body |
|--------|-----|------|
| GET | `/api/user/me/addresses` | — (sorted default-first, then newest) |
| POST | `/api/user/me/addresses` | see below |
| PATCH | `/api/user/me/addresses/:id` | any subset of the same fields |
| DELETE | `/api/user/me/addresses/:id` | — |
| POST | `/api/user/me/addresses/:id/default` | — (unsets any prior default) |

**Create/update body:**
```json
{
  "label": "Home", "firstName": "Jane", "lastName": "Doe", "phone": "+12145551234",
  "line1": "123 Main St", "line2": "Apt 4B", "city": "Dallas", "state": "TX", "zip": "75201",
  "country": "US", "latitude": 32.7767, "longitude": -96.7970, "isDefault": true
}
```
`firstName`, `lastName`, `phone`, `line1`, `city`, `state`, `zip` are required on create. The first address a user saves is automatically made default.

### Geo "near me" discovery

**GET** `{{baseUrl}}/api/users/nearby?lat=32.78&lng=-96.80&radiusKm=50&limit=20` — Optional Bearer. Returns sellers (`sellerEnabled: true` with lat/lng set) near the given point, ordered by distance:

```json
{ "data": { "items": [{ "...": "same shape as user_to_dict", "distanceKm": 4.2 }] } }
```

Distance computed via the haversine formula in raw SQL (no PostGIS on this Postgres instance) — a full-table scan per call, fine at hundreds/low-thousands of sellers. `radiusKm` defaults to 50, `limit` defaults to 20 (max 50).

---

## Media

**POST** `{{baseUrl}}/api/media/presign` (Bearer)

```json
{ "purpose": "profile" | "cover" | "piece" | "post", "contentType": "image/jpeg", "pieceId": "optional", "postId": "optional" }
```

`contentType`: `image/jpeg`, `image/png`, `image/webp` (max 20MB), or `video/mp4` (max 100MB) — video is supported for any purpose. Response: `{ "presignedPutUrl", "url", "key", "devMode" }` — upload to `presignedPutUrl`, then pass `url` when creating/updating content. `devMode: true` when S3 isn't configured (local dev) — `presignedPutUrl` is `null` and `url` is a placeholder.

---

## Pieces & Scenes

Create/edit routes require completed onboarding (`onboardingComplete: true`). Detail (`GET /:id`) routes accept an **optional** Bearer token (`optional_auth`) — send one for viewer-specific `isLiked`/`isSaved`/`author.isFollowing`; omit for anonymous (those fields default to `false`).

### Pieces

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/pieces` | Bearer | Create; sale fields require seller mode |
| GET | `/api/pieces/:id` | Optional Bearer | Enriched detail |
| PATCH | `/api/pieces/:id` | Bearer | Edit, toggle sale |
| GET | `/api/pieces/:id/related-posts` | — | Scenes linked to piece |
| GET | `/api/pieces/:id/comments` | — | Cursor-paginated comment thread |
| GET | `/api/pieces/:id/shipping-quote` | Optional Bearer | See [Orders](#orders--checkout--addresses) |
| POST | `/api/pieces/:id/collect` | Bearer + onboarding | Checkout — see [Orders](#orders--checkout--addresses) |
| GET | `/api/users/:username/pieces` | — | Profile Work tab |
| GET | `/api/users/:username/pieces/for-sale` | — | For Sale tab |
| GET | `/api/user/me/saved/pieces` | Bearer | See [User](#saved-pieces--saved-scenes-protected) |

**Create piece body:**
```json
{
  "title": "Sunset Study", "mediaUrl": "https://.../abc.jpg", "mediaType": "image",
  "caption": "Oil on canvas", "medium": "painting", "isForSale": true, "priceCents": 25000,
  "dimensions": "24x36 in", "shippingRegion": "US",
  "yearCreated": 2024, "framingMounting": "Framed, ready to hang", "provenance": "Direct from artist",
  "handlingNotes": "Keep away from direct sunlight", "materials": ["oil", "canvas"], "styleTags": ["abstract"]
}
```
`yearCreated`/`framingMounting`/`provenance`/`handlingNotes` are first-class optional fields (replace the old caption-JSON workaround). `materials[]`/`styleTags[]`/`aiDisclosed`/`altText` are also accepted on create and returned on every piece response. `PATCH` accepts the same field set plus `status` (`draft|live|sold|delisted|reserved` — `reserved`/`sold` are set automatically by checkout, not client-settable in normal use).

**Get piece response** (`GET /api/pieces/:id`) — all create fields plus:
```json
{
  "status": "live", "createdAt": "...",
  "author": { "username": "maya_art", "name": "Maya", "profilePhotoUrl": "...", "isFollowing": false },
  "likeCount": 12, "commentCount": 3, "isLiked": false, "isSaved": false,
  "series": { "id": "...", "name": "Riverwalk Dream", "pieceCount": 3, "previewPieces": [...], "pieceIds": [...] },
  "relatedPosts": []
}
```
`series` is `null` if the piece doesn't belong to one. `GET /api/user/me/saved/pieces` and `GET /api/users/:username/pieces` / `.../pieces/for-sale` return arrays of this same enriched shape (list endpoints under `/api/users/:username/*` are unauthenticated, so `isLiked`/`isSaved`/`author.isFollowing` are always `false` there).

### Scenes (API: posts)

UI **Scenes** map to the `posts` resource. Scenes may be **image** or **video** (`mediaType`) and are not collectible (no sale fields).

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/posts` | Bearer | Create scene (image or video) |
| GET | `/api/posts/:id` | Optional Bearer | Enriched detail |
| PATCH | `/api/posts/:id` | Bearer | Edit, link/unlink piece |
| GET | `/api/posts/:id/comments` | — | Cursor-paginated comment thread |
| GET | `/api/users/:username/posts` | — | Profile **Scenes** tab |
| GET | `/api/user/me/saved/posts` | Bearer | Saved scenes |

**Create scene body:** `{ "mediaUrl", "mediaType": "image"|"video", "caption"?, "linkedPieceId"? }` — `mediaType` must be `image` or `video`; `isProcess` defaults to `false` when omitted.

**Get scene response** (`GET /api/posts/:id`) — base fields (`id`, `userId`, `mediaUrl`, `mediaType`, `caption`, `isProcess`, `linkedPieceId`, `status`, `createdAt`) plus enrichment: `author`, `likeCount`, `commentCount`, `isLiked`, `isSaved`, and `piece` (full linked piece, or `null`).

---

## Social

Like/save/comment-create/follow mutation routes require Bearer + completed onboarding. Comment **reads** are public (no auth).

| Method | URL | Notes |
|--------|-----|-------|
| POST/DELETE | `/api/users/:username/follow` | Follow/unfollow |
| POST/DELETE | `/api/pieces/:id/like`, `/api/posts/:id/like` | Like/unlike piece or scene |
| POST/DELETE | `/api/pieces/:id/save`, `/api/posts/:id/save` | Save/unsave piece or scene |
| POST | `/api/pieces/:id/comments`, `/api/posts/:id/comments` | `{ "body" }` |
| GET | `/api/pieces/:id/comments`, `/api/posts/:id/comments` | Query: `cursor?`, `limit?` (default 50, max 100) |

**Get comments response:**
```json
{
  "data": {
    "items": [
      { "id": "uuid", "body": "Beautiful work!", "author": { "username": "alex_chen", "name": "Alex Chen", "profilePhotoUrl": "https://..." }, "createdAt": "2026-07-08T12:00:00Z" }
    ],
    "nextCursor": "2026-07-08T11:00:00+00:00"
  }
}
```
Pass `nextCursor` back as `?cursor=` to fetch the next (older) page; `null` when there are no more comments.

Follow/like/save/comment each emit a [notification](#notifications) (with push) to the target's owner — skipped for self-actions.

---

## Feeds

| Method | URL | Auth | Description |
|--------|-----|------|--------------|
| GET | `/api/feed/following` | Bearer + onboarding | Chronological pieces + scenes from followed users |
| GET | `/api/feed/explore` | Optional Bearer | Recent public pieces + scenes; `?medium=painting` filters pieces by medium; `?medium=video` returns video scenes only |
| GET | `/api/feed/for-you` | Bearer + onboarding | Stub wrapping explore (full personalization engine deferred) |

All three are cursor-paginated: `?cursor=&limit=` (default 20, max 50). Response:
```json
{ "data": { "items": [{ "type": "piece"|"post", "...": "full enriched piece or scene fields (author, likeCount, isLiked, isSaved)" }], "nextCursor": "<opaque-cursor-string-or-null>" } }
```
`type` is `"piece"` or `"post"`. Default `explore` (no `medium`) returns pieces and scenes merged by recency; `?medium=<piece medium>` returns pieces of that medium only; `?medium=video` returns video scenes only. Pass `nextCursor` back as `?cursor=` for the next page; `null` means no more items. Anonymous requests get `isLiked`/`isSaved`/`author.isFollowing` defaulted to `false`; send a Bearer token for viewer-specific values.

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

## Notifications

General activity feed. Every entry may also trigger a push via [Devices](#devices-push-notifications-protected) (Firebase Cloud Messaging — iOS/Android/Web, sent synchronously, fails open/logs if unconfigured — never blocks the triggering action).

| Method | URL | Notes |
|--------|-----|-------|
| GET | `/api/notifications` | Bearer. Cursor-paginated (`?cursor=&limit=`, default 20 max 50) |
| PATCH | `/api/notifications/:id/read` | Bearer |
| POST | `/api/notifications/read-all` | Bearer |
| GET | `/api/notifications/unread-count` | Bearer → `{ "count": N }` |

**List response:**
```json
{
  "data": {
    "items": [{
      "id": "uuid", "type": "save"|"follow"|"inquiry"|"purchase"|"like"|"comment",
      "actor": { "username", "name", "profilePhotoUrl" },
      "target": { "type": "piece"|"post"|"order"|"inquiry"|"user", "id": "uuid" },
      "payload": { "...": "type-specific pre-rendered fields" },
      "message": "saved your piece", "read": false, "createdAt": "..."
    }],
    "nextCursor": "..."
  }
}
```

Emitted automatically by: follow, like, save, comment (see [Social](#social)), new inquiry message (see [Inquiries](#inquiries)), and order confirmation (see [Orders](#orders--checkout--addresses)).

---

## Inquiries

Structured, **piece-scoped** chat — a buyer asks about a specific piece, the seller replies. Not open/general DMs. Mutations require Bearer + onboarding; reads require Bearer (participant-only).

| Method | URL | Body |
|--------|-----|------|
| GET | `/api/inquiries` | — Inbox, cursor-paginated by last activity |
| GET | `/api/inquiries/:id` | — Thread + messages; auto-marks caller's read state |
| POST | `/api/inquiries` | `{ "pieceId", "message" }` |
| POST | `/api/inquiries/:id/messages` | `{ "body" }` |
| PATCH | `/api/inquiries/:id/read` | — Explicit mark-read (in addition to auto-mark on GET) |

**Inbox item:**
```json
{ "id", "piece": {"id","title","thumbnailUrl"}, "otherParty": {...}, "preview": "...", "updatedAt": "...", "unread": true, "status": "open" }
```

**`POST /api/inquiries`:** 400 if inquiring on your own piece. If an open thread already exists for this buyer+piece, returns the **existing** thread with `200` (`{"id", "reused": true}`) instead of erroring — otherwise creates one and returns `201` (`{"id", "reused": false}`). Every new message notifies the other participant (push included).

---

## Orders / Checkout / Addresses

Full checkout lifecycle **except real payment capture** — the client is still finalizing a payment gateway. See [Addresses](#addresses-protected) for the address book used at checkout.

### Shipping quote

**GET** `{{baseUrl}}/api/pieces/:id/shipping-quote` — Optional Bearer.
```json
{ "data": { "methods": [{"id":"standard","cents":500},{"id":"express","cents":1500},{"id":"overnight","cents":3500},{"id":"free","cents":0}] } }
```
Flat global rates — no carrier integration.

### Checkout (collect)

**POST** `{{baseUrl}}/api/pieces/:id/collect` — Bearer + onboarding. Body: `{ "addressId", "shippingMethod" }`.

Validates the piece is for-sale and `status == "live"` (else `409`), the caller isn't the seller (`400`), the address belongs to the caller (`404`), and the method is valid (`400`). Computes `artworkCents`/`shippingCents`/`taxCents` (flat 8.25% placeholder, server-side)/`totalCents`, creates the order, snapshots the chosen address (edits to the saved address later never change this), and reserves the piece (`status → "reserved"`, so it disappears from sale listings immediately). Response:
```json
{ "data": { "id", "status": "pending_payment", "artworkCents", "shippingCents", "taxCents", "totalCents", "shippingAddress": {...}, "items": [...], "clientSecret": null } }
```
`clientSecret` is a contract-stable placeholder — `null` today, populated once a real payment provider is wired up.

### Confirm (pay)

**POST** `{{baseUrl}}/api/orders/:id/confirm` — Bearer, caller must be the buyer, `409` unless the order is `pending_payment`.

**No payment provider configured (current default):** auto-succeeds — order → `paid`, piece → `sold`, both buyer and seller are notified (`type: "purchase"`). Response includes `"devMode": true`.

**Provider key present (not yet built):** `501 Payment provider not yet implemented.` — this is an intentional seam, not a bug; real Stripe integration lands in a future pass.

### Order management

| Method | URL | Notes |
|--------|-----|-------|
| GET | `/api/orders/:id` | Buyer or seller only |
| PATCH | `/api/orders/:id` | `{"status": "shipped"\|"completed"\|"cancelled"}` — seller-only for `shipped`/`completed` (strict forward order from `paid`), buyer-or-seller for `cancelled` (from `pending_payment`/`paid`, releases the piece back to `"live"`) |
| GET | `/api/user/me/orders` | Buyer history, cursor-paginated |
| GET | `/api/user/me/sales` | Seller history, cursor-paginated |

**Order object** (all of the above): `{ id, buyerId, sellerId, status, shippingMethod, shippingAddress, artworkCents, shippingCents, taxCents, totalCents, paymentProvider, items: [{pieceId, priceCents, quantity}], createdAt, updatedAt }`.

---

## Quick reference

| Method | URL | Auth | Body |
|--------|-----|------|------|
| GET | `{{baseUrl}}/` | — | — |
| GET | `{{baseUrl}}/api/auth/username/check` | Optional | Query: `username`, `for_user_id=me` |
| POST | `{{baseUrl}}/api/auth/otp/generate` \| `/otp/resend` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/register` | — | `{ "username", "name", "email", "password", "otp", "phone"? }` |
| POST | `{{baseUrl}}/api/auth/login` | — | `{ "username", "password" }` — `username` accepts username or email |
| POST | `{{baseUrl}}/api/auth/refresh` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout` | Cookie | — |
| POST | `{{baseUrl}}/api/auth/logout-all` | Bearer | — |
| POST | `{{baseUrl}}/api/auth/forget-password` | — | `{ "email" }` |
| POST | `{{baseUrl}}/api/auth/reset-password` | — | `{ "token", "newPassword" }` |
| GET/PATCH | `{{baseUrl}}/api/user/me` | Bearer | Profile fields incl. `latitude`/`longitude` |
| PATCH | `{{baseUrl}}/api/user/me/username` \| `/role` | Bearer | — |
| GET | `{{baseUrl}}/api/user/:username` | Optional Bearer | — |
| GET | `{{baseUrl}}/api/users/nearby` | Optional Bearer | Query: `lat`, `lng`, `radiusKm?`, `limit?` |
| POST | `{{baseUrl}}/api/user/me/onboarding/*` | Bearer | See above |
| POST/GET | `{{baseUrl}}/api/user/me/seller/*` | Bearer | See above |
| GET | `{{baseUrl}}/api/user/me/saved/pieces` \| `/saved/posts` \| `/orders` \| `/sales` | Bearer | — |
| GET/POST/PATCH/DELETE | `{{baseUrl}}/api/user/me/addresses/*` | Bearer | See above |
| POST/DELETE | `{{baseUrl}}/api/user/me/devices` | Bearer | `{ "platform", "pushToken" }` |
| POST | `{{baseUrl}}/api/media/presign` | Bearer | `{ "purpose", "contentType" }` |
| POST/PATCH/GET | `{{baseUrl}}/api/pieces/*` | Varies | See above |
| GET/POST | `{{baseUrl}}/api/pieces/:id/{comments,shipping-quote,collect,related-posts}` | Varies | See above |
| POST/PATCH/GET | `{{baseUrl}}/api/posts/*` | Varies | See above |
| GET | `{{baseUrl}}/api/posts/:id/comments` | — | Query: `cursor?`, `limit?` |
| GET | `{{baseUrl}}/api/users/:username/{pieces,posts,series}` | — | — |
| POST/DELETE | `{{baseUrl}}/api/users/:username/follow` | Bearer | — |
| POST/DELETE | `{{baseUrl}}/api/pieces/:id/{like,save}` \| `/api/posts/:id/{like,save}` | Bearer | — |
| GET | `{{baseUrl}}/api/feed/following` | Bearer | Query: `cursor?`, `limit?` |
| GET | `{{baseUrl}}/api/feed/explore` | Optional Bearer | Query: `medium?`, `cursor?`, `limit?` |
| GET | `{{baseUrl}}/api/feed/for-you` | Bearer | Query: `cursor?`, `limit?` |
| POST/PATCH/GET/DELETE | `{{baseUrl}}/api/series/*` | Varies | See above |
| GET/PATCH/POST | `{{baseUrl}}/api/notifications/*` | Bearer | See above |
| GET/POST/PATCH | `{{baseUrl}}/api/inquiries/*` | Bearer | See above |
| GET/PATCH/POST | `{{baseUrl}}/api/orders/*` | Bearer | See above |

**Auth column:** "Bearer" = `Authorization: Bearer {{accessToken}}` required; "Optional Bearer" = works without a token but returns viewer-specific fields (`isLiked`/`isSaved`/`isFollowing`) when one is sent; "Cookie" = sent automatically by Postman after login/register/refresh.
