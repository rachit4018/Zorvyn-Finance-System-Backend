from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, transactions, summary, users

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Tracking System",
    description=(
        "A Python/FastAPI backend for managing personal financial records. "
        "Supports role-based access (viewer, analyst, admin), CRUD on transactions, "
        "and financial summaries."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(summary.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Finance Tracking API is running"}


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )
