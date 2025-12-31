# HRMS Project - README

## Project Structure

This HRMS (Human Resource Management System) project is organized into separate backend and frontend folders:

```
/Users/murari/LMS/
├── backend/          # FastAPI Python backend with all endpoints
└── frontend/         # Flutter cross-platform frontend application
```

---

## Backend (FastAPI)

### Location
`backend/`

### Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server runs on: `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Available Endpoints

**Authentication:**
- POST `/auth/register` - Register user with organization
- POST `/auth/login` - Login 
- GET `/auth/me` - Get current user
- POST `/auth/refresh` - Refresh token
- POST `/auth/logout` - Logout

**Users:**
- GET/POST `/users/`
- GET/PUT/DELETE `/users/{id}`

**Organization Management:**
- `/organizations/`, `/branches/`, `/departments/`

**Learning Management:**
- `/courses/`, `/videos/`, `/enrollments/`, `/progress/`, `/quiz-checkpoints/`

**Recruitment:**
- `/job-postings/`, `/job-descriptions/`, `/candidates/`, `/candidates-documents/`

**Attendance & Leave:**
- `/attendance/`, `/attendance-punch/`, `/leavemaster/`, `/holidays/`, `/permissions/`

**Shift Management:**
- `/shifts/`, `/shift-rosters/`, `/user-shifts/`, `/shift-change-requests/`

**Payroll:**
- `/salary-structures/`, `/formulas/`, `/payroll/`, `/payroll-attendance/`

**System:**
- `/roles/`, `/menus/`, `/role-rights/`

---

## Frontend (Flutter)

### Location
`frontend/`

### Setup

```bash
cd frontend
flutter pub get
flutter run
```

### Platforms Supported
- ✅ Web
- ✅ iOS
- ✅ Android

### Architecture

```
lib/
├── core/              # Configuration, theme, utils
├── data/              # Models, services, repositories
├── presentation/      # Screens and widgets
└── state/             # State management (Provider)
```

### Key Features

- **Authentication:** Login, Register, Token management
- **Dashboard:** User stats, organization info, quick actions
- **Navigation:** Dynamic menu from backend
- **State Management:** Provider pattern
- **API Integration:** Dio with interceptors
- **Secure Storage:** Token and user data persistence
- **Theme:** Modern Material 3 design

### Configuration

API URL is configured in:
```dart
// lib/core/config/app_config.dart
static const String apiBaseUrl = 'http://localhost:8000';
```

---

## Getting Started

### 1. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Start Frontend

```bash
cd frontend
flutter run -d chrome  # For web
# or
flutter run  # Select device
```

### 3. Test the Application

1. Open app (goes to login screen)
2. Click "Register" to create new account
3. Fill in details and register
4. Automatically logged in to dashboard
5. View organization stats and menu

---

## Development

### Adding New Modules

1. **Create Service** in `frontend/lib/data/services/`
2. **Create Model** in `frontend/lib/data/models/`
3. **Create Provider** in `frontend/lib/state/providers/`
4. **Create Screen** in `frontend/lib/presentation/screens/`
5. **Add Route** in `frontend/lib/main.dart`
6. **Register Provider** in `main.dart`

### Code Quality

Run Flutter analyzer:
```bash
cd frontend
flutter analyze
```

Current status: ✅ **No issues found!**

---

## Documentation

- **Implementation Plan:** See `implementation_plan.md` in artifacts
- **Walkthrough:** See `walkthrough.md` in artifacts
- **Task Tracking:** See `task.md` in artifacts

---

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL/SQLite
- JWT Authentication
- Alembic Migrations

### Frontend
- Flutter 3.9+
- Dart
- Provider (State Management)
- Dio (HTTP Client)
- Go Router (Routing)
- Flutter Secure Storage

---

## Next Steps

1. Test authentication end-to-end with backend
2. Implement remaining modules (Users, Courses, Attendance, etc.)
3. Add more screens and functionality
4. Implement role-based access control in UI
5. Add comprehensive error handling
6. Create unit and integration tests
7. Deploy to staging/production

---

## Support

For questions or issues, review the walkthrough document in the artifacts directory.
