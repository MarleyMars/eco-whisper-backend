-- Eco Whisper Demo Database Schema
-- This file contains all CREATE TABLE statements, indexes, and constraints

-- Users table for user management
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Intent table for mapping user queries to responses
CREATE TABLE IF NOT EXISTS Intent (
    intent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    requires_data_access BOOLEAN DEFAULT 0,
    response_template TEXT NOT NULL
);

-- Add question_patterns column if it doesn't exist
ALTER TABLE Intent ADD COLUMN question_patterns TEXT;

-- Electricity usage tracking per user
CREATE TABLE IF NOT EXISTS Electricity_Usage (
    usage_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    kwh_used DECIMAL(8,2) NOT NULL,
    estimated_cost DECIMAL(8,2),
    is_peak_time BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Community statistics
CREATE TABLE IF NOT EXISTS Community_Stats (
    stat_id TEXT PRIMARY KEY,
    community_id TEXT NOT NULL,
    date DATE NOT NULL,
    avg_kwh_per_user DECIMAL(8,2) NOT NULL,
    total_co2_saved DECIMAL(8,2) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Impact records for tracking environmental impact
CREATE TABLE IF NOT EXISTS Impact_Record (
    impact_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    impact_value DECIMAL(8,2) NOT NULL,
    impact_unit TEXT NOT NULL,
    impact_equivalent TEXT,
    impact_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Tips and advice
CREATE TABLE IF NOT EXISTS Tip (
    tip_id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    impact_value DECIMAL(8,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Conversation history
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    intent_matched TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (intent_matched) REFERENCES Intent (intent_id)
);

-- Smart meters for appliance tracking
CREATE TABLE IF NOT EXISTS smart_meters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meter_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    location TEXT,
    installation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Appliance usage tracking
CREATE TABLE IF NOT EXISTS appliance_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meter_id TEXT NOT NULL,
    appliance_name TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    kwh_consumed REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meter_id) REFERENCES smart_meters (meter_id)
);

-- Electricity rates for cost calculation
CREATE TABLE IF NOT EXISTS electricity_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rate_type TEXT NOT NULL,
    rate_per_kwh REAL NOT NULL,
    start_time TIME,
    end_time TIME,
    effective_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT 1
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_electricity_usage_user_date ON Electricity_Usage(user_id, date);
CREATE INDEX IF NOT EXISTS idx_community_stats_date ON Community_Stats(date);
CREATE INDEX IF NOT EXISTS idx_impact_record_user_date ON Impact_Record(user_id, date);
CREATE INDEX IF NOT EXISTS idx_conversations_user_timestamp ON conversations(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_appliance_usage_meter_time ON appliance_usage(meter_id, start_time);
CREATE INDEX IF NOT EXISTS idx_electricity_rates_effective_date ON electricity_rates(effective_date);

-- Create unique constraints
CREATE UNIQUE INDEX IF NOT EXISTS idx_electricity_usage_user_date_unique ON Electricity_Usage(user_id, date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_community_stats_community_date ON Community_Stats(community_id, date); 