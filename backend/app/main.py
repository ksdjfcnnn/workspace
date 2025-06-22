from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import auth
from app.api.admin import employees, projects, tasks, analytics
from app.api.user import profile, projects as user_projects, tasks as user_tasks, time_tracking, screenshots

app = FastAPI(
    title=settings.APP_NAME,
    description="Employee Time Tracking API compatible with Insightful",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Admin routes
app.include_router(employees.router, prefix="/api/v1/employee", tags=["Admin - Employees"])
app.include_router(projects.router, prefix="/api/v1/project", tags=["Admin - Projects"])
app.include_router(tasks.router, prefix="/api/v1/task", tags=["Admin - Tasks"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Admin - Analytics"])

# User routes
app.include_router(profile.router, prefix="/api/v1/user", tags=["User - Profile"])
app.include_router(user_projects.router, prefix="/api/v1/user/projects", tags=["User - Projects"])
app.include_router(user_tasks.router, prefix="/api/v1/user/tasks", tags=["User - Tasks"])
app.include_router(time_tracking.router, prefix="/api/v1/user/time-tracking", tags=["User - Time Tracking"])
app.include_router(screenshots.router, prefix="/api/v1/user/screenshots", tags=["User - Screenshots"])


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=12000)