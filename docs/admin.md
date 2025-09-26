# IELTS Admin Panel Documentation

## Overview
The IELTS Admin Panel provides comprehensive management capabilities for administrators to control all aspects of the IELTS practice platform including test content, user management, and system statistics.

## Authentication

### Admin Login
Administrators can log in using predefined credentials to access the admin panel.

**Endpoint:** `POST /auth/admin/login`

**Request Body:**
```json
{
  "email": "admin@gmail.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 0,
  "email": "admin@gmail.com",
  "full_name": "Admin",
  "is_admin": true
}
```

**Response Fields:**
- `access_token`: JWT token for authentication (expires in 60 minutes)
- `token_type`: Always "bearer"
- `user_id`: Always 0 for admin
- `email`: Admin email address
- `full_name`: Display name "Admin"
- `is_admin`: Always true for admin users

### Using the JWT Token
All admin endpoints require the JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Admin Capabilities

### 1. Test Management
- **Speaking Tests**: Create, read, update, delete speaking tests and questions
- **Reading Tests**: Manage reading tests, passages, and question packs
- **Writing Tests**: Control writing tests and tasks (Academic/General)
- **Listening Tests**: Handle listening tests, sections, and question packs

### 2. User Management
- View all registered users
- Activate/deactivate user accounts
- Delete user accounts
- View user statistics and test history

### 3. Dashboard & Analytics
- System-wide statistics
- Recent submissions monitoring
- Test overview across all skills
- User activity tracking

## Separated Admin Endpoints

The admin panel is organized into separate modules for each IELTS skill:

- `/admin/speaking/*` - Speaking test management
- `/admin/reading/*` - Reading test management  
- `/admin/writing/*` - Writing test management
- `/admin/listening/*` - Listening test management
- `/admin/dashboard/*` - User management and statistics

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Admin-Only Access**: All admin endpoints require admin privileges
3. **Token Expiration**: Admin tokens expire after 60 minutes
4. **Environment Variables**: Admin credentials stored in environment variables
5. **Role Separation**: Clear separation between admin and user roles

## Error Handling

All admin endpoints return appropriate HTTP status codes:

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient privileges (non-admin user)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Example error response:
```json
{
  "detail": "Admin access required"
}
```

## Rate Limiting & Security

- Admin sessions are limited to 60-minute JWT tokens
- All admin operations are logged
- Database operations use transactions for data integrity
- Input validation on all request bodies
- SQL injection protection through SQLAlchemy ORM