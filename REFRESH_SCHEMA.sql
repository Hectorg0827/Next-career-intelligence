-- Force Supabase PostgREST to reload schema cache
NOTIFY pgrst, 'reload schema';

-- Verify jobs table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'jobs'
ORDER BY ordinal_position;
