-- SQL schema for Agent Suite core tables.
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    education TEXT[],
    skills TEXT[],
    interests TEXT[],
    normalized_profile JSONB DEFAULT '{}'::jsonb,
    embedding JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    source TEXT,
    title TEXT,
    company TEXT,
    location TEXT,
    url TEXT,
    description TEXT,
    structured_data JSONB DEFAULT '{}'::jsonb,
    ranking_score DOUBLE PRECISION DEFAULT 0,
    posted_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE application_status AS ENUM ('draft', 'submitted', 'interview', 'offer', 'rejected', 'withdrawn');

CREATE TABLE IF NOT EXISTS resume_variants (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id),
    job_id INTEGER REFERENCES job_postings(id),
    variant_name TEXT,
    content TEXT,
    ats_score DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS application_logs (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES profiles(id),
    job_id INTEGER REFERENCES job_postings(id),
    status application_status DEFAULT 'draft',
    cover_letter TEXT,
    recruiter_email TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
