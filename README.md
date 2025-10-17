# 🏥 AfyaAccess Healthcare Management System

AfyaAccess is a **comprehensive healthcare management system** built with **Django REST Framework** and Docker.  
It streamlines hospital operations through modular applications that manage **patients, consultations, pharmacy, billing, triage, and reports** — all secured with **token-based authentication**.

---

## 🚀 Project Overview

AfyaAccess is designed to improve healthcare delivery by integrating digital systems across departments.  
It enables secure patient data management, billing transparency, and better coordination between healthcare providers.

**Key Features**

- Centralized patient records
- Doctor–patient consultation tracking
- Pharmacy drug inventory management
- Automated billing and payment tracking
- Role-based authentication and authorization
- RESTful API endpoints for integration with mobile and web clients

---

## 🧭 Project Structure

Below is the simplified directory tree for the backend service:

```

AfyaAccess-Healthcare-Management-System/
│
├── backend/
│   ├── afyaaccess/                # Core Django project (settings, urls, wsgi)
│   ├── users/                     # Authentication and user management
│   ├── patients/                  # Patient registration and records
│   ├── consultation/              # Consultations, diagnoses, prescriptions
│   ├── pharmacy/                  # Drug inventory and dispensing
│   ├── billing/                   # Invoices, payments, and billing logic
│   ├── triage/                    # Vital signs, initial assessments
│   ├── reports/                   # Analytics and data summaries
│   └── manage.py
│
├── .env
├── .env_example
├── docker-compose.yml
└── README.md
├── requirements.txt

```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Benjamin-Kyalo/AfyaAccess-Healthcare-Management-System.git
cd AfyaAccess-Healthcare-Management-System
```

### 2. Build and Run Docker Containers

```bash
docker compose build
docker compose up -d
```

### 3. Apply Migrations and Load Initial Data

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py loaddata consultation/fixtures/drugs.json
```

### 4. Create a Superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

### 5. Access Services

- **Backend API:** `http://localhost:8000/api/`
- **pgAdmin:** `http://localhost:5050/`
- **Admin Panel:** `http://localhost:8000/admin/`

---

## 🔐 Authentication

AfyaAccess uses **token-based authentication (DRF Token Auth)**.

### Obtain Token

**Endpoint:**
`POST /api/users/login/`

**Request (raw JSON):**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**

```json
{
  "token": "a1b2c3d4e5f6..."
}
```

### Use Token in Postman

Add the following header to every request:

```
Authorization: Token a1b2c3d4e5f6...
```

---

## 🧩 Module Endpoints

Below are sample endpoints for each app (list is partial, showing 2–3 core routes per module):

### 👤 Users

| Method | Endpoint               | Description         |
| ------ | ---------------------- | ------------------- |
| `POST` | `/api/users/register/` | Register a new user |

---

### 🩺 Patients

| Method | Endpoint              | Description                 |
| ------ | --------------------- | --------------------------- |
| `GET`  | `/api/patients/`      | List all patients           |
| `POST` | `/api/patients/`      | Register a new patient      |
| `GET`  | `/api/patients/{id}/` | Retrieve a patient’s record |

---

### 💬 Consultation

| Method | Endpoint                   | Description                  |
| ------ | -------------------------- | ---------------------------- |
| `GET`  | `/api/consultations/`      | List all consultations       |
| `POST` | `/api/consultations/`      | Create a consultation record |
| `GET`  | `/api/consultations/{id}/` | Get consultation details     |

---

### 💊 Pharmacy

| Method | Endpoint                    | Description               |
| ------ | --------------------------- | ------------------------- |
| `GET`  | `/api/pharmacy/drugs/`      | View available drugs      |
| `POST` | `/api/pharmacy/drugs/`      | Add new drug to inventory |
| `GET`  | `/api/pharmacy/drugs/{id}/` | Get details of a drug     |

---

### 💰 Billing

| Method | Endpoint                         | Description                     |
| ------ | -------------------------------- | ------------------------------- |
| `GET`  | `/api/billing/`                  | List all bills                  |
| `POST` | `/api/billing/`                  | Create a new billing record     |
| `POST` | `/api/billing/{id}/add-payment/` | Record a payment against a bill |

---

### 🧾 Reports

| Method | Endpoint                 | Description                   |
| ------ | ------------------------ | ----------------------------- |
| `GET`  | `/api/reports/overview/` | Get system-wide summaries     |
| `GET`  | `/api/reports/patients/` | View patient activity reports |
| `GET`  | `/api/reports/billing/`  | Get billing analytics         |

---

### 🩹 Triage

| Method | Endpoint            | Description              |
| ------ | ------------------- | ------------------------ |
| `GET`  | `/api/triage/`      | List triage assessments  |
| `POST` | `/api/triage/`      | Create new triage record |
| `GET`  | `/api/triage/{id}/` | Retrieve triage details  |

---

## 🧠 Developer Notes

- Use `TokenAuthentication` in DRF for all protected routes.
- Ensure Docker volumes are **not removed** when restarting (`avoid using -v`).
- To reset data selectively:

  ```bash
  docker compose exec backend python manage.py flush
  ```

- Run automated tests:

  ```bash
  docker compose exec backend python manage.py test
  ```

---

## 🩷 Authors & Credits

**Benjamin Kyalo** — Project Manager & UX Researcher
Guided by **ALX Africa Capstone Team**

AfyaAccess is part of a mission to leverage **technology for equitable healthcare access in rural Kenya**.

---
