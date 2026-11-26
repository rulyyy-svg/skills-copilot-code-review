# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View and filter extracurricular activities
- Manage student registrations while signed in
- Publish database-backed announcements with optional start dates and required expiration dates

## Getting Started

1. From the repository root, install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get announcements currently within their display dates              |
| POST   | `/auth/login?username=...&password=...`                            | Sign in and receive a bearer token                                  |
| GET    | `/auth/check-session`                                             | Validate the bearer token and return the signed-in teacher          |
| POST   | `/auth/logout`                                                    | Invalidate the current bearer token                                 |
| GET    | `/announcements/manage`                                           | List all announcements (signed-in teachers only)                    |
| POST   | `/announcements`                                                  | Create an announcement (signed-in teachers only)                   |
| PUT    | `/announcements/{id}`                                             | Update an announcement (signed-in teachers only)                   |
| DELETE | `/announcements/{id}`                                             | Delete an announcement (signed-in teachers only)                   |

Announcement writes use JSON with `title`, `message`, and required
`expiration_date` (`YYYY-MM-DD`). `start_date` is optional. Send the token
returned by login as `Authorization: Bearer <token>` for session and
announcement-management endpoints. The example announcement is inserted by
`backend/database.py` when the announcements collection is empty.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activities, teachers, announcements, and login sessions are stored in MongoDB.
