# Insightful API Backend - Deployment Guide

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Navigate to backend directory
cd backend

# Copy environment template
cp .env.example .env

# Edit environment variables
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

### 4. Start the Application

```bash
# Using the startup script (recommended)
python start_server.py

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/verify-email` - Email verification
- `POST /api/v1/auth/forgot-password` - Password reset request
- `POST /api/v1/auth/reset-password` - Password reset

### Admin Endpoints
- `POST /api/v1/employee/` - Create employee
- `GET /api/v1/employee/` - List employees
- `PUT /api/v1/employee/{id}` - Update employee
- `POST /api/v1/employee/deactivate/{id}` - Deactivate employee
- `POST /api/v1/project/` - Create project
- `GET /api/v1/project/` - List projects
- `PUT /api/v1/project/{id}` - Update project
- `DELETE /api/v1/project/{id}` - Delete project
- `POST /api/v1/task/` - Create task
- `PUT /api/v1/task/{id}` - Update task
- `DELETE /api/v1/task/{id}` - Delete task
- `GET /api/v1/analytics/project-time` - Time analytics
- `GET /api/v1/analytics/screenshot` - Screenshot data

### User Endpoints
- `GET /api/v1/user/me` - Get profile
- `GET /api/v1/user/me/stats` - Get statistics
- `GET /api/v1/user/projects/` - Get assigned projects
- `GET /api/v1/user/tasks/` - Get assigned tasks
- `POST /api/v1/user/time-tracking/start` - Start time tracking
- `POST /api/v1/user/time-tracking/end` - End time tracking
- `GET /api/v1/user/time-tracking/active` - Get active session
- `GET /api/v1/user/time-tracking/history` - Get tracking history
- `POST /api/v1/user/screenshots/` - Upload screenshot
- `GET /api/v1/user/screenshots/` - Get screenshots

## 🧪 Testing

```bash
# Run all tests
python run_tests.py

# Run specific test files
pytest app/tests/test_auth.py -v
pytest app/tests/test_admin_employees.py -v
pytest app/tests/test_user_time_tracking.py -v

# Generate coverage report
pytest app/tests/ --cov=app --cov-report=html
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./insightful.db  # or PostgreSQL URL

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

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:12000/docs
- **ReDoc**: http://localhost:12000/redoc
- **OpenAPI JSON**: http://localhost:12000/openapi.json

## 🔐 Authentication Flow

### Admin Workflow
1. Admin creates employee account via API
2. Employee receives email verification link
3. Employee sets password via verification
4. Employee can login with email/password
5. JWT token provided for API access

### User Workflow
1. Login with verified credentials
2. Access assigned projects and tasks
3. Start/stop time tracking sessions
4. Upload screenshots during work
5. View personal statistics

## 🏗️ Architecture

### Database Models
- **Organization**: Company data
- **Team**: Team within organization
- **Employee**: User accounts with roles
- **Project**: Work projects with assignments
- **Task**: Individual tasks within projects
- **Shift**: Time tracking sessions
- **Screenshot**: Work session screenshots

### Service Layer
- **EmployeeService**: Employee management
- **ProjectService**: Project operations
- **TaskService**: Task management
- **ShiftService**: Time tracking
- **ScreenshotService**: Screenshot handling
- **EmailService**: Email notifications

### Security Features
- JWT token authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Email verification for new accounts
- CORS protection
- Input validation and sanitization

## 🚀 Production Deployment

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

### Environment Setup

```bash
# Production environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/insightful_prod
export SECRET_KEY=your-production-secret-key
export SENDGRID_API_KEY=your-sendgrid-api-key
export FRONTEND_URL=https://your-frontend-domain.com
```

### Database Migration

```bash
# Run migrations in production
alembic upgrade head
```

## 📊 Monitoring

### Health Check
- `GET /health` - Application health status

### Logging
- Application logs to stdout
- Error tracking with detailed stack traces
- Request/response logging for debugging

## 🔄 API Compatibility

This backend maintains full compatibility with the Insightful API specification:

- **Original camelCase naming**: All field names use camelCase as per Insightful API
- **Identical response structures**: Responses match Insightful API format exactly
- **Compatible endpoints**: All endpoints follow Insightful API patterns
- **Same data models**: Database models mirror Insightful API specifications

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL in .env file
   - Ensure database server is running
   - Verify database credentials

2. **Email Not Sending**
   - Check SENDGRID_API_KEY configuration
   - Verify FROM_EMAIL is authorized in SendGrid
   - Check SendGrid account status

3. **Authentication Failures**
   - Verify SECRET_KEY is set correctly
   - Check token expiration settings
   - Ensure user email is verified

4. **CORS Issues**
   - Update BACKEND_CORS_ORIGINS in .env
   - Check frontend URL configuration
   - Verify request headers

### Debug Mode

```bash
# Run with debug logging
uvicorn app.main:app --host 0.0.0.0 --port 12000 --log-level debug
```

## 📝 Development

### Adding New Features

1. Create database models in `app/models/`
2. Add Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Create API endpoints in `app/api/`
5. Write tests in `app/tests/`
6. Update documentation

### Code Quality

```bash
# Run linting
flake8 app --max-line-length=100

# Format code
black app

# Type checking
mypy app
```

## 🔗 External Services

### SendGrid Email Service
- Account setup required for email functionality
- API key configuration in environment variables
- Email templates for verification and password reset

### Database Support
- **SQLite**: Development and testing
- **PostgreSQL**: Production recommended
- **MySQL**: Supported via SQLAlchemy

## 📈 Performance

### Optimization Tips
- Use database connection pooling
- Implement Redis caching for sessions
- Add database indexes for frequently queried fields
- Use async endpoints for I/O operations
- Implement pagination for large datasets

### Scaling
- Deploy multiple instances behind load balancer
- Use separate read/write database replicas
- Implement background task processing with Celery
- Add monitoring with Prometheus/Grafana