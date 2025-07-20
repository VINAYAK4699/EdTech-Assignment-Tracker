# 🎓 EdTech Assignment Tracker – FastAPI + HTML Frontend

## ✅ Objective

This project implements a simplified **assignment tracking system** for an EdTech platform. Teachers can post assignments, students can submit them, and teachers can view submissions. Authentication is handled via JWT, and a simple HTML frontend is provided.

---

## ✅ Part A: System Design (Written)

### 1. Core Entities and Their Relationships

| Entity         | Attributes                                                                                      |
| -------------- | ----------------------------------------------------------------------------------------------- |
| **User**       | id (PK), username, password, role (student/teacher)                                             |
| **Assignment** | id (PK), title, description, created\_by (FK to User), created\_at                              |
| **Submission** | id (PK), assignment\_id (FK to Assignment), student\_id (FK to User), file\_path, submitted\_at |

#### Relationships:

* **User** (Teacher) can **create multiple Assignments**.
* **User** (Student) can **submit Submissions** for **Assignments**.
* **Assignments** can have **multiple Submissions** from students.

### 2. API Endpoints

| Endpoint                                   | Method | Description                                   | Access              |
| ------------------------------------------ | ------ | --------------------------------------------- | ------------------- |
| `/signup`                                  | POST   | Register a new user (student/teacher)         | Public              |
| `/login`                                   | POST   | Login and receive JWT token                   | Public              |
| `/assignments/create`                      | POST   | Teacher creates an assignment                 | Auth (Teacher Only) |
| `/assignments/{assignment_id}/submit`      | POST   | Student submits assignment (with file upload) | Auth (Student Only) |
| `/assignments/{assignment_id}/submissions` | GET    | Teacher views submissions                     | Auth (Teacher Only) |

### 3. Authentication Strategy

* Authentication is done using **JWT tokens**.
* **/signup** and **/login** are public.
* JWT token is required in the `Authorization` header for other routes.
* **Role-Based Access Control (RBAC)** ensures:

  * Teachers can create assignments and view submissions.
  * Students can only submit assignments.

### 4. Scaling Strategy (Suggestions for Future Improvements)

* **Database:** Migrate from SQLite to PostgreSQL (already supported).
* **File Storage:** Move file uploads from local directory to AWS S3 / Cloud Storage for scalability.
* **Asynchronous Processing:** Use async SQLAlchemy and FastAPI’s async features to improve performance.
* **Pagination:** Add pagination to submissions API for large data handling.
* **Dockerization:** Use Docker for containerization and easier deployment.
* **Deployment:** Deploy on cloud platforms (e.g., AWS, Azure, GCP) with Nginx + Gunicorn.

---

## ✅ Part B: Prototype Implementation

### Technology Stack

* **Backend:** FastAPI (Python)
* **Frontend:** Plain HTML, CSS, and Vanilla JavaScript served via FastAPI static files
* **Database:** SQLite (with option to switch to PostgreSQL)
* **Authentication:** JWT tokens
* **File Upload:** `multipart/form-data` file uploads supported
* **API Docs:** Swagger/OpenAPI available at `/docs`

### Directory Structure

```
Edtech Assignment Tracker/
│
├── main.py                     # FastAPI backend
├── submissions/                # Folder for storing uploaded files
├── assignment_tracker.db       # SQLite Database (auto-created)
├── static/                     # Frontend static files
│   ├── signup.html
│   ├── login.html
│   ├── create-assignment.html
│   ├── submit-assignment.html
│   ├── submissions.html
│   └── style.css
└── README.md
```

### How to Run the Project

1. **Clone the Repository**

```bash
git clone <your-repo-url>
cd Edtech Assignment Tracker
```

2. **Setup Virtual Environment**

```bash
python -m venv fastapi-env
source fastapi-env/bin/activate  # Linux/MacOS
fastapi-env\Scripts\activate     # Windows
```

3. **Install Requirements**

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-multipart jwt
```

4. **Run the Application**

```bash
uvicorn main:app --reload
```

5. **Access Application**

* API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Frontend Pages:

  * [Signup](http://127.0.0.1:8000/static/signup.html)
  * [Login](http://127.0.0.1:8000/static/login.html)
  * [Create Assignment (Teacher)](http://127.0.0.1:8000/static/create-assignment.html)
  * [Submit Assignment (Student)](http://127.0.0.1:8000/static/submit-assignment.html)
  * [View Submissions (Teacher)](http://127.0.0.1:8000/static/submissions.html)

---

## 📝 Conclusion

This EdTech Assignment Tracker fulfills the core requirements of:

* 🎯 Secure Role-based assignment management
* 🎯 Interactive API with OpenAPI/Swagger docs
* 🎯 Functional HTML + CSS frontend
* 🎯 Room for scalability and enhancements

✅ Suitable for demonstration of practical API design, authentication, and basic frontend integration in an EdTech context.
