You are acting as the lead product engineer and software architect for a new bilingual business communication application.

# Project Working Title

**Bridge Surface**

The name is temporary. Do not spend time on branding during the first build phase.

# Core Product Idea

This is not primarily a translation application.

It is a **shared bilingual communication surface** where Japanese-speaking and English-speaking manufacturing professionals can communicate through the same message, email, and business context.

The central product principle is:

> One shared business message, represented clearly in both Japanese and English.

Both languages must be treated as first-class views of the same communication object.

Do not design the application as a normal chat interface with a translated message hidden underneath. The interface must visually reinforce that the Japanese side and English side are interacting with the same communication surface.

# Primary Users

The application is intended for Japanese and English-speaking associates working together in a manufacturing business environment.

Relevant business areas include:

* Production
* Maintenance
* Reliability
* Engineering
* Quality
* Safety
* Logistics
* Purchasing
* Scheduling
* Project management
* Supplier communication
* Equipment installation
* Training
* Problem-solving meetings
* Management communication

The application is not Maximo-specific, although Maximo terminology, equipment numbers, work orders, asset identifiers, and status codes may appear in conversations.

# Initial Product Modes

Build the application around two primary modes:

1. **Conversation Mode**
2. **Email Mode**

The architecture should support future communication surfaces, but only these two modes belong in the first major release.

Potential future modes include:

* Meeting notes
* Shift handoff
* Work instructions
* Document translation
* SOP review
* Live voice conversation
* Shared technical notes

Do not implement those future modes yet.

---

# Product Philosophy

The application must preserve three things:

1. What the original person wrote
2. What the other language communicates
3. Whether both language versions still express the same business meaning

The application must never hide or overwrite the original message.

Translations must be editable without altering the original source text.

Technical and business terminology must remain stable across a conversation.

Names, part numbers, equipment identifiers, document numbers, acronyms, codes, and numerical values must not be translated or modified unless explicitly requested.

Examples include:

* Line 4
* Robot 17
* IsoQuest
* WAPPR
* EQ-1048
* Drawing 22A-118
* WO123456
* 8:30 AM
* $25,000
* 0.05 mm

---

# Conversation Mode UX

Conversation Mode should not resemble a conventional two-person chat where translated messages simply alternate.

The primary desktop layout should use three visually connected regions:

```text
Japanese Side | Shared Translation Surface | English Side
```

The Japanese user writes on the Japanese side.

The English user writes on the English side.

Each conversation turn should create one shared message row.

A message row should include:

* Original language
* Original text
* Translated text
* Speaker side
* Timestamp
* Preserved terminology
* Translation status
* Optional clarification warning
* Optional edited translation
* Optional reverse-translation check

The center surface should visually connect the original message to its counterpart language.

Possible visual concept:

```text
┌────────────────────┬──────────────────────────┬────────────────────┐
│ Japanese Side      │ Shared Meaning Surface   │ English Side       │
├────────────────────┼──────────────────────────┼────────────────────┤
│ Japanese original │ English translation      │                    │
├────────────────────┼──────────────────────────┼────────────────────┤
│                    │ Japanese translation     │ English original   │
└────────────────────┴──────────────────────────┴────────────────────┘
```

On mobile, collapse this into stacked message cards while preserving the relationship among:

* Original
* Translation
* Speaker
* Message direction

Conversation Mode MVP actions:

* Create conversation
* Enter Japanese message
* Enter English message
* Translate message
* Edit translated text
* Show reverse translation
* Mark translation approved
* Flag translation as unclear
* Save conversation history
* Copy either language version
* Export bilingual transcript
* Maintain a conversation terminology list

Do not implement voice input in the first phase.

---

# Email Mode UX

Email Mode is a critical feature, not an optional add-on.

The application must produce bilingual emails intended for mixed Japanese and English recipients, including CC lists containing people from both language groups.

The outgoing email must contain both language versions.

The application should not treat the second language as an internal-only retranslation.

The standard workflow should be:

```text
Compose in source language
        ↓
Generate opposite-language draft
        ↓
Generate reverse translation for validation
        ↓
Review and approve
        ↓
Create bilingual outgoing email
```

The outgoing email should contain:

```text
Recipient-preferred language version

────────

Other language version

────────

Shared approved signature
```

