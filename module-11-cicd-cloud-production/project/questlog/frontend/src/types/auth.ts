/**
 * The auth-related shapes this frontend works with -- new in Module 07.
 * See lessons/06-building-signup-login.md for the backend routes these
 * mirror, and src/api/authApi.ts for where each one is actually used.
 */

/** Matches the backend's `UserPublic` Pydantic model exactly -- see
 * backend/app/models.py. Deliberately has no password field at all;
 * there is no version of this type, anywhere in this frontend, that
 * holds a password past the moment a login/signup form submits it. */
export interface AuthUser {
  id: string;
  email: string;
  createdAt: string;
}

/** Matches the backend's `Token` Pydantic model -- the body
 * `POST /api/auth/login` returns on success. Deliberately **snake_case**
 * (`access_token`, `token_type`), unlike every other type in this file
 * and in src/types/quest.ts -- those field names are not this app's own
 * design choice, they're mandated, verbatim, by the OAuth2 spec itself
 * (RFC 6749) that this login endpoint's response shape borrows, per
 * lessons/05-oauth2-conceptual.md. Renaming them to `accessToken` to
 * match QuestLog's own camelCase convention would break compatibility
 * with that spec (and with tools, like FastAPI's own `/docs` "Authorize"
 * button, that expect these exact names) for no real benefit. */
export interface AuthToken {
  access_token: string;
  token_type: string;
}
