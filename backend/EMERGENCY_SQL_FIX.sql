-- EMERGENCY SQL FIX FOR PRODUCTION
-- If Python script fails, run this SQL directly in PostgreSQL

-- STEP 1: Add all missing columns (safe with IF NOT EXISTS)
ALTER TABLE projects ADD COLUMN IF NOT EXISTS subtotal DOUBLE PRECISION;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS contingency_percentage DOUBLE PRECISION DEFAULT 10.0;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS contingency_amount DOUBLE PRECISION;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_per_sqft DOUBLE PRECISION;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS project_classification VARCHAR(50) DEFAULT 'ground_up';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS building_type VARCHAR(100);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS occupancy_type VARCHAR(100);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS scenario_name VARCHAR(100);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS team_id INTEGER;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS created_by_id INTEGER;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_data TEXT;

-- STEP 2: Update existing projects with calculated values
UPDATE projects 
SET 
    subtotal = COALESCE(subtotal, total_cost / 1.1),
    contingency_percentage = COALESCE(contingency_percentage, 10.0),
    contingency_amount = COALESCE(contingency_amount, total_cost * 0.0909),
    cost_per_sqft = COALESCE(cost_per_sqft, 
        CASE WHEN square_footage > 0 THEN total_cost / square_footage ELSE NULL END),
    project_classification = COALESCE(project_classification, 'ground_up')
WHERE total_cost IS NOT NULL;

-- STEP 3: Verify the fix
SELECT 
    COUNT(*) as total_projects,
    COUNT(subtotal) as with_subtotal,
    COUNT(contingency_percentage) as with_contingency,
    COUNT(cost_per_sqft) as with_cost_per_sqft
FROM projects;

-- STEP 4: Show sample to verify all columns work
SELECT 
    project_id,
    name,
    subtotal,
    contingency_percentage,
    contingency_amount,
    total_cost,
    cost_per_sqft,
    project_classification
FROM projects
LIMIT 3;

-- If successful, you should see:
-- ✓ All columns exist
-- ✓ Projects have calculated values
-- ✓ No errors when querying