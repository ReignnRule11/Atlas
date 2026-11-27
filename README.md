# Atlas

**Professional Economy Infrastructure**

> Turn professional capability into economic opportunity.

Atlas is being built to connect a person's professional identity, demonstrable work, relevant opportunities, collaboration, intelligence, and economic activity in one evidence-centered system. It is intended to help professionals move from describing what they can do to demonstrating it—and making that capability discoverable and actionable.

## Product thesis

Professional value should be **demonstrable, discoverable, and economically actionable**. Traditional professional profiles are largely claim-based and fragmented across portfolios, resumes, job boards, project tools, and marketplaces. Atlas aims to connect these layers while preserving user control and making evidence and verification status explicit.

Atlas is not a social-feed-first professional network or a LinkedIn clone.

## Principles

- **Evidence over unsupported claims:** distinguish user-submitted claims from linked evidence and independently verified information.
- **Explainable reputation:** no opaque AI reputation score; any future signal must show what it measures, its inputs, limitations, and how a user can contest it.
- **User control and privacy:** clear consent, granular visibility, and safe handling of personal and professional evidence.
- **Honest status:** features are only described as shipped when implemented and tested; no fabricated profiles, proof, opportunities, integrations, or verification.
- **Utility before scale:** establish real user value and retention before expanding the product surface.
- **Incremental delivery:** build a modular monolith and ship small reviewable pull requests; do not prematurely introduce microservices or blockchain.

## Intended product areas

| Area | Intended capability |
|---|---|
| **Identity** | Professional profile, skills, experience, interests, goals, and availability |
| **Proof** | Projects, artifacts, contributions, evidence links, and transparent verification states |
| **Opportunity** | Jobs, gigs, grants, collaborations, partnerships, and other relevant opportunities |
| **Intelligence** | Grounded profile analysis, skill insights, opportunity matching, and recommendations |
| **Work** | Teams, project workspaces, milestones, collaboration, and contribution records |
| **Economy** | Contracts, invoicing, payments, revenue sharing, and partner-supported financial workflows |
| **Learning** | Learning paths linked to project outcomes, demonstrated skills, and career goals |
| **Network** | Purposeful connections, mentors, referrals, and professional collaboration |

These are product directions, not claims that the modules are currently implemented.

## Initial users and MVP

The initial focus is builders, engineers, designers, product professionals, founders, and independent professionals.

The first validation milestone is intentionally narrow:

1. Create and manage a professional identity.
2. Add skills and experience.
3. Publish projects and attach supporting evidence.
4. Clearly label self-reported information versus verified evidence.
5. Give users control over what is public, private, or shared.

Identity and Proof come first. Opportunity discovery and matching should be introduced only after the profile/evidence foundation can support relevant, explainable matches.

## Differentiator: Proof of Work / Proof Graph

Atlas aims to connect skills and professional claims to supporting evidence—such as projects, repositories, artifacts, documented outcomes, and contributions. The model should preserve provenance and verification state rather than treating every profile statement as equally authoritative.

Future evidence records may distinguish:
- **Self-reported:** entered by the user and not independently verified.
- **Linked evidence:** attached to a source or artifact; the link is not itself proof of authorship or quality.
- **Verified:** validated through a defined process, with the verification method and scope disclosed.

A verification badge must never imply more than the process actually checked.

## Architecture

Atlas starts as a **modular monolith** with clear application boundaries. Services can be extracted only when scale, ownership, or operational needs justify it.

| Layer | Current foundation |
|---|---|
| Web | Next.js 15, React 19, TypeScript |
| API | FastAPI, Python 3.12 |
| Persistence | PostgreSQL 16, SQLAlchemy |
| Local orchestration | Docker Compose |
| API testing | pytest, FastAPI TestClient |
| Planned quality gates | GitHub Actions (backend tests, web type-check/build) |

### Repository layout

```
Atlas/
├── apps/
│   └── web/
│       ├── app/
│       │   ├── globals.css
│       │   ├── layout.tsx
│       │   └── page.tsx
│       ├── Dockerfile
│       ├── next.config.ts
│       ├── package.json
│       └── tsconfig.json
├── services/
│   └── api/
│       ├── app/
│       │   ├── core/
│       │   ├── db/
│       │   ├── routes/
│       │   └── main.py
│       ├── tests/
│       ├── Dockerfile
│       ├── pytest.ini
│       └── requirements.txt
├── .env.example
├── docker-compose.yml
└── README.md
```

The structure will evolve as real product features are added.

## Current implementation status

### Foundation (0.1)

Implemented in the repository:
- Next.js application shell with responsive starter dashboard.
- FastAPI service.
- API liveness endpoint: `GET /health`.
- Database readiness endpoint: `GET /ready` (attempts a database connection).
- SQLAlchemy engine/session baseline.
- PostgreSQL 16 development service in Docker Compose.
- API smoke tests for health and OpenAPI availability.
- Environment example and container build definitions.

Not yet implemented:
- User registration, authentication, session management, account recovery, or RBAC.
- Profile persistence or profile editing.
- Skills, projects, evidence, Proof Graph, or verification workflows.
- Opportunity ingestion, search, matching, or recommendations.
- AI agent functionality.
- Teams, collaboration, contracts, billing, payments, or escrow.
- Production deployment, production secrets, migrations, backups, monitoring, or security review.

Do not use the starter dashboard as evidence that these features already work.

## Local development

### Requirements

- Docker and Docker Compose (recommended for the complete local stack).
- Alternatively: Python 3.12+, Node.js 22+, npm, and a local PostgreSQL 16 database.

### 1. Clone the repository

```bash
git clone https://github.com/ReignnRule11/Atlas.git
cd Atlas
```

### 2. Configure environment

Copy the example environment file:

```bash
cp .env.example .env
```

The sample values are for **local development only**. Do not use the sample database password or commit a real `.env` file.

### 3. Start the services

```bash
docker compose up --build
```

When containers are built and running:
- Web app: http://localhost:3000
- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs
- Liveness check: http://localhost:8000/health
- Database readiness check: http://localhost:8000/ready

Stop the stack with:

```bash
docker compose down
```

The named PostgreSQL volume retains local database data. To intentionally delete the local database volume and its data, use `docker compose down -v` (destructive).

### Web development without Docker

```bash
cd apps/web
npm install
npm run dev
```

Quality checks:

```bash
npm run typecheck
npm run build
```

### API development without Docker

```bash
cd services/api
python -m venv .venv
# Activate the virtual environment for your operating system
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

The API needs a reachable PostgreSQL instance for `/ready`. The liveness endpoint and OpenAPI smoke tests do not require a database query.

## Environment variables

| Variable | Purpose | Example (local only) |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection URL | `postgresql+psycopg://atlas:atlas@db:5432/atlas` |
| `API_CORS_ORIGINS` | Comma-separated allowed web origins | `http://localhost:3000` |

Review `.env.example` and the application settings before configuring another environment. Use managed secrets in deployed environments rather than committing credentials.

## API baseline

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | API liveness; does not assert database availability |
| GET | `/ready` | Readiness probe; checks database connectivity with `SELECT 1` |
| GET | `/docs` | FastAPI Swagger UI |
| GET | `/openapi.json` | API schema |

A readiness failure indicates the API cannot complete its database check. Authentication and domain endpoints will be added in later increments.

## Roadmap

1. **Foundation and quality gates:** stable scaffold, developer experience, automated checks, and deployment hygiene.
2. **Identity and Proof MVP:** secure authentication, profile/skills, project records, evidence links, privacy controls, and profile/proof management.
3. **Intelligence:** grounded profile analysis, skill insights, and explainable opportunity matching.
4. **Network and Work:** collaboration, teams, workspaces, projects, and contribution records.
5. **Economy:** contracts, invoices, payment integrations, partner rails, and carefully scoped financial workflows.
6. **Platform expansion:** APIs, enterprise integrations, workforce insights, and agent interoperability.

Roadmap sequence may change based on validation, risk, and user evidence.

## Security and trust considerations

Atlas is not production-ready. Before real users or sensitive information are onboarded, the project must implement and review:
- Authentication, secure session handling, account recovery, authorization, and role boundaries.
- Input validation, rate limits, abuse protections, and security headers.
- Privacy/consent controls, data export and deletion, and evidence access rules.
- Secrets management, database migration strategy, backups, restoration testing, and least privilege.
- Audit events for sensitive operations.
- Dependency and container scanning, test coverage for security boundaries, and deployment monitoring.
- A documented verification policy and dispute/appeal process for any verification or reputation signals.

Do not upload sensitive documents or private evidence to the current scaffold.

## Contributing

Contributions should be small, focused, and reviewable. For substantive changes:
1. Describe the user problem and expected outcome.
2. Define acceptance criteria and privacy/security implications.
3. Keep implementation and tests in the same pull request where practical.
4. Run relevant checks and report results accurately.
5. Update documentation when behavior, configuration, or setup changes.

Issues and pull requests are welcome. Avoid introducing simulated integrations, placeholder features presented as working, or unnecessary infrastructure complexity.

## License

No license has been selected yet. Unless a license is added to this repository, reuse and redistribution permissions are not granted by default.
