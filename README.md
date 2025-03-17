# TCE-contactWeb
## TCE Contacts Management System

A Flask web application for managing university contacts, replacing an Excel-based system. Features CRUD operations, dynamic dropdowns, CSV exports, and hierarchical college-department-course relationships.

## Features
- View/search/filter contacts
- Add/edit/delete contacts
- Export to CSV
- College-department-course hierarchy
- Primary contact validation
- Course coordinator management

## File Structure
├── app.py # Main application logic
├── contacts.csv # Generated contacts database
├── hierarchy.csv # University hierarchy data
├── templates/
│ ├── base.html # Base template
│ ├── index.html # Contact list + filters
│ ├── add_contact.html # Add contact form
│ └── edit_contact.html # Edit contact form
└── static/
└── script.js # Optional JavaScript helpers

## Requirements
- Python 3.x
- Flask

## How to Run
```  python .\app.py         ```
- Access at: http://localhost:5000