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

### Auth – Login / Refresh / Logout / Logout-all

- **POST** `/api/auth/login` — `{ "username", "password" }`. Same response shape as Register.
- **POST** `/api/auth/refresh` — cookie only, no body. New access token + refresh cookie.
- **POST** `/api/auth/logout` — cookie only. Clears refresh cookie.
- **POST** `/api/auth/logout-all` — Bearer required. Revokes all sessions.

### Auth – Forget / Reset password

- **POST** `/api/auth/forget-password` — `{ "email" }`.
- **POST** `/api/auth/reset-password` — `{ "token", "newPassword" }`.

---

## User & profile

### Get me / Update me (protected)

**GET** `{{baseUrl}}/api/user/me` — full profile: `username`, `name`, `email`, `phone`, `bio`, `location`, `profilePhotoUrl`, `coverPhotoUrl`, `role`, `sellerEnabled`, `onboardingComplete`, `emailVerified`, `canChangeUsername`, `tastePreferences`, `lastUsernameChangeAt`, counts (`followersCount`/`followingCount`/`piecesCount`/`savesCount`/`collectedCount`), `isFollowing` (always `false` for self), `savedPieces` (first 20, enriched — see [Pieces](#pieces--posts)), plus the legacy alias keys described above.

**PATCH** `{{baseUrl}}/api/user/me` — body: `{ "name"?, "bio"?, "location"?, "profilePhotoUrl"?, "coverPhotoUrl"?, "latitude"?, "longitude"? }`. `latitude`/`longitude` are optional — both-or-neither (400 if only one is sent); used for [seller "near me" discovery](#geo-near-me-discovery).

### Change username / Public profile

- **PATCH** `/api/user/me/username` — `{ "username" }`. 30-day cooldown.
- **GET** `/api/user/:username` — Optional Bearer (populates `isFollowing`). Public subset only (no email/phone/tastePreferences/savedPieces). Supports `redirectToUsername` for renamed handles.

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
`inquiriesCount` is the number of inquiry threads received on this seller's pieces (see [Inquiries](#inquiries)). `salesCount` is the number of completed sales (orders in `paid`/`shipped`/`completed` status, see [Orders](#orders--checkout--addresses)).

### Saved pieces (protected)

**GET** `{{baseUrl}}/api/user/me/saved/pieces` — pieces the caller has saved, each enriched like `GET /api/pieces/:id`.

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

`contentType`: `image/jpeg`, `image/png`, `image/webp` (max 20MB), or `video/mp4` (max 100MB, supported for any purpose). Response: `{ "presignedPutUrl", "url", "key", "devMode" }` — `devMode: true` when S3 isn't configured (local dev placeholder).

---

## Pieces & posts

Create/edit require completed onboarding. Detail (`GET /:id`) routes accept an **optional** Bearer token — send one for viewer-specific `isLiked`/`isSaved`/`author.isFollowing`; omit for anonymous (all default `false`).

### Pieces

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/pieces` | Bearer | Create; sale fields require seller mode |
| GET | `/api/pieces/:id` | Optional Bearer | Enriched detail |
| PATCH | `/api/pieces/:id` | Bearer | Edit, toggle sale |
| GET | `/api/pieces/:id/related-posts` | — | Posts linked to piece |
| GET | `/api/pieces/:id/comments` | — | Cursor-paginated |
| GET | `/api/pieces/:id/shipping-quote` | Optional Bearer | See [Orders](#orders--checkout--addresses) |
| POST | `/api/pieces/:id/collect` | Bearer + onboarding | Checkout — see [Orders](#orders--checkout--addresses) |
| GET | `/api/users/:username/pieces` | — | Profile Work tab |
| GET | `/api/users/:username/pieces/for-sale` | — | For Sale tab |
| GET | `/api/user/me/saved/pieces` | Bearer | See [User](#saved-pieces-protected) |

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
`yearCreated`/`framingMounting`/`provenance`/`handlingNotes` are first-class optional fields. `PATCH` accepts the same set plus `status` (`draft|live|sold|delisted|reserved` — `reserved`/`sold` are set automatically by checkout, not client-settable in normal use).

**Get piece response** — all create fields plus:
```json
{
  "status": "live", "createdAt": "...",
  "author": { "username": "maya_art", "name": "Maya", "profilePhotoUrl": "...", "isFollowing": false },
  "likeCount": 12, "commentCount": 3, "isLiked": false, "isSaved": false,
  "series": { "id": "...", "name": "Riverwalk Dream", "pieceCount": 3, "previewPieces": [...], "pieceIds": [...] },
  "relatedPosts": []
}
```
`series` is `null` if the piece isn't in one.

### Posts

| Method | URL | Auth | Notes |
|--------|-----|------|-------|
| POST | `/api/posts` | Bearer | WIP/process — no sale fields |
| GET | `/api/posts/:id` | Optional Bearer | Enriched detail |
| PATCH | `/api/posts/:id` | Bearer | Edit, link/unlink piece |
| GET | `/api/posts/:id/comments` | — | Cursor-paginated |
| GET | `/api/users/:username/posts` | — | Profile Process tab |

**Get post response** — base fields (`id`, `userId`, `mediaUrl`, `mediaType`, `caption`, `isProcess`, `linkedPieceId`, `status`, `createdAt`) plus `author`, `likeCount`, `commentCount`, `isLiked`, `isSaved`, and `piece` (full linked piece, or `null`).

---

## Social

Like/save/comment-create/follow require Bearer + onboarding. Comment **reads** are public.

| Method | URL | Notes |
|--------|-----|-------|
| POST/DELETE | `/api/users/:username/follow` | Follow/unfollow |
| POST/DELETE | `/api/pieces/:id/like`, `/api/posts/:id/like` | — |
| POST/DELETE | `/api/pieces/:id/save`, `/api/posts/:id/save` | — |
| POST | `/api/pieces/:id/comments`, `/api/posts/:id/comments` | `{ "body" }` |
| GET | `/api/pieces/:id/comments`, `/api/posts/:id/comments` | Query: `cursor?`, `limit?` (default 50, max 100) |

**Get comments response:**
```json
{ "data": { "items": [{ "id", "body", "author": {...}, "createdAt" }], "nextCursor": "..." } }
```

Follow/like/save/comment each emit a [notification](#notifications) (with push) to the target's owner — skipped for self-actions.

---

## Feeds

| Method | URL | Auth | Description |
|--------|-----|------|--------------|
| GET | `/api/feed/following` | Bearer + onboarding | Pieces+posts from followed users |
| GET | `/api/feed/explore` | Optional Bearer | Public pieces; `?medium=` filter |
| GET | `/api/feed/for-you` | Bearer + onboarding | Stub wrapping explore |

All cursor-paginated: `?cursor=&limit=` (default 20, max 50).
```json
{ "data": { "items": [{ "type": "piece"|"post", "...": "enriched fields" }], "nextCursor": "..." } }
```
`explore` returns pieces only. Anonymous requests get `isLiked`/`isSaved`/`author.isFollowing` defaulted `false`.

---

## Series

Piece grouping for the profile "Series" tab. Mutations require Bearer + onboarding; reads are public. A piece belongs to at most one series.

| Method | URL | Body |
|--------|-----|------|
| GET | `/api/users/:username/series` | — (only `pieceCount > 1`) |
| GET | `/api/series/:id` | — |
| POST | `/api/series` | `{ "name", "pieceIds"?: [] }` |
| PATCH | `/api/series/:id` | `{ "name"?, "pieceOrder"?: [pieceId,...] }` |
| POST | `/api/series/:id/pieces` | `{ "pieceId" }` |
| DELETE | `/api/series/:id/pieces/:pieceId` | — |

**Series object:** list — `{ id, name, pieceCount, previewPieces: [{id,mediaUrl,title}] }`; detail (and mutation responses) — same plus `pieceIds: [...]`.

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
      "actor": { "username", "name", "profilePhotoUrl" } ,
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

Validates the piece is for-sale and `status == "live"` (else `409`), the caller isn't the seller (`400`), the address belongs to the caller (`404`), and the method is valid (`400`). Computes `artworkCents`/`shippingCents`/`taxCents` (flat 8.25% placeholder, server-side) /`totalCents`, creates the order, snapshots the chosen address (edits to the saved address later never change this), and reserves the piece (`status → "reserved"`, so it disappears from sale listings immediately). Response:
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

| Method | URL | Auth |
|--------|-----|------|
| GET | `{{baseUrl}}/` | — |
| POST | `{{baseUrl}}/api/auth/{register,login,refresh,logout,logout-all,otp/generate,otp/resend,forget-password,reset-password}` | Varies |
| GET | `{{baseUrl}}/api/auth/username/check` | Optional |
| GET/PATCH | `{{baseUrl}}/api/user/me` | Bearer |
| PATCH | `{{baseUrl}}/api/user/me/username` \| `/role` | Bearer |
| GET | `{{baseUrl}}/api/user/:username` | Optional |
| GET | `{{baseUrl}}/api/users/nearby` | Optional |
| POST | `{{baseUrl}}/api/user/me/onboarding/*` | Bearer |
| POST/GET | `{{baseUrl}}/api/user/me/seller/*` | Bearer |
| GET | `{{baseUrl}}/api/user/me/saved/pieces` \| `/orders` \| `/sales` | Bearer |
| POST/GET/PATCH/DELETE | `{{baseUrl}}/api/user/me/addresses/*` | Bearer |
| POST/DELETE | `{{baseUrl}}/api/user/me/devices` | Bearer |
| POST | `{{baseUrl}}/api/media/presign` | Bearer |
| POST/PATCH/GET | `{{baseUrl}}/api/pieces/*` | Varies |
| GET/POST | `{{baseUrl}}/api/pieces/:id/{comments,shipping-quote,collect,related-posts}` | Varies |
| POST/PATCH/GET | `{{baseUrl}}/api/posts/*` | Varies |
| GET | `{{baseUrl}}/api/users/:username/{pieces,posts,series}` | — |
| POST/DELETE | `{{baseUrl}}/api/users/:username/follow` | Bearer |
| POST/DELETE | `{{baseUrl}}/api/pieces/:id/{like,save}` | Bearer |
| GET | `{{baseUrl}}/api/feed/{following,explore,for-you}` | Varies |
| POST/PATCH/GET/DELETE | `{{baseUrl}}/api/series/*` | Varies |
| GET/PATCH/POST | `{{baseUrl}}/api/notifications/*` | Bearer |
| GET/POST/PATCH | `{{baseUrl}}/api/inquiries/*` | Bearer |
| GET/PATCH/POST | `{{baseUrl}}/api/orders/*` | Bearer |

**Auth column:** "Bearer" = `Authorization: Bearer {{accessToken}}` required; "Optional" = works without a token, returns viewer-specific fields when one is sent; "Cookie" = sent automatically by Postman after login/register/refresh.
