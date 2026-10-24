# Validation — 23 October 2026

Command: python -m unittest -v test_api

Result: **11 offline tests passed** using the course Python environment. Tests use FastAPI TestClient, the real Supabase Python SDK, and HTTPX MockTransport to simulate database responses. No live Supabase calls or credentials are used.

| Scenario | Expected and observed |
|---|---|
| Create Asha, age 22, valid email, Python | 201; generated ID and trimmed strings; correct insert JSON |
| Empty/populated list | 200; [] or list; ID ordering |
| Fetch existing/missing student | Record or descriptive 404; correct ID filter |
| PUT all editable fields, then repeat | 200; ID preserved; full validated payload and exact ID filter |
| PUT nonexistent ID | 404; update only, no insert |
| DELETE existing then missing | 200 confirmation, then 404; exact ID filter |
| Missing/null/extra fields, invalid strings/email/age | 422; no database requests |
| Names 3 and 50, ages 19 and 99, courses 2 and 100 characters | Accepted boundaries |
| Invalid URL IDs, missing/malformed JSON | 422; no database requests |
| Missing tables, permissions error, network failure | 503; raw diagnostic details not exposed |
| Unexpected error in any endpoint | Generic 500 |
| Missing settings and documentation | 503 for database route; Swagger and five route definitions available |

Not verified: execution of schema.sql, hosted table constraints, real persistence, live credentials/RLS, manual Swagger/Postman clicks, fresh dependency installation, GitHub publication, or video recording/upload. The private .env is blank and must be filled locally. No claim of live database readiness is made.
