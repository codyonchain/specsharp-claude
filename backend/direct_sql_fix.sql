-- IMMEDIATE FIX FOR POSTGRESQL
-- Run this directly in PostgreSQL to fix the issue NOW

-- Add all missing columns with safe IF NOT EXISTS
ALTER TABLE projects 
ADD COLUMN IF NOT EXISTS subtotal FLOAT,
ADD COLUMN IF NOT EXISTS contingency_percentage FLOAT DEFAULT 10.0,
ADD COLUMN IF NOT EXISTS contingency_amount FLOAT,
ADD COLUMN IF NOT EXISTS cost_per_sqft FLOAT,
ADD COLUMN IF NOT EXISTS project_classification VARCHAR DEFAULT 'ground_up',
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS building_type VARCHAR,
ADD COLUMN IF NOT EXISTS occupancy_type VARCHAR,
ADD COLUMN IF NOT EXISTS cost_data TEXT,
ADD COLUMN IF NOT EXISTS team_id INTEGER,
ADD COLUMN IF NOT EXISTS created_by_id INTEGER,
ADD COLUMN IF NOT EXISTS scenario_name VARCHAR;

-- Update existing projects with calculated values
UPDATE projects 
SET 
    subtotal = COALESCE(subtotal, total_cost / 1.1),
    contingency_percentage = COALESCE(contingency_percentage, 10.0),
    contingency_amount = COALESCE(contingency_amount, (total_cost / 1.1) * 0.1),
    cost_per_sqft = COALESCE(cost_per_sqft, total_cost / NULLIF(square_footage, 0))
WHERE total_cost IS NOT NULL;

-- Verify the fix worked
SELECT 
    COUNT(*) as total_projects,
    COUNT(subtotal) as projects_with_subtotal,
    COUNT(contingency_percentage) as projects_with_contingency
FROM projects;

-- Show sample project to verify
SELECT 
    project_id,
    name,
    subtotal,
    contingency_percentage,
    contingency_amount,
    total_cost,
    cost_per_sqft
FROM projects
LIMIT 5;