Example:

```text
──────── 日本語 ────────

[Japanese message]

──────── English ────────

[English message]

────────────────────────

[Signature]
```

The application must support:

* English-authored email
* Japanese-authored email
* Recipient language first
* Sender language first
* Japanese first
* English first
* Bilingual subject line
* Single shared signature
* English signature profile
* Japanese signature profile
* Bilingual signature profile
* Internal signature profile
* External or supplier signature profile

The application should preserve the approved original language exactly.

The opposite language should be generated from the original.

The reverse translation is a validation artifact. It should be visible inside the application but should not automatically appear as a third version in the outgoing email.

The email itself should contain the approved original and approved translated version.

Email Mode MVP actions:

* Compose email
* Add To recipients
* Add CC recipients
* Enter subject
* Select source language
* Select language order
* Translate subject
* Translate body
* Generate reverse translation
* Edit translated version
* Compare original and reverse translation
* Mark both language versions approved
* Select signature profile
* Preview final bilingual email
* Copy final email as plain text
* Copy final email as HTML
* Save email draft locally

Do not send email directly in the first implementation milestone.

Create the architecture so email delivery can be added later through:

1. SMTP
2. Microsoft Graph
3. Gmail API

The preferred rollout order is:

1. Copy-to-email-client mode
2. Mailbox draft creation
3. Explicit send after final approval

Never auto-send translated email.

---

# Translation Behavior

Create a translation provider abstraction.

Do not tightly couple the application to one model or API.

Use an interface similar to:

```python
class TranslationProvider(Protocol):
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: TranslationContext,
    ) -> TranslationResult:
        ...
```

The translation result should include:

* translated_text
* detected_source_language
* reverse_translation
* preserved_terms
* ambiguous_terms
* warnings
* confidence, if available
* provider metadata

Create a mock translation provider for local development and testing.

Create one real provider adapter behind environment variables, but ensure the application runs without external credentials.

Do not hardcode API keys.

Use `.env` configuration with a committed `.env.example`.

Translation prompts should explicitly instruct the provider to:

* Preserve business meaning
* Preserve names and codes
* Preserve equipment and document identifiers
* Avoid casual wording unless requested
* Use professional manufacturing-business language
* Avoid inventing context
* Flag ambiguity instead of guessing
* Keep numerical values unchanged
* Preserve bullet structures
* Preserve requested dates and deadlines
* Preserve levels of urgency
* Distinguish requests, instructions, questions, findings, and approvals

---

# Terminology Management

Create a terminology system that can operate at multiple scopes:

* Global application terminology
* Organization terminology
* Conversation terminology
* Email draft terminology
* User terminology preferences

For the MVP, implement:

* Global terminology
* Conversation terminology
* Email draft terminology

Each terminology entry should include:

* source term
* preferred Japanese term
* preferred English term
* do-not-translate flag
* notes
* scope
* active status

Example:

```json
{
  "source_term": "trial",
  "english_term": "production trial",
  "japanese_term": "トライ生産",
  "do_not_translate": false,
  "notes": "Manufacturing trial, not legal proceeding"
}
```

The application should allow users to add a term from a translation warning.

---

# Meaning Validation

The system should compare:

* Original text
* Translated text
* Reverse translation

Create a lightweight meaning-validation layer.

For the first version, this can be provider-generated structured feedback.

Meaning warnings should identify issues such as:

* Request changed into confirmation
* Investigation changed into instruction
* Possibility changed into certainty
* Deadline removed
* Urgency weakened
* Responsibility changed
* Negative statement became positive
* Equipment identifier changed
* Numerical value changed
* Business term appears ambiguous

The user must be able to approve a translation even when warnings exist, but the approval should be explicit.

---

# Recommended Technical Stack

Use the following unless a strong technical reason requires adjustment:

## Backend

* Python 3.13+
* FastAPI
* SQLAlchemy 2.x
* Pydantic
* Alembic
* SQLite for initial development
* PostgreSQL-compatible design
* Pytest
* Ruff
* Mypy
* HTTPX

## Frontend

Use a simple modern frontend.

Preferred starting point:

* React
* TypeScript
* Vite
* CSS modules or a small maintainable styling layer
* No large UI framework unless clearly justified

Keep the frontend architecture modest.

