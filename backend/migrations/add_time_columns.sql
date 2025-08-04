-- Add startzeit and endzeit columns to zeiteintraege table
-- First add columns as nullable to allow for existing data
ALTER TABLE zeiteintraege 
ADD COLUMN IF NOT EXISTS startzeit TIME,
ADD COLUMN IF NOT EXISTS endzeit TIME;

-- Update any existing records with default values (8:00 AM to 5:00 PM)
-- This ensures we don't have NULL values in existing records
UPDATE zeiteintraege
SET startzeit = '08:00:00',
    endzeit = '17:00:00'
WHERE startzeit IS NULL OR endzeit IS NULL;

-- Now set the columns to NOT NULL to match the model definition
ALTER TABLE zeiteintraege
ALTER COLUMN startzeit SET NOT NULL,
ALTER COLUMN endzeit SET NOT NULL;
