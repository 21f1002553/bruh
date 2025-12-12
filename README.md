# SE Project – School HRM Solution

Software Engineering Project – Sept 2025, Team 18

---

## Problem Statement

### Problem Statement 1: HRM Solution for Schools

Design and build a **web-based Human Resource Management (HRM) System** tailored for schools and educational institutions.

The application features a comprehensive HRM solution for schools, including modules for staff hiring, management, evaluations, and internal coordination among teachers, HR personnel, and administrators. The application also includes AI-powered modules for resume screening, job matching, automated candidate evaluation, and document summarization. Additionally, the application provides portals for different user roles, including **HR, HO, BDA, and candidate**, each with authorized access and tailored functionality.

The goal is to deliver a **real-world HRM solution** improving efficiency, transparency, and collaboration within schools.

---

## Project Structure

```
backend
├── app.py
├── chroma_db
│   ├── 384fd469-8f1b-43ee-8929-fa7b68dc9f63
│   │   ├── data_level0.bin
│   │   ├── header.bin
│   │   ├── length.bin
│   │   └── link_lists.bin
│   ├── chroma.sqlite3
│   └── fd561184-f65c-43f5-a112-222a8d29219f
│       ├── data_level0.bin
│       ├── header.bin
│       ├── length.bin
│       └── link_lists.bin
├── chroma_rag_chatbot
│   └── chroma.sqlite3
├── config.py
├── database
│   └── vector_db
│       ├── __init__.py
│       └── chroma_vector_db.py
├── extensions.py
├── genai
│   ├── llm_factory
│   │   ├── __init__.py
│   │   └── llm_factory_service.py
│   ├── llm_models
│   │   ├── __init__.py
│   │   ├── base_llm_model.py
│   │   └── llm_model_implementation.py
│   ├── prompt
│   │   ├── __init__.py
│   │   └── prompt_manager.py
│   ├── schema
│   │   ├── __init__.py
│   │   └── schema_manager.py
│   └── services
│       ├── __init__.py
│       ├── ai_review_service.py
│       ├── chatbot_service.py
│       ├── expense_service.py
│       ├── recommendation_service.py
│       └── resume_service.py
├── init_db.py
├── instance
│   └── hr_system.db
├── models.py
├── requirements.txt
├── routes
│   ├── ai_routes.py
│   ├── application_routes.py
│   ├── auth_routes.py
│   ├── eod_routes.py
│   ├── expense_routes.py
│   ├── file_routes.py
│   ├── job_routes.py
│   ├── leave_routes.py
│   ├── notification_routes.py
│   ├── onboarding_routes.py
│   ├── pipeline_routes.py
│   ├── reporting_routes.py
│   ├── role_routes.py
│   ├── salary_routes.py
│   ├── screening_routes.py
│   ├── task_routes.py
│   ├── training_routes.py
│   ├── user_routes.py
│   └── vacancy_routes.py
├── run.py
├── tests
│   ├── conftest.py
│   ├── test_ai_routes.py
│   ├── test_application_routes.py
│   ├── test_auth_routes.py
│   ├── test_eod_routes.py
│   ├── test_expense_routes.py
│   ├── test_file_routes.py
│   ├── test_job_routes.py
│   ├── test_leave_routes.py
│   ├── test_notification_routes.py
│   ├── test_onboarding_routes.py
│   ├── test_pipeline_routes.py
│   ├── test_reporting_routes.py
│   ├── test_role_routes.py
│   ├── test_salary_routes.py
│   ├── test_screening_routes.py
│   ├── test_training_routes.py
│   ├── test_user_routes.py
│   └── test_vacancy_routes.py
├── uploads
│   ├── documents
│   ├── files
│   │   ├── 00ccd40d-0fd8-465c-9bb1-a52ce17fd03b_40b783c2bd0e251ab648e825d3bea14a.pdf
│   │   ├── 253b6bb3-863b-42c0-8a21-56cb8295f38d_40b783c2bd0e251ab648e825d3bea14a.pdf
│   │   └── 486ec5a8-67a8-4aaf-bef3-9cb73c1881ec_40b783c2bd0e251ab648e825d3bea14a.pdf
│   ├── offer_letters
│   │   └── 97673935-9f43-45c8-9241-b42675af74e6
│   ├── receipts
│   └── resumes
└── utils
    ├── __init__.py
    ├── file_utils.py
    ├── text_utility.py
    └── validation_json.py

24 directories, 80 files

frontend
├── INSTRUCTIONS.md
├── README.md
├── index.html
├── package-lock.json
├── package.json
├── public
│   ├── hr.jpg
│   └── vite.svg
├── src
│   ├── App.vue
│   ├── assets
│   │   ├── styles
│   │   │   └── candidate.css
│   │   └── vue.svg
│   ├── components
│   │   ├── AITestModal.vue
│   │   ├── AdminDashboard.vue
│   │   ├── AdminEODForm.vue
│   │   ├── ApplyForm.vue
│   │   ├── BDABehavioralInterviewPage.vue
│   │   ├── BDADashboard.vue
│   │   ├── BDAEODPage.vue
│   │   ├── BDAExpensePage.vue
│   │   ├── BDALeavePage.vue
│   │   ├── BDANotificationsPage.vue
│   │   ├── CandidateApplicationsPage.vue
│   │   ├── CandidateCoursePage.vue
│   │   ├── CandidateDashboard.vue
│   │   ├── CandidateJobRecommendations.vue
│   │   ├── CandidateJobSearch.vue
│   │   ├── CandidateLeavePage.vue
│   │   ├── CandidateNotificationsPage.vue
│   │   ├── CandidateOnboarding.vue
│   │   ├── CandidatePerformance.vue
│   │   ├── CandidateProfile.vue
│   │   ├── CandidateTakingTest.vue
│   │   ├── CandidateTasks.vue
│   │   ├── CandidateUpskillingPage.vue
│   │   ├── CandidateVacanciesPage.vue
│   │   ├── DashboardLayout.vue
│   │   ├── ExpenseManagement.vue
│   │   ├── HODashboard.vue
│   │   ├── HOLeavePage.vue
│   │   ├── HONotificationsPage.vue
│   │   ├── HOTechnicalInterviews.vue
│   │   ├── HOVacancyPage.vue
│   │   ├── HRApplications.vue
│   │   ├── HRCourseManagement.vue
│   │   ├── HRDashboard.vue
│   │   ├── HREmployees.vue
│   │   ├── HRExpenseReports.vue
│   │   ├── HRJobPostings.vue
│   │   ├── HRLeavePage.vue
│   │   ├── HRNotificationsPage.vue
│   │   ├── HROnboarding.vue
│   │   ├── HRPerformanceReviews.vue
│   │   ├── HiringPipeline.vue
│   │   ├── HomePage.vue
│   │   ├── InterviewAssignmentModal.vue
│   │   ├── InterviewDetailsModal.vue
│   │   ├── InterviewDetailsPage.vue
│   │   ├── JobApplicationModal.vue
│   │   ├── JobDetailsModal.vue
│   │   ├── JobPostModal.vue
│   │   ├── JobPosting.vue
│   │   ├── LoginPage.vue
│   │   ├── ManagerDashboard.vue
│   │   ├── OnboardingPage.vue
│   │   ├── ReportingPage.vue
│   │   ├── ResumeModal.vue
│   │   ├── ResumeUploadModal.vue
│   │   ├── ScorecardModal.vue
│   │   ├── ScreeningPage.vue
│   │   ├── SignupPage.vue
│   │   ├── TaskManagement.vue
│   │   ├── TeacherEODForm.vue
│   │   ├── TestResultsModal.vue
│   │   ├── VacancyList.vue
│   │   └── ai_profile_enhancement.vue
│   ├── main.js
│   ├── router
│   │   └── index.js
│   ├── stores
│   │   ├── auth.js
│   │   ├── counter.js
│   │   └── recruitment.js
│   └── style.css
└── vite.config.js

8 directories, 81 files
```

