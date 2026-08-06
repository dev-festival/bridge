# Bridge Surface Architecture Decisions

This log records the decisions that constrain the implementation schedule. It is based on `BRIDGE-SPEC.md` and the repository state observed on 2026-08-06. Decisions marked **Accepted for planning** may be revisited through a later ADR, but a sprint must not silently diverge from them.

## ADR-001: Use a modest monorepo with explicit boundaries

- **Status:** Accepted for planning
- **Decision:** Keep the FastAPI entry point and API schemas under `apps/api`, the React application under `apps/web`, reusable Python domain code under `src/bridge_surface`, migrations under `migrations`, and Python tests under `tests`. Keep API routes thin; domain services own business rules; repositories own persistence; provider adapters own external calls; renderers own export formatting.
- **Why:** This follows the product specification while preventing route handlers, ORM models, API schemas, React components, and external-provider code from becoming coupled.
- **Consequence:** A feature may touch several layers, but each sprint must still remain a single reviewable capability. Exact filenames are intentionally deferred until the foundation exists.

## ADR-002: Establish one cross-platform tool contract

- **Status:** Accepted for planning
- **Decision:** Use Python 3.13+, `uv` with `pyproject.toml`/`uv.lock`, and npm with `apps/web/package.json`/`package-lock.json`. Establish these canonical gates:
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run mypy .`
  - `uv run pytest`
  - `npm --prefix apps/web run lint`
  - `npm --prefix apps/web run typecheck`
  - `npm --prefix apps/web run test -- --run`
  - `npm --prefix apps/web run build`
- **Why:** The repository has no existing package or command configuration. These commands are concrete, CI-friendly equivalents of the required gates and work on the current Windows environment as well as Unix-like CI runners.
- **Consequence:** Backend-only sprints before the web scaffold run only the four Python gates. Once Sprint 06 creates the web toolchain, every feature sprint runs all eight gates unless the plan explicitly says otherwise.

## ADR-003: Keep operational health outside the versioned business API

- **Status:** Accepted for planning
- **Decision:** Expose `GET /health` for process health and place configuration and product endpoints under `/api/v1`, beginning with `GET /api/v1/config`.
- **Why:** Health checks are operational rather than a versioned domain contract. This resolves the specification's simultaneous request for a versioned API and an unqualified health route.
- **Consequence:** No duplicate `/api/v1/health` endpoint is planned unless deployment infrastructure later requires it.

## ADR-004: Put persistence behind repositories and migrate every schema change

- **Status:** Accepted for planning
- **Decision:** Use SQLAlchemy 2.x with Alembic and SQLite initially. Establish the migration system before adding persistent domain models. Services depend on repository interfaces or focused repository classes, never directly on API request state.
- **Why:** This keeps database logic out of routes and preserves a realistic path to PostgreSQL.
- **Consequence:** SQLite-specific shortcuts, implicit schema creation during normal startup, and unmigrated model changes are disallowed. Each model sprint includes a migration round-trip integration test.

## ADR-005: Model one local owner now without baking in authentication

- **Status:** Accepted for planning
- **Decision:** Seed one local user and require ownership fields on owned records. Resolve that user through an application dependency rather than hard-coded IDs in services.
- **Why:** The MVP is single-user, but the specification requires a path to company authentication and SSO.
- **Consequence:** Authentication, authorization roles, organizations, and SSO are out of scope. Repositories and APIs must still prevent owner fields from being supplied arbitrarily by the browser.

## ADR-006: Make originals and approval transitions service-enforced invariants

- **Status:** Accepted for planning
- **Decision:** A persisted conversation message's `original_text` and `source_language` are immutable. Translations remain separately editable. Email source fields are author-editable while a draft is open, but changing source text invalidates generated translations, reverse translations, warnings, and approvals. Approved source content is locked until the user explicitly reopens it for revision. All transitions are validated in services and reflected by explicit states.
- **Why:** The product must never overwrite the original or depend on disabled frontend controls for safety.
- **Consequence:** PATCH schemas use allowlists. Invalid transitions return domain errors. The MVP tracks creation/update/approval timestamps but does not promise a complete legal audit history.

## ADR-007: Use an explicit translation protocol and deterministic mock first

- **Status:** Accepted for planning
- **Decision:** Define provider-neutral translation context/result contracts and an async provider protocol. The deterministic mock is the default until a real provider is explicitly selected by environment configuration. Provider calls occur in application services, never route handlers.
- **Why:** Conversation and email behavior must be testable without credentials, and a later provider must not control domain state.
- **Consequence:** Tests use contract fixtures, not live API calls. A configured real provider failure is reported; it must not mutate or delete saved content. Development-only mock fallback must be explicit and visibly labeled rather than silent.

## ADR-008: Resolve terminology from most-specific to global scope

- **Status:** Accepted for planning
- **Decision:** For conversation translation, conversation terms override global terms. For email translation, email-draft terms override global terms. A do-not-translate entry takes precedence at the same effective scope. Duplicate active entries at one scope are rejected rather than resolved by creation order.
- **Why:** The specification defines scopes but not collision behavior. Deterministic precedence is required before terminology can affect prompts or preservation checks.
- **Consequence:** Organization and user preference scopes remain future work. Terms are injected as context and checked after translation; they do not rewrite original content.

## ADR-009: Treat meaning validation as advisory but acknowledgement as mandatory

- **Status:** Accepted for planning
- **Decision:** Structured warnings are stored separately from translations. Warnings never prevent a user from approving, but every unresolved warning requires explicit acknowledgement during approval. Resolving a warning and acknowledging it are distinct actions.
- **Why:** The specification permits approval despite warnings while requiring visible, deliberate review.
- **Consequence:** Confidence is informational only. The backend, not the UI, enforces warning acknowledgement.

## ADR-010: Keep email assembly pure and delivery-free in the MVP

- **Status:** Accepted for planning
- **Decision:** Build plain-text and HTML output from one validated email assembly model. Output contains the approved Japanese version and approved English version, then exactly one selected shared signature. Reverse translation is validation-only and is never emitted. HTML is escaped by default. No SMTP, Microsoft Graph, Gmail, send route, auto-send behavior, mailbox draft creation, or development delivery provider is included in the MVP schedule.
- **Why:** The attached guideline explicitly says email sending is not implemented in the MVP and requires rendering to be proven before mailbox integration.
- **Consequence:** The renderer/export service boundary is the future handoff point for an `EmailDeliveryProvider`. That protocol should be introduced only when mailbox-draft work is authorized, avoiding speculative MVP code.

## ADR-011: Require explicit ordering when recipients do not share one preference

- **Status:** Accepted for planning
- **Decision:** `recipient_language_first` resolves automatically only when all To recipients with a recorded preference agree. With mixed or unknown To-recipient preferences, the UI requires an explicit Japanese-first or English-first resolution before approval/export. CC preferences do not choose the order. Sender-first is resolved from the draft source language.
- **Why:** A single bilingual email cannot put two different languages first simultaneously. The specification requires mixed Japanese/English To and CC recipients but does not define this edge case.
- **Consequence:** Both approved languages are always present regardless of order. The API returns a validation error rather than choosing silently.

## ADR-012: Use feature-local React state and typed API boundaries

- **Status:** Accepted for planning
- **Decision:** Use React, TypeScript, Vite, CSS modules or a similarly small styling layer, feature-local state, and focused API hooks. Do not add a global state library or large UI framework during the MVP.
- **Why:** The product is workflow-heavy but does not yet justify additional frontend architecture.
- **Consequence:** Domain rules remain on the backend. Frontend tests verify interaction and visible state, not a duplicate state machine.

## ADR-013: Minimize data exposure in logs and provider metadata

- **Status:** Accepted for planning
- **Decision:** Structured logs omit message/email bodies by default, redact credentials and authorization headers, use identifiers for correlation, and sanitize provider metadata through an allowlist before persistence. The UI clearly identifies when text will leave the application for an external provider.
- **Why:** Manufacturing communications may be confidential, and provider responses/errors can accidentally echo content or secrets.
- **Consequence:** Debug logging of full bilingual content is not an MVP feature. Production use must be documented as requiring company security review; the product will not claim compliance certification.

## ADR-014: Archive conversations instead of hard-deleting them in normal use

- **Status:** Accepted for planning
- **Decision:** Interpret the conversation delete endpoint as an archive operation backed by `archived_at`. Hard deletion is not exposed in the MVP UI or API.
- **Why:** This aligns the suggested model with preservation requirements and avoids accidental loss of communication history.
- **Consequence:** API documentation must call out archive semantics. Data-retention and administrative purge policies remain future work.

## ADR-015: Defer the real-provider vendor choice to its entry sprint

- **Status:** Proposed; decision required before Sprint 46
- **Decision:** Sprint 46 must record a vendor-specific ADR after reviewing approved providers, data-handling terms, SDK/API stability, and deployment constraints. Only one adapter is implemented in the MVP.
- **Why:** The specification requires one real provider but names none. Selecting one during planning without organizational privacy and procurement context would be speculative.
- **Consequence:** Sprints 01-45 must remain provider-neutral. Sprint 46 cannot proceed until configuration names, required credentials, and the approved data boundary are known.