Do not create unnecessary state-management complexity.

Use standard React state and API hooks unless the application grows beyond that.

## Authentication

For the first local MVP:

* Single local user mode
* No external authentication dependency

Design user ownership fields so multi-user authentication and company SSO can be added later.

## Persistence

Use SQLite with migrations.

Create clear repositories or service layers so database logic is not spread across API routes.

---

# Suggested Domain Model

Create models approximately equivalent to:

## User

* id
* display_name
* preferred_language
* created_at
* updated_at

## Conversation

* id
* title
* created_by
* created_at
* updated_at
* archived_at

## Message

* id
* conversation_id
* speaker_side
* source_language
* original_text
* translated_text
* reverse_translation
* translation_status
* provider_name
* provider_metadata
* created_at
* updated_at

## MessageWarning

* id
* message_id
* warning_type
* message
* severity
* resolved
* created_at

## TerminologyEntry

* id
* scope_type
* scope_id
* source_term
* english_term
* japanese_term
* do_not_translate
* notes
* active
* created_at
* updated_at

## EmailDraft

* id
* source_language
* subject_original
* subject_translated
* body_original
* body_translated
* reverse_translation
* language_order
* translation_status
* signature_profile_id
* created_at
* updated_at

## EmailRecipient

* id
* email_draft_id
* recipient_type
* display_name
* email_address
* preferred_language

Recipient type values:

* to
* cc
* bcc

BCC may exist in the data model but does not need significant UI emphasis in the MVP.

## SignatureProfile

* id
* name
* signature_type
* english_content
* japanese_content
* bilingual_content
* active
* created_at
* updated_at

---

# API Design

Create a versioned API under:

```text
/api/v1
```

Suggested endpoints:

```text
GET    /health
GET    /config

GET    /conversations
POST   /conversations
GET    /conversations/{conversation_id}
PATCH  /conversations/{conversation_id}
DELETE /conversations/{conversation_id}

GET    /conversations/{conversation_id}/messages
POST   /conversations/{conversation_id}/messages
PATCH  /messages/{message_id}
POST   /messages/{message_id}/translate
POST   /messages/{message_id}/reverse-translate
POST   /messages/{message_id}/approve
POST   /messages/{message_id}/flag

GET    /terminology
POST   /terminology
PATCH  /terminology/{entry_id}
DELETE /terminology/{entry_id}

GET    /email-drafts
POST   /email-drafts
GET    /email-drafts/{draft_id}
PATCH  /email-drafts/{draft_id}
DELETE /email-drafts/{draft_id}
POST   /email-drafts/{draft_id}/translate
POST   /email-drafts/{draft_id}/validate
POST   /email-drafts/{draft_id}/approve
GET    /email-drafts/{draft_id}/preview
GET    /email-drafts/{draft_id}/export

GET    /signature-profiles
POST   /signature-profiles
PATCH  /signature-profiles/{profile_id}
DELETE /signature-profiles/{profile_id}
```

Do not create direct-send endpoints during the first milestone.

---

# Repository Structure

Use a clear monorepo structure similar to:

```text
bridge-surface/
├── apps/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── dependencies/
│   │   └── schemas/
│   └── web/
│       ├── src/
│       ├── public/
│       └── tests/
├── src/
│   └── bridge_surface/
│       ├── config/
│       ├── domain/
│       ├── models/
│       ├── repositories/
│       ├── services/
│       ├── translation/
│       ├── terminology/
│       ├── validation/
│       ├── email/
│       └── exports/
├── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/
├── docs/
├── .env.example
├── pyproject.toml
├── README.md
└── Makefile
```

Adjust details where needed, but preserve separation between:

* API
* Domain logic
* Translation providers
* Persistence
* Email formatting
* Frontend

---

# CLI Requirements

Create an owner/admin CLI using Typer.

Suggested commands:

```text
bridge init-db
bridge migrate
bridge seed-demo
bridge run-api
bridge create-user
bridge list-conversations
bridge export-conversation <conversation-id>
bridge list-terminology
bridge add-term
bridge export-email <draft-id>
bridge doctor
```

The `doctor` command should verify:

* Python version
* Database connection
* Migration status
* Required environment configuration
* Translation provider configuration
* Frontend build availability

The application should still run using the mock translation provider when no external provider credentials exist.

