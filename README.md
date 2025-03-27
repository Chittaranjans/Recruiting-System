# Recruitment Tracking System - Backend

A comprehensive recruitment management API built with FastAPI and PostgreSQL that helps companies manage their hiring process efficiently.

## 🚀 Features

- **Authentication System**: Secure JWT-based authentication with role-based permissions
- **User Management**: Support for different roles (Admin, Recruiter, Interviewer, Candidate)
- **Job Posting Management**: Create and manage job listings
- **Candidate Tracking**: Track candidates through the recruitment process
- **Interview Management**: Schedule interviews and record feedback
- **Kanban Board**: Visual representation of candidate status
- **Notification System**: Track and notify about recruitment events

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: SQL toolkit and ORM
- **JWT**: Token-based authentication
- **Docker**: Containerization for easy deployment

## 📋 API Endpoints

The API is organized around the following resources:

- `/api/v1/auth/*`: Authentication endpoints
- `/api/v1/jobs/*`: Job posting management
- `/api/v1/candidates/*`: Candidate management
- `/api/v1/interviews/*`: Interview scheduling and feedback
- `/api/v1/kanban/*`: Kanban board functionality
- `/api/v1/notifications/*`: Notification system

<div align="center">
  <img src="Screenshot 2025-03-27 171353.png" alt="API Documentation" width="300px" style="margin: 10px" />
  <img src="Screenshot 2025-03-27 171416.png" alt="Endpoints" width="300px" style="margin: 10px" />
  <img src="Screenshot 2025-03-27 171436.png" alt="API Schema" width="300px" style="margin: 10px" />
</div>

## 🔧 Setup and Installation

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for PostgreSQL database)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Chittaranjans/Recruiting-System

   ```

2. Start the PostgreSQL database:
   ```bash
   docker-compose up -d
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```bash
   python dbInit.py
   ```

6. Create admin user:
   ```bash
   python create_admin.py
   ```

7. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

8. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔐 Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. Register a user: `POST /api/v1/auth/register`
2. Login to get a token: `POST /api/v1/auth/login`
3. Use the token in the Authorization header: `Bearer YOUR_TOKEN`

## 🧪 Testing

Coming soon.

## 📱 Frontend Repository

The frontend for this application is available at: 
