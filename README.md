# Salary Tracker — Project Roadmap

**Version:** 1.0  
**Project type:** Full-stack web application  
**Status:** Planning / Ready for Development  
**Currency:** Malaysian Ringgit (MYR)

---

# 1. Project Overview

## 1.1 Objective

Build a full-stack web application that allows users to record, manage, track and analyse their income from different sources.

The application is designed for people with multiple or irregular income streams, including tutors, freelancers, students and part-time workers.

The goal is to create a simple, intuitive and reliable income tracking application that can eventually evolve into a more comprehensive financial management platform.

## 1.2 Target Users

- Private tutors
- Freelancers
- Part-time workers
- University students
- Individuals with multiple income streams

## 1.3 Core Principles

- Simple and intuitive user experience.
- Accurate financial calculations.
- Secure user authentication.
- Reliable data storage.
- Maintainable and modular code.
- Responsive desktop and mobile interface.

---

# 2. Technology Stack

| Layer | Technology |
|---|---|
| Programming language | Python |
| Backend framework | Flask |
| Database | SQLite |
| Database interface | Python `sqlite3` |
| Frontend | HTML5, CSS3 |
| CSS framework | Bootstrap 5 |
| Templating engine | Jinja |
| Client-side programming | JavaScript |
| Data visualization | Chart.js |
| Password hashing | Werkzeug |
| Version control | Git and GitHub |

### Development principles

- Do not use the CS50 library or CS50 helper functions.
- Use Python's built-in `sqlite3` module.
- Use standard Flask functionality.
- Understand the implementation rather than blindly copying code.
- Keep the application simple and avoid unnecessary dependencies.
- Use Git commits throughout development.

---

# 3. Functional Requirements

## FR-01: User Authentication

Users must be able to:

- Register an account using a username and password.
- Log in using their credentials.
- Log out securely.
- Maintain authenticated sessions.
- Receive appropriate validation errors.
- Access only their own data.

Security requirements:

- Hash passwords using Werkzeug.
- Never store plaintext passwords.
- Prevent duplicate usernames.
- Protect authenticated routes.
- Prevent unauthorized access to other users' records.
- Validate all user input on the server.

## FR-02: Income Management

Users must be able to:

- Create income records.
- View all their income records.
- Edit existing income records.
- Delete existing income records.
- View individual income record details.

### Income Record Structure

| Field | Type | Required |
|---|---|---|
| ID | Integer | Yes |
| User ID | Integer | Yes |
| Date | Date | Yes |
| Income Type | Text | Yes |
| Description | Text | No |
| Quantity | Integer | Yes |
| Rate Per Unit | Integer (sen) | Yes |
| Total | Calculated | Yes |

### Income Calculation

Total income = Quantity × Rate per unit.

Example:

| Date | Type | Quantity | Rate | Total |
|---|---|---:|---:|---:|
| 01/11/2026 | Teaching | 3 | RM25 | RM75 |
| 02/11/2026 | Event | 1 | RM80 | RM80 |
| 03/11/2026 | Freelance | 2 | RM50 | RM100 |

Each record must preserve its own rate so that changing a user's usual rate does not alter historical earnings.

Money should be stored as integer sen to avoid floating-point inaccuracies.

Example:
- RM25.00 = 2500
- RM80.50 = 8050

## FR-03: Income Categories

Initial income categories:

- Teaching
- Freelance
- Event
- Other

Users should be able to distinguish between different income sources when reviewing their earnings.

## FR-04: Dashboard

The dashboard should display:

- Total monthly income.
- Total yearly income.
- Number of income records this month.
- Average earnings per record.
- Recent income records.
- Monthly income chart.
- Income breakdown by category.

## FR-05: Search, Filtering and Sorting

Users should be able to:

- Filter records by month.
- Filter records by year.
- Filter records by income type.
- Filter records using a date range.
- Sort records by date.
- Sort records by total earnings.

## FR-06: Analytics

The application should calculate:

- Monthly income.
- Yearly income.
- Total income by category.
- Monthly income trends.
- Average income per record.

---

# 4. Non-Functional Requirements

| Requirement | Description |
|---|---|
| Security | Secure authentication and protected routes |
| Data isolation | Users cannot access other users' records |
| Accuracy | Monetary calculations avoid floating-point errors |
| Usability | Intuitive and easy-to-use interface |
| Responsiveness | Compatible with desktop and mobile |
| Maintainability | Modular, readable and organized code |
| Reliability | Invalid inputs must not crash the application |
| Performance | Efficient database queries and page loading |

---

# 5. Database Design

The initial database will contain two tables.

## 5.1 Users Table

| Column | Data Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Unique user ID |
| username | TEXT UNIQUE | Account username |
| password_hash | TEXT | Hashed password |
| created_at | TEXT | Account creation timestamp |

## 5.2 Income Records Table

| Column | Data Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Unique record ID |
| user_id | INTEGER FOREIGN KEY | Record owner |
| date | TEXT | Income date |
| income_type | TEXT | Income category |
| description | TEXT | Optional description |
| quantity | INTEGER | Number of units |
| rate_per_unit | INTEGER | Rate in sen |

The total can be calculated using quantity multiplied by rate per unit.

### Database Relationship

One user can have multiple income records.

Every income record belongs to exactly one user.

---

# 6. User Interface Requirements

## Design Direction

**Theme:** Minimalist, warm beige and neutral.

Design characteristics:

- Warm beige background.
- Neutral sidebar.
- Clean typography.
- Simple navigation.
- Rounded dashboard cards.
- Clear data visualization.
- Consistent spacing.
- Responsive layouts.