---

# Email Rendering

Create both plain-text and HTML renderers.

The renderer should support:

* Japanese first
* English first
* Recipient language first
* Sender language first
* Bilingual subject
* Clear language separators
* Shared signature
* HTML-safe escaping
* Plain-text fallback

Example plain-text structure:

```text
本メールは日本語と英語の両方で記載しています。
This message is provided in both Japanese and English.

──────── 日本語 ────────

[Japanese message]

──────── English ────────

[English message]

────────────────────────

[Signature]
```

The standardized bilingual notice should be configurable.

Do not automatically add it when the user disables it.

---

# Privacy and Safety Requirements

Manufacturing communications may contain confidential business information.

Design accordingly:

* Do not log full message bodies by default
* Redact API keys and credentials
* Avoid exposing translation text in exception traces
* Add configurable structured logging
* Store provider metadata without storing secrets
* Clearly identify when text is sent to an external translation provider
* Support a future local translation provider
* Require explicit approval before any future email-send action
* Never silently modify approved text
* Maintain edit timestamps
* Preserve original message text

Do not claim the application is certified for confidential, export-controlled, regulated, or proprietary company data.

Document that production deployment requires company security review.

---

# Testing Requirements

Testing is mandatory.

## Unit Tests

Cover:

* Terminology preservation
* Email language ordering
* Plain-text email rendering
* HTML email rendering
* Signature selection
* Translation provider interface
* Mock provider behavior
* Meaning-warning parsing
* Approval state transitions
* Numerical-value preservation
* Equipment-code preservation

## Integration Tests

Cover:

* Conversation creation
* Message translation flow
* Translation edit flow
* Approval flow
* Email draft creation
* Email translation
* Email validation
* Email preview
* Email export
* Database migrations

## Frontend Tests

Cover key user flows:

* Add Japanese message
* Add English message
* Review translation
* Edit translation
* Approve message
* Compose bilingual email
* Change language order
* Preview final email
* Select signature
* Save draft

## Test Gates

Every milestone must pass:

```text
ruff check .
ruff format --check .
mypy .
pytest
frontend lint
frontend typecheck
frontend tests
frontend production build
```

Do not mark a milestone complete with failing tests.

---

# Documentation Requirements

Create:

## README.md

Include:

* Product purpose
* Screenshots or interface placeholders
* Local setup
* Environment configuration
* Database setup
* Running backend
* Running frontend
* Running tests
* Mock translation mode
* Real provider configuration
* CLI usage
* Known limitations

## docs/architecture.md

Include:

* System diagram
* Domain model
* Translation flow
* Email flow
* Provider abstraction
* Security boundaries
* Future deployment considerations

## docs/product-principles.md

Include:

* One message, two first-class language views
* Original text is immutable
* Translation is editable
* Meaning validation is visible
* Business terminology is preserved
* Human approval precedes external delivery

## docs/roadmap.md

Include future phases without implementing them prematurely.

---

# Development Phases

Work incrementally.

Do not attempt the complete final system in one uncontrolled pass.

## Phase 0 — Repository Foundation

Deliver:

* Project structure
* Python configuration
* Frontend configuration
* FastAPI health endpoint
* SQLite connection
* Alembic migration setup
* Typer CLI
* Test configuration
* CI-ready commands
* README setup instructions

Acceptance criteria:

* Backend starts
* Frontend starts
* Database initializes
* Tests run
* Mock provider loads
* `bridge doctor` works

## Phase 1 — Conversation Mode Foundation

Deliver:

* Conversation model
* Message model
* Conversation API
* Message API
* Mock translation workflow
* Japanese side, center surface, English side
* Persistent conversation history
* Translation editing
* Translation approval
* Responsive mobile layout

Acceptance criteria:

* English and Japanese users can enter messages
* Each message appears as one shared bilingual message object
* Original text remains unchanged
* Translation can be edited
* Conversation survives refresh
* Tests cover the main workflow

## Phase 2 — Terminology and Meaning Validation

Deliver:

* Terminology entries
* Conversation terminology
* Do-not-translate rules
* Preserved-term display
* Reverse translation
* Meaning warnings
* Approval with warning acknowledgement

Acceptance criteria:

* Part numbers and equipment identifiers remain unchanged
* User-defined terminology affects translation context
* Reverse translation is visible
* Meaning warnings can be reviewed and resolved

## Phase 3 — Email Mode

Deliver:

* Email draft model
* Recipient model
* Signature profiles
* Subject translation
* Body translation
* Reverse translation
* Language ordering
* Plain-text preview
* HTML preview
* Copy/export capability
* Draft persistence

Acceptance criteria:

* User can compose in either language
* Final email contains both approved languages
* Mixed-language CC recipients are supported
* Signature appears once
* Original and translation remain synchronized but separately editable
* No direct sending exists yet

## Phase 4 — Real Translation Provider

Deliver:

* One external provider adapter
* Environment-based configuration
* Timeout handling
* Retry policy
* Provider error messages
* Mock fallback in development
* Provider metadata
* Security documentation

Acceptance criteria:

* App runs without credentials using mock provider
* App can use external provider when configured
* Provider failures do not destroy drafts
* No secrets appear in logs

## Phase 5 — Mail Integration Preparation

Do not implement full production sending unless explicitly directed.

Prepare interfaces for:

* SMTP
* Microsoft Graph
* Gmail API

Create an `EmailDeliveryProvider` protocol.

Implement only a development-safe file or console delivery provider unless directed otherwise.

The future delivery API must require:

* Approved original
* Approved translation
* Final preview confirmation
* Explicit send request
* Idempotency protection

---

# UI Design Direction

The UI should feel like a professional manufacturing-business tool.

Avoid:

* Consumer social-media styling
* Excessive animation
* Flags as the primary language selector
* Cartoon translation icons
* Overly colorful chat bubbles
* Hidden translation states
* Tiny text
* Excessive modal dialogs

Prefer:

* Clear typography
* Strong alignment
* Calm neutral colors
* Japanese and English labels where useful
* Visible message relationships
* Clear approval states
* Desktop-first three-column workspace
* Responsive stacked mobile cards
* Accessible form controls
* Keyboard-friendly interaction
* High contrast
* Clear error messaging

Use language labels such as:

```text
日本語
English
```

Do not rely only on `J` and `E`, although those can be used as compact secondary labels.

---

# Important State Rules

A translated message should use explicit states:

```text
draft
translated
review_needed
edited
warning
approved
```

An email should not become export-ready until:

* Source body exists
* Translated body exists
* Source subject exists or is intentionally blank
* Translation warnings have been reviewed
* Original version is approved
* Translation version is approved
* Signature selection is valid

Create state-transition validation in the service layer.

Do not depend only on disabled frontend buttons for enforcing rules.

---

# Demo Data

Seed the application with realistic manufacturing-business examples.

Include terminology such as:

* production trial
* countermeasure
* line stop
* downtime
* quality concern
* temporary repair
* permanent repair
* inspection result
* equipment abnormality
* supplier response
* target completion date
* drawing revision
* work order
* root cause
* corrective action
* preventive action

Include example identifiers:

* Line 4
* Robot 17
* EQ-1048
* WO123456
* Drawing 22A-118
* IsoQuest

Do not use real confidential company information.

---

# Implementation Conduct

Before coding:

1. Restate the product in concise technical language.
2. Identify architectural assumptions.
3. Produce the proposed repository tree.
4. Produce the first milestone plan.
5. Identify major risks.
6. Then begin implementation.

During implementation:

* Work in small, reviewable increments
* Keep the application runnable
* Add tests with each feature
* Avoid speculative abstractions
* Avoid placeholder code that pretends to work
* Mark incomplete functionality clearly
* Document design decisions
* Do not add unrequested infrastructure
* Do not implement direct email sending in the first milestone
* Do not make translation provider calls inside route handlers
* Do not place business logic directly in React components
* Do not mix database models and API schemas

At the end of each phase, provide:

* Summary of completed work
* Files changed
* Commands to run
* Tests added
* Test results
* Known limitations
* Recommended next phase

# First Task

Begin with **Phase 0 — Repository Foundation**.

Create the repository structure, configuration, minimal backend, minimal frontend, database initialization, migrations, CLI, test framework, mock translation provider, documentation skeleton, and development commands.

Do not jump ahead into full Conversation Mode until Phase 0 passes all test gates.

The first deliverable must leave the repository in a clean, runnable, testable state.
