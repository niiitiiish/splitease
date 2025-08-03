# SplitEase 💸
[link](https://splitease-a4m5.onrender.com/):
**SplitEase** is a simple and efficient expense-splitting web app built using **FastAPI** and **PostgreSQL**. It helps groups of people keep track of shared expenses and automatically calculates who owes whom.

---

## 🚀 Features

* ✅ User registration and login (optional)
* 🏨 Group creation and management
* ➕ Add expenses with descriptions, payer, and split info
* 📊 View who owes what within a group
* 📥 Retrieve all notifications (e.g., in-app, email, SMS support planned)
* 🔁 Planned support for background task queues and retries

---

## 🚠 Tech Stack

| Tool                                                        | Purpose                      |
| ----------------------------------------------------------- | ---------------------------- |
| [FastAPI](https://fastapi.tiangolo.com/)                    | Backend web framework        |
| [PostgreSQL](https://www.postgresql.org/)                   | Relational database          |
| [SQLAlchemy](https://www.sqlalchemy.org/)                   | ORM for database interaction |
| [Jinja2](https://jinja.palletsprojects.com/)                | HTML templating              |
| [HTML/CSS/JS](https://developer.mozilla.org/en-US/docs/Web) | Frontend templates           |

---

## 📁 Folder Structure

```
splitease/
│
├── main.py                 # Entry point with all routes
├── models.py               # SQLAlchemy models for User, Group, Expense, etc.
├── schemas.py              # Pydantic schemas for request/response validation
├── database.py             # Database connection and session management
├── templates/              # HTML templates for frontend
├── static/                 # Static files (CSS, JS)
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/niiitiiish/splitease.git
cd splitease
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your PostgreSQL database

Create a `.env` file or modify `database.py` with your DB credentials:

```python
DATABASE_URL = "postgresql://username:password@localhost/splitease"
```

### 5. Run the app

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` in your browser.

---

## 🧪 API Endpoints Overview

| Method | Endpoint                    | Description                  |
| ------ | --------------------------- | ---------------------------- |
| GET    | `/users/{id}/notifications` | Get notifications for a user |
| POST   | `/groups`                   | Create a new group           |
| POST   | `/groups/{id}/expenses`     | Add an expense to a group    |
| GET    | `/groups/{id}/balance`      | View who owes whom           |

---

## 🧹 To-Do / Future Enhancements

* [ ] Add authentication (OAuth or JWT)
* [ ] Integrate Celery or background tasks for retrying failed notifications
* [ ] Add email/SMS notification support
* [ ] Create a modern frontend (React/Vue/Alpine.js)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Acknowledgments

* Thanks to the FastAPI, SQLAlchemy, and PostgreSQL communities.
* Inspired by the Splitwise app concept.
