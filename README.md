# Notification Preference APIs

## Project Description
This project provides REST APIs for managing user notification preferences, including types of notifications and user-specific settings for frequency, email, push, and SMS preferences.

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/premkumar0/notification-preference-management-api.git
   ```

2. **Create a Virtual Environment: (for Linux based OS)**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Required Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations to Set Up the Database: (Optional)**

   db.sqlite3 file attached if needed feel free to delete the file and run below command
   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser for Admin Access:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Development Server:**

   ```bash
   python manage.py runserver
   ```

## Instructions on How to Run the Project
1. Use the `create_notification_types` management command or the provided API to create notification types.
2. Utilize the provided APIs to manage notification preferences.

## API Endpoints

### Notification Types
- **GET /api/notification-types/**: Retrieve all notification types.
- **POST /api/notification-types/**: Create a new notification type. *(Accessible only for admins; login with admin credentials required)*

### Notification Preferences
- **GET /api/notification-preferences/**: Retrieve the authenticated user's notification preferences.
- **POST /api/notification-preferences/update_preferences/**: Update the authenticated user's notification preferences.

## Testing the APIs
- Use the Django Rest Framework's browsable API to manually test APIs, logging in as both an admin user and a normal user.
- Run the test suite using the command:
  ```bash
  python manage.py test
  ```
