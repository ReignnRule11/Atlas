-- Atlas Identity & Proof foundation.
-- Apply once to a PostgreSQL database. Rollback: drop tables in reverse dependency order,
-- then drop the enum types declared below.
CREATE TYPE profile_visibility AS ENUM ('private', 'unlisted', 'public');
CREATE TYPE project_visibility AS ENUM ('private', 'unlisted', 'public');
CREATE TYPE evidence_visibility AS ENUM ('private', 'unlisted', 'public');
CREATE TYPE evidence_status AS ENUM ('self_reported', 'pending_review', 'verified', 'rejected');

CREATE TABLE owners (
    id UUID PRIMARY KEY,
    auth_provider VARCHAR(40) NOT NULL CHECK (length(auth_provider) > 0),
    auth_subject VARCHAR(255) NOT NULL CHECK (length(auth_subject) > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_owners_provider_subject UNIQUE (auth_provider, auth_subject)
);

CREATE TABLE professional_profiles (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL UNIQUE REFERENCES owners(id) ON DELETE CASCADE,
    display_name VARCHAR(120) NOT NULL CHECK (length(display_name) > 0),
    headline VARCHAR(180),
    summary TEXT,
    location VARCHAR(160),
    visibility profile_visibility NOT NULL DEFAULT 'private',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE skills (
    id UUID PRIMARY KEY,
    profile_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL CHECK (length(name) > 0),
    proficiency VARCHAR(40),
    source VARCHAR(30) NOT NULL DEFAULT 'self_reported'
        CHECK (source IN ('self_reported', 'imported', 'assessed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_skill_profile_name UNIQUE (profile_id, name)
);

CREATE TABLE experiences (
    id UUID PRIMARY KEY,
    profile_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    organization VARCHAR(160) NOT NULL,
    role VARCHAR(160) NOT NULL,
    description TEXT,
    started_on TIMESTAMPTZ,
    ended_on TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_experience_date_order
        CHECK (ended_on IS NULL OR started_on IS NULL OR ended_on >= started_on)
);
CREATE INDEX ix_experiences_profile ON experiences(profile_id);

CREATE TABLE projects (
    id UUID PRIMARY KEY,
    profile_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    title VARCHAR(160) NOT NULL CHECK (length(title) > 0),
    description TEXT,
    project_url VARCHAR(2048),
    visibility project_visibility NOT NULL DEFAULT 'private',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evidence_items (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(160) NOT NULL CHECK (length(title) > 0),
    description TEXT,
    evidence_url VARCHAR(2048),
    provenance VARCHAR(40) NOT NULL DEFAULT 'owner_submitted'
        CHECK (provenance IN ('owner_submitted', 'connected_source', 'third_party')),
    verification_status evidence_status NOT NULL DEFAULT 'self_reported',
    verifier_owner_id UUID REFERENCES owners(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    visibility evidence_visibility NOT NULL DEFAULT 'private',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_verified_evidence_has_auditor CHECK (
        (verification_status = 'verified' AND verifier_owner_id IS NOT NULL AND verified_at IS NOT NULL)
        OR (verification_status <> 'verified' AND verified_at IS NULL)
    )
);
CREATE INDEX ix_evidence_project ON evidence_items(project_id);
CREATE INDEX ix_evidence_status ON evidence_items(verification_status);
