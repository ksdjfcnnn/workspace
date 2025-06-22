# Insightful API Backend

A comprehensive FastAPI backend for employee time tracking and management, compatible with the Insightful API specification. This system provides role-based access control (RBAC) with separate admin and user interfaces for managing employees, projects, tasks, and time tracking.

## 🚀 Features

### Admin Features
- **Employee Management**: Create, update, deactivate employees with email verification
- **Project Management**: Create and manage projects with employee assignments
- **Task Management**: Create and assign tasks to employees
- **Analytics**: View time tracking analytics, screenshots, and productivity metrics
- **Organization Management**: Full control over organization data

### User Features
- **Time Tracking**: Start/stop time tracking sessions with project and task assignment
- **Project Access**: View assigned projects and tasks
- **Personal Dashboard**: View personal statistics and time tracking history
- **Screenshot Management**: Upload and view screenshots during work sessions

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Separate admin and user permissions
- **Email Verification**: Secure employee onboarding process
- **Password Security**: Bcrypt hashing with secure password policies

## 📋 API Compatibility

This backend is designed to be plug-and-play compatible with the Insightful API, maintaining:
- Original camelCase naming conventions
- Identical response structures
- Compatible endpoint patterns
- Same data models and relationships

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database (SQLite for testing)
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **SendGrid**: Email service integration
- **Pytest**: Comprehensive testing framework

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                    # API route handlers
│   │   ├── admin/             # Admin-only endpoints
│   │   ├── auth/              # Authentication endpoints
│   │   └── user/              # User endpoints
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── security.py        # Security utilities
│   │   └── deps.py            # Dependency injection
│   ├── db/                    # Database configuration
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic layer
│   ├── tests/                 # Test suite
│   └── main.py               # FastAPI application
├── alembic/                   # Database migrations
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the backend directory
cd backend

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 4. Start the Server

```bash
# Using the startup script (recommended)
python start_server.py

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload
```

The API will be available at:
- Local: http://localhost:12000
- Documentation: http://localhost:12000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/insightful_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourcompany.com

# Application
APP_NAME=Insightful API
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Database Configuration

The application supports both PostgreSQL (production) and SQLite (development/testing):

**PostgreSQL (Recommended for production):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/insightful_db
```

**SQLite (Development):**
```env
DATABASE_URL=sqlite:///./insightful.db
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/verify-email` - Email verification and password setup
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with token

### Admin Endpoints

**Employee Management:**
- `POST /api/v1/employee/` - Create employee
- `GET /api/v1/employee/` - List employees
- `GET /api/v1/employee/{id}` - Get employee
- `PUT /api/v1/employee/{id}` - Update employee
- `POST /api/v1/employee/deactivate/{id}` - Deactivate employee

**Project Management:**
- `POST /api/v1/project/` - Create project
- `GET /api/v1/project/` - List projects
- `PUT /api/v1/project/{id}` - Update project
- `DELETE /api/v1/project/{id}` - Delete project

**Analytics:**
- `GET /api/v1/analytics/project-time` - Time analytics
- `GET /api/v1/analytics/screenshot` - Screenshot data

### User Endpoints

**Profile:**
- `GET /api/v1/user/me` - Get current user profile
- `GET /api/v1/user/me/stats` - Get user statistics

**Time Tracking:**
- `POST /api/v1/user/time-tracking/start` - Start time tracking
- `POST /api/v1/user/time-tracking/end` - End time tracking
- `GET /api/v1/user/time-tracking/active` - Get active session
- `GET /api/v1/user/time-tracking/history` - Get tracking history

## 🧪 Testing

### Run All Tests

```bash
# Using the test runner script
python run_tests.py

# Or manually
pytest app/tests/ -v
```

### Run Specific Test Categories

```bash
# Authentication tests
pytest app/tests/test_auth.py -v

# Admin functionality tests
pytest app/tests/test_admin_*.py -v

# User functionality tests
pytest app/tests/test_user_*.py -v
```

### Coverage Report

```bash
pytest app/tests/ --cov=app --cov-report=html
# View coverage report at htmlcov/index.html
```

## 🔐 Security Considerations

### Authentication Flow

1. **Admin Creates Employee**: Admin creates employee account via API
2. **Email Verification**: Employee receives verification email
3. **Password Setup**: Employee sets password via verification link
4. **Login**: Employee can now login with email/password
5. **JWT Token**: Secure token provided for API access

### Role-Based Access Control

- **Admin Users**: Full access to all endpoints and organization data
- **Regular Users**: Limited to personal data and assigned projects/tasks
- **Deactivated Users**: Cannot login or access any endpoints

### Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- Email verification for new accounts
- CORS protection
- Input validation and sanitization

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**:
   ```bash
   # Set production environment variables
   export DATABASE_URL=postgresql://...
   export SECRET_KEY=...
   export SENDGRID_API_KEY=...
   ```

2. **Database Migration**:
   ```bash
   alembic upgrade head
   ```

3. **Start Application**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Database Schema

### Core Models

- **Organization**: Company/organization data
- **Team**: Team within organization
- **Employee**: User accounts with roles
- **Project**: Work projects with assignments
- **Task**: Individual tasks within projects
- **Shift**: Time tracking sessions
- **Screenshot**: Work session screenshots

### Relationships

- Organizations contain Teams and Employees
- Projects belong to Organizations and have assigned Employees
- Tasks belong to Projects and have assigned Employees
- Shifts track time against Projects and Tasks
- Screenshots are captured during Shifts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test files for usage examples
- Create an issue for bugs or feature requests

## 🔄 API Compatibility

This backend maintains full compatibility with the Insightful API specification:

- **Employee API**: Complete CRUD operations with deactivation
- **Project API**: Full project management with team assignments
- **Task API**: Task creation and assignment with project relationships
- **Time Tracking API**: Comprehensive shift management and analytics
- **Screenshot API**: Screenshot capture and retrieval with permissions

All endpoints use the original camelCase naming convention and maintain identical response structures for seamless integration.