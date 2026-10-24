"""Student CRUD API: class-style FastAPI + Supabase with regular def functions."""
import logging
import httpx
from fastapi import Depends, FastAPI, HTTPException, Path
from postgrest.exceptions import APIError
from supabase import Client
from database import get_client
from models import DeleteResult, Student, StudentInput

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
app = FastAPI(title="Student CRUD API", version="1.0.0")


def handle_error(error: Exception) -> None:
    """Preserve expected HTTP errors; hide raw database/connection details."""
    if isinstance(error, HTTPException):
        logger.warning("Request rejected: %s", error.detail)
        raise error
    if isinstance(error, APIError):
        logger.error("Database request failed (code=%s)", error.code)
        if error.code in ("PGRST205", "42P01"):
            raise HTTPException(503, "Student table is missing; run schema.sql") from error
        raise HTTPException(503, "Database request failed; check configuration") from error
    if isinstance(error, httpx.RequestError):
        logger.error("Database connection failed")
        raise HTTPException(503, "Database is unavailable") from error
    logger.error("Unexpected failure (%s)", type(error).__name__)
    raise HTTPException(500, "Internal server error") from error


def require_student(rows: list[dict], student_id: int) -> dict:
    """Reuse this check for GET, PUT, and DELETE results; [] means no match."""
    if not rows:
        raise HTTPException(404, f"Student {student_id} not found")
    return rows[0]


@app.post("/students", response_model=Student, status_code=201)
def create_student(data: StudentInput, client: Client = Depends(get_client)):
    """Insert validated fields; the database supplies the ID."""
    try:
        # model_dump() replaces the older .dict() shown in the class.
        response = client.table("student").insert(data.model_dump()).execute()
        logger.info("Student created")
        return response.data[0]
    except Exception as error:
        handle_error(error)


@app.get("/students", response_model=list[Student])
def list_students(client: Client = Depends(get_client)):
    """Return students in ID order, or an empty list."""
    try:
        response = client.table("student").select("*").order("id").execute()
        return response.data
    except Exception as error:
        handle_error(error)


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int = Path(..., gt=0), client: Client = Depends(get_client)):
    """Fetch one student; missing IDs return 404 instead of an empty success."""
    try:
        response = client.table("student").select("*").eq("id", student_id).execute()
        return require_student(response.data, student_id)
    except Exception as error:
        handle_error(error)


@app.put("/students/{student_id}", response_model=Student)
def update_student(data: StudentInput, student_id: int = Path(..., gt=0),
                   client: Client = Depends(get_client)):
    """Replace all four editable fields; preserve the database ID."""
    try:
        # The filter is essential: without it an update could affect every row.
        response = client.table("student").update(data.model_dump()).eq("id", student_id).execute()
        student = require_student(response.data, student_id)
        logger.info("Student updated: %s", student_id)
        return student
    except Exception as error:
        handle_error(error)


@app.delete("/students/{student_id}", response_model=DeleteResult)
def delete_student(student_id: int = Path(..., gt=0), client: Client = Depends(get_client)):
    """Delete only the requested row and return a confirmation with HTTP 200."""
    try:
        response = client.table("student").delete().eq("id", student_id).execute()
        require_student(response.data, student_id)
        logger.info("Student deleted: %s", student_id)
        return DeleteResult(message="Student deleted", student_id=student_id)
    except Exception as error:
        handle_error(error)
