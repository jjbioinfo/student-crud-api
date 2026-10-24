# Student CRUD API: run and record

## Preparation

1. Use a dedicated Supabase project and run schema.sql once in SQL Editor. One empty student table is created. Do not run this over the Course Enrollment database's student table.
2. Fill the private .env with SUPABASE_URL and the server-side SUPABASE_KEY. Show .env.example during recording, never the real key.
3. Run each command separately:

```bash
cd /Users/JJOHN41/Documents/my_learning/euron_super30/assignment/october/2_student_CRUD_API
```

```bash
source /Users/JJOHN41/Documents/my_learning/euron_super30/.venv/bin/activate
```

```bash
python -m unittest -v test_api
```

Expected: 11 tests, OK. These are offline tests; the live demonstration checks the configured database.

```bash
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs. Stop any earlier assignment using port 8000 first. Leave this terminal running while demonstrating.

## Explain the problem

“CRUD means create, read, update, and delete. This application manages student records with FastAPI. Pydantic validates input, and Supabase stores the data.”

## Demonstrate the APIs

Use Try it out → Execute in Swagger. Use the actual returned ID instead of assuming it is 1.

1. GET /students: 200 and [] on a fresh table.
2. POST /students using:

```json
{"name":"Asha","email":"asha@example.com","age":22,"course":"Python"}
```

Expected 201; note the generated ID.

3. GET /students: 200, array containing the student.
4. GET /students/{student_id}: 200, one student object.
5. PUT /students/{student_id} using all editable fields:

```json
{"name":"Asha John","email":"asha@example.com","age":23,"course":"FastAPI"}
```

Expected 200, same ID with updated fields. GET it again to confirm persistence.

6. POST with email changed to not-an-email: 422.
7. POST with age changed to 18: 422; explain the class's age rule is 19–99.
8. PUT with course missing: 422; explain full replacement requires all fields.
9. GET a confirmed nonexistent student ID: 404.
10. DELETE the created student: 200 and confirmation.
11. GET the deleted ID: 404. Repeat DELETE: 404.
12. GET /students: [] if this was the only student.

For Postman, use raw JSON bodies and the same paths/methods.

## Explain the important code

- models.py: BaseModel, Field, EmailStr, strict integer ages, generated ID, and rejecting extra fields.
- database.py: load_dotenv, environment variables, create_client, Depends, and caching the client. See README for definitions.
- main.py: The five decorators, regular def functions, direct Supabase query chains, ID filters, response.data, shared missing-student check, try/except, and logger.
- schema.sql: Primary key (unique row identifier), identity (database ID generation), column constraints, and backend database access.
- test_api.py: Tests simulate the database using the real Supabase SDK and check requests/results. They do not validate the live hosted database.

## Publish and submit

Stop Uvicorn with Ctrl+C. Copy the commands in git_workflow.sh one at a time. This folder already has Git initialized, but had no commits or remote when prepared. The workflow includes your Git name/email and the planned repository URL. Pause at the browser step to create the empty public repository yourself.

Show the repository files and README, upload your video, and submit the actual GitHub and YouTube URLs. The planned repository is jjbioinfo/student-crud-api; its remote availability has not been checked.
