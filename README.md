Perfect request, Benjamin 👌 — since I’ve now gone through all your apps (users, accounts, patients, pharmacy, triage, lab, billing, consultation, reports), I can prepare a **full end-to-end `README.md`** for your AfyaAccess project.

This README will be **human-like**, **clear**, and **developer-friendly**. It will:

- Explain the project purpose.
- Show folder structure.
- Document each app’s role.
- Include setup instructions.
- Show example API usage.
- Mention improvements & next steps.

Here’s the draft 👇

---

# 🏥 AfyaAccess Healthcare Management System

AfyaAccess is a **modular hospital management system** built with **Django REST Framework** and **React (frontend planned)**.
It aims to improve healthcare delivery in hospitals and rural clinics by providing **patient registration, billing, lab, pharmacy, triage, consultations, and reporting tools** in one integrated platform.

---

## 🚀 Features

- 👩‍⚕️ **User Management**: Staff login, roles (doctor, nurse, pharmacist, admin, etc.), JWT authentication.
- 🧑‍🤝‍🧑 **Patient Management**: Register, update, and track patients.
- 💉 **Triage Module**: Record vital signs & initial assessments.
- 💊 **Pharmacy**: Manage medicines, stock, and prescriptions.
- 🔬 **Laboratory**: Request and complete lab tests.
- 🩺 **Consultations**: Manage doctor-patient consultations.
- 💵 **Billing**: Track consultation, lab, and pharmacy charges; separate paid vs unpaid bills.
- 📊 **Reports**: Generate summaries (patients, billing, consultations, triage).

---

## 🗂️ Project Structure

```
AfyaAccess-Healthcare-Management-System/
│── accounts/        # Registration & JWT authentication
│── users/           # Custom user model with roles
│── patients/        # Patient records & management
│── triage/          # Vital signs & triage records
│── consultation/    # Doctor consultations
│── pharmacy/        # Drug inventory & prescriptions
│── lab/             # Lab test requests & results
│── billing/         # Bills & payments
│── reports/         # Reporting & analytics
│── backend/         # Django project config
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AfyaAccess-Healthcare-Management-System.git
cd AfyaAccess-Healthcare-Management-System
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

Ensure PostgreSQL is installed & running. Create a database:

```sql
CREATE DATABASE afyaaccess_db;
```

Update `settings.py` with your DB credentials.

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

---

## 🔑 Authentication

- Uses **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`.
- Obtain tokens:

  - `POST /accounts/login/` → returns `access` + `refresh`.

- Refresh token:

  - `POST /accounts/token/refresh/`.

---

## 📌 API Endpoints (Examples)

### Users

```
POST   /accounts/register/       # Register a new user
POST   /accounts/login/          # Login with JWT
GET    /users/                   # List all users
```

### Patients

```
POST   /patients/                # Register patient
GET    /patients/                # List patients
GET    /patients/{id}/           # Patient details
```

### Triage

```
POST   /triage/                  # Record triage data
GET    /triage/                  # List all triage records
```

### Billing

```
GET    /billing/                 # All bills
GET    /billing/{id}/            # Single bill
```

### Reports

```
GET    /reports/summary/         # High-level system summary
GET    /reports/patients/        # Patient statistics
GET    /reports/billing/         # Billing statistics
GET    /reports/consultations/   # Consultation statistics
GET    /reports/triage/          # Triage statistics
```

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 📊 Future Improvements

- ✅ **Date filters** for reports (daily, weekly, monthly trends).
- ✅ **Role-based permissions** (e.g., billing only visible to admins).
- ✅ **Aggregate queries** to optimize report queries.
- ✅ **Unit & integration tests** for all apps.
- ✅ **Frontend React app** for a modern hospital dashboard.
- ✅ **Docker setup** for deployment.

---

## 👨‍💻 Contributors

- **Benjamin Kyalo** – Project Manager & Developer
- ALX Software Engineering inspiration
