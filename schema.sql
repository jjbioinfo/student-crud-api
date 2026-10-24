-- Run ONCE in a dedicated Supabase project, separate from course enrollment.
-- No DROP: if student already exists, inspect it rather than deleting class data.
BEGIN;
CREATE TABLE public.student (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL CHECK (length(trim(name)) BETWEEN 3 AND 50),
    email text NOT NULL,
    age integer NOT NULL CHECK (age > 18 AND age < 100),
    course text NOT NULL CHECK (length(trim(course)) BETWEEN 2 AND 100)
);
-- The local backend uses a service_role key, never a browser/anonymous key.
ALTER TABLE public.student ENABLE ROW LEVEL SECURITY;
GRANT ALL ON public.student TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.student_id_seq TO service_role;
COMMIT;
-- Starts empty: create students through POST /students during the demonstration.