---

# Getting Started

## Backend Setup

### 1. Go to Backend Directory
```bash
cd backend
```
### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate (for windows)
source venv/bin/activate (for linux) 
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Initialize Database 
```bash
python init_db.py
```
### 5. Run the backend server
```bash
python run.py

```
### Testing
```bash
# Run all tests
pytest tests/

# Test API manually
curl http://localhost:5001/health
```
---

## Frontend Setup

### 1. Go to frontend directory
```bash
cd frontend
```

### 2. Install npm dependencies
```bash
npm install
```

### 3. Start frontend server
```bash
npm run dev
```

## Environment Variables

Create a `.env` file:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///hr_system.db
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
DATA_ROOT=your-project-location
```

---

# Features

1. Multi-Role User System
   - HR, HO, BDA, Candidate
   - Role-based authentication & authorization

2. Recruitment Management
   - Job posting & applications
   - AI-based resume screening
   - Candidate shortlisting suggestions

3. AI Integration
   - Resume parsing
   - Skill extraction
   - Job-role matching
   - Automated candidate evaluation
   - Document summarization

4. Employee Records
   - Digital employee profiles
   - Leave management

5. Training Module
   - Academic logs
   - Announcements & tasks

6. HR Dashboard
   - Employee onboarding
   - Document management
   - Analytics & reporting

7. Candidate Dashboard
   - AI Performance Mansgement
   - AI Job Recommendations & Auto Apply
   - AI upskilling & Profile Enhancement
 
---

# Technology Stack

## Frontend
- Vue.js 3 (Vue CLI)
- HTML5, CSS3, JavaScript (ES6+)
- Axios for API communication
- Vite for development and build

## Backend
- Flask (Python)
- SQLAlchemy ORM
- Flask-JWT-Extended for authentication
- Flask-CORS for cross-origin resource sharing
- Flask-Migrate for database migrations
- Flask-SQLAlchemy for database operations

## Database
- SQLite

## AI Modules
- AI/ML: Google Gemini
- Vector DB: ChromaDB
- Python: scikit-learn

## Tools & Workflow
- Git & GitHub (branching + PR workflow)
- Postman for API testing
- Swagger UI for API documentation
