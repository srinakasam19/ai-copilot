-- Create analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id VARCHAR(255) PRIMARY KEY,
    repo_url VARCHAR(500) NOT NULL,
    repo_name VARCHAR(255),
    commit_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    tree_structure JSON,
    tech_stack JSON,
    architecture JSON,
    security JSON,
    code_quality JSON,
    documentation JSON,
    interview_questions JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(255) PRIMARY KEY,
    analysis_id VARCHAR(255) REFERENCES analyses(id) ON DELETE CASCADE,
    sender VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    sources JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