## Main Pages

1. Login
2. Registration
3. Dashboard
4. Income Records
5. Add Income
6. Edit Income

---

# 7. Proposed Project Structure

```text
salary-tracker/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   └── salary.db
│
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── records.html
│   ├── add.html
│   └── edit.html
│
├── static/
│   ├── css/
│   │   └── styles.css
│   │
│   └── js/
│       ├── main.js
│       └── charts.js
│
└── tests/
    ├── test_auth.py
    ├── test_income.py
    └── test_database.py
```

This is a proposed structure. We can introduce additional modules as the application grows.

---

# 8. Development Roadmap

## Milestone 1: Flask Foundation

- [ ] Create project directory.
- [ ] Set up virtual environment.
- [ ] Install Flask.
- [ ] Create Flask application.
- [ ] Configure routes.
- [ ] Understand HTTP GET and POST requests.
- [ ] Implement Jinja templates.
- [ ] Implement template inheritance.
- [ ] Connect static CSS and JavaScript files.

**Deliverable:** A functioning Flask application with multiple pages.

## Milestone 2: Frontend Foundation

- [ ] Establish the beige design system.
- [ ] Create navigation sidebar.
- [ ] Create dashboard layout.
- [ ] Create income records page.
- [ ] Create add income form.
- [ ] Create edit income form.
- [ ] Create login page.
- [ ] Create registration page.
- [ ] Make layouts responsive.

**Deliverable:** Complete frontend with placeholder data.

## Milestone 3: Database Foundation

- [ ] Understand SQLite and relational databases.
- [ ] Create database connection.
- [ ] Create users table.
- [ ] Create income records table.
- [ ] Establish foreign key relationships.
- [ ] Implement database queries.
- [ ] Implement parameterized SQL queries.
- [ ] Handle database transactions.

**Deliverable:** Application connected to SQLite.

## Milestone 4: Income Management (CRUD)

- [ ] Implement Create functionality.
- [ ] Implement Read functionality.
- [ ] Implement Update functionality.
- [ ] Implement Delete functionality.
- [ ] Implement income calculations.
- [ ] Implement input validation.
- [ ] Implement error handling.

**Deliverable:** Fully functional income management system.

## Milestone 5: Authentication and Security

- [ ] Implement registration.
- [ ] Implement password hashing.
- [ ] Implement login.
- [ ] Implement logout.
- [ ] Configure Flask sessions.
- [ ] Implement route protection.
- [ ] Implement user-specific database queries.
- [ ] Test data isolation between users.
- [ ] Configure secure session settings.

**Deliverable:** Secure multi-user application.

## Milestone 6: Dashboard and Analytics

- [ ] Calculate monthly earnings.
- [ ] Calculate yearly earnings.
- [ ] Calculate average earnings.
- [ ] Calculate income by category.
- [ ] Retrieve recent records.
- [ ] Implement monthly income chart.
- [ ] Connect Chart.js to database data.

**Deliverable:** Dynamic dashboard with real financial data.

## Milestone 7: Search and Filtering

- [ ] Implement month filtering.
- [ ] Implement year filtering.
- [ ] Implement category filtering.
- [ ] Implement date range filtering.
- [ ] Implement sorting by date.
- [ ] Implement sorting by earnings.

**Deliverable:** Functional record search and filtering.

## Milestone 8: Testing and Polish

- [ ] Test registration and login.
- [ ] Test CRUD operations.
- [ ] Test database relationships.
- [ ] Test input validation.
- [ ] Test authorization and data isolation.
- [ ] Test monetary calculations.
- [ ] Test responsive layouts.
- [ ] Handle edge cases.
- [ ] Improve error messages.
- [ ] Review code organization.

**Deliverable:** Stable and reliable application.

## Milestone 9: Documentation and Deployment

- [ ] Write project README.
- [ ] Document installation instructions.
- [ ] Document technologies used.
- [ ] Document application features.
- [ ] Add screenshots.
- [ ] Record demonstration video.
- [ ] Deploy the application.

**Deliverable:** Completed portfolio-ready project.

---

# 9. Features Excluded from Version 1

To prevent scope creep, the following features are reserved for future versions:

- Expense tracking.
- Bank account integration.
- Stock portfolio tracking.
- AI financial advice.
- Receipt scanning.
- Multiple currencies.
- Recurring income automation.
- Native mobile application.
- Automated financial predictions.

---

# 10. Definition of Done

Salary Tracker Version 1.0 will be considered complete when:

1. Users can register and log in securely.
2. Users can create, view, edit and delete income records.
3. Every user can only access their own records.
4. Income calculations are accurate.
5. Monthly and yearly summaries work correctly.
6. Income categories are displayed accurately.
7. Search, filtering and sorting work.
8. Dashboard charts display actual database data.
9. The application works on desktop and mobile.
10. Core functionality has been tested.
11. Documentation is available.
12. The project is published on GitHub and deployed.

---

# 11. Development Philosophy

This project is also intended to develop practical software engineering skills.

Development rules:

- Understand before implementing.
- Break large features into smaller tasks.
- Avoid unnecessary abstractions.
- Write readable and maintainable code.
- Test features as they are developed.
- Use Git commits to track progress.
- Debug systematically instead of randomly changing code.
- Use AI as a tutor and reviewer, not as a replacement for understanding.

**Final objective:** Build a complete, secure and usable full-stack income tracking application independently, with the ability to explain its architecture, implementation and design decisions.