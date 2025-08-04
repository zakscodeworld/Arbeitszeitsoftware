# Email System Documentation

## Overview

The application includes an email notification system for important events such as:

1. Work hour notifications when hours are under or over the standard 8-hour workday
2. Absence request notifications (when submitted, approved, or rejected)
3. Password change confirmations
4. New account creation notifications

## Configuration

Email settings are configured through environment variables:

- `EMAIL_ENABLED`: Set to "true" to enable email sending (default: false)
- `SMTP_SERVER`: SMTP server address (default: smtp.example.com)
- `SMTP_PORT`: SMTP port (default: 465 for SSL)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `SENDER_EMAIL`: Email address to send from (default: noreply@example.com)
- `SENDER_NAME`: Display name for the sender (default: BBQ GmbH Zeiterfassung)
- `APP_URL`: Base URL of the application for links in emails (default: http://localhost:8000)
- `ENVIRONMENT`: Current environment (development, testing, production)

## Setup Instructions

1. Copy the `.env.example` file to `.env` in the backend directory:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file to set your SMTP server details:
   ```
   EMAIL_ENABLED=true
   SMTP_SERVER=your-smtp-server.com
   SMTP_PORT=465  # or 587 for TLS
   SMTP_USERNAME=your-username
   SMTP_PASSWORD=your-secure-password
   SENDER_EMAIL=your-email@example.com
   SENDER_NAME=Your Application Name
   APP_URL=https://your-application-url.com
   ENVIRONMENT=production  # or development/testing
   ```

3. Restart the application to apply the settings:
   ```
   docker-compose down
   docker-compose up -d
   ```

## Email Types

### Work Hours Notification
Sent when a time entry is created with hours that are significantly different from the standard 8-hour workday.

### Absence Notifications
- **Submitted**: When a new absence request is created
- **Approved**: When a manager approves an absence request
- **Rejected**: When a manager rejects an absence request

### Password Change Notification
Sent to confirm when a user has changed their password.

### Account Creation
Sent when a new user account is created.

## Troubleshooting

If emails are not being sent:

1. Check if `EMAIL_ENABLED` is set to "true" in your environment variables
2. Verify SMTP credentials are correct
3. Check application logs for error messages related to email sending
4. Try using different SMTP ports (465 for SSL, 587 for TLS, 25 for non-encrypted)
5. Make sure your SMTP server allows sending from the specified `SENDER_EMAIL`

## Security Notes

- SMTP passwords should be kept secure and not committed to version control
- In development environments, email sending is disabled by default
- The system uses SSL/TLS encryption for secure email communication
