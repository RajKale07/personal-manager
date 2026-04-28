# Product Overview — Personal Manager

## Purpose
A web-based personal document management system that helps users track important documents, get notified before expiry, and manage renewal tasks. Built as a college DBMS project using Flask and MySQL.

## Key Features
- User registration and login with session-based authentication
- Add and view personal documents (name, authority, issue/expiry dates, importance)
- Expiry notifications: warning banner for documents expiring within 30 days, urgent alert for ≤7 days
- Expired document tracking with auto-created renewal tasks
- Task management: view and mark renewal tasks as done
- Document issuance guide (ISSUE_GUIDE) with step-by-step procedures and required documents for common Indian government IDs (Passport, Driving License, Aadhaar, PAN, Voter ID, etc.)
- Admin panel: view all users and all documents across the system

## Target Users
- Individual users managing personal government/identity documents
- Admin (single hardcoded admin@example.com) for oversight

## Use Cases
- Track expiry of Passport, Driving License, Insurance, Vehicle RC, etc.
- Get reminded before documents expire
- Know what documents are needed to apply for a new document
- Admin monitoring of all registered users and their documents
