# CogniFlow - My Study Companion

An intelligent study companion application that leverages artificial intelligence to help students optimize their learning process through personalized study plans, smart document analysis, and comprehensive progress tracking.

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [Commands to Run](#-commands-to-run)
- [API Documentation](#-api-documentation)
- [License](#-license)

---

## 🔍 The Problem

Students and learners face several critical challenges in their educational journey:

### 1. **Information Overload**
- Students receive massive amounts of study materials (PDFs, documents, lecture notes) without effective tools to process and understand them
- Difficulty extracting key concepts and main ideas from lengthy documents
- No systematic way to identify learning objectives from raw content

### 2. **Ineffective Study Planning**
- Creating personalized study plans requires significant time and expertise
- Students struggle to estimate appropriate time allocation for different topics
- Lack of understanding about optimal study session structures and sequences
- Difficulty in adapting plans based on progress and comprehension levels

### 3. **Poor Focus and Time Management**
- Distractions during study sessions lead to reduced productivity
- No structured approach to managing study time and breaks
- Difficulty maintaining consistent study habits

### 4. **Limited Progress Tracking**
- No meaningful analytics on study patterns and effectiveness
- Cannot identify areas that need more attention
- Lack of reflection mechanisms to improve future study sessions

### 5. **Cognitive Load Management**
- Students don't know how to pace their learning effectively
- Difficulty breaking down complex topics into manageable chunks
- No guidance on which topics to study in what order

---

## 💡 The Solution

**CogniFlow** addresses these challenges by combining modern AI technology with evidence-based learning principles to create an intelligent study companion that:

### 1. **AI-Powered Document Analysis**
- Automatically processes uploaded study materials (PDFs, DOCX)
- Uses Google Gemini AI to generate comprehensive summaries highlighting main points
- Extracts key concepts and learning objectives automatically
- Assesses document difficulty level and estimates reading time
- Provides personalized study recommendations based on content analysis

### 2. **Intelligent Study Plan Generation**
- Creates personalized study plans based on:
  - User's learning goals and objectives
  - Available study time and preferences
  - Document complexity and content structure
  - Prior knowledge assessment
- Optimizes session scheduling for maximum retention
- Breaks down content into manageable study sessions
- Adapts recommendations based on learning style

### 3. **Structured Study Sessions with Pomodoro Integration**
- Implements scientifically-proven Pomodoro Technique (25-minute focus + 5-minute break cycles)
- Tracks actual study time vs. planned duration
- Monitors focus levels and productivity ratings
- Records mood before and after sessions for psychological insights

### 4. **Comprehensive Progress Tracking & Analytics**
- Records detailed session metadata (duration, focus rating, productivity)
- Provides insights into study patterns and habits
- Tracks completion rates and goal achievement
- Enables reflection through session notes and feedback

### 5. **Organized Knowledge Management**
- Note-taking capabilities during study sessions
- Links notes to specific sessions and documents
- Centralized repository for all study materials
- Cross-referencing between documents, sessions, and plans

---

## ✨ Key Features

### For Students
- 📚 **Smart Document Upload**: Process PDFs and Word documents with AI-powered analysis
- 🎯 **Personalized Study Plans**: AI generates custom plans based on your goals and materials
- ⏰ **Pomodoro Timer**: Built-in timer to maintain focus with structured breaks
- 📊 **Progress Dashboard**: Visual analytics of your study habits and achievements
- 📝 **Integrated Note-Taking**: Capture insights and questions during sessions
- 🧠 **Concept Mapping**: Visualize relationships between topics (powered by NetworkX)
- 💭 **Mood & Reflection Tracking**: Monitor emotional state and productivity patterns

### For Developers
- 🚀 **RESTful API**: Comprehensive FastAPI backend with automatic documentation
- 🔐 **Secure Authentication**: JWT-based auth with bcrypt password hashing
- 📦 **Modular Architecture**: Clean separation of concerns (API, Services, Data layers)
- ⚡ **Redis Caching**: High-performance caching for AI responses and frequent queries
- 🔄 **Rate Limiting**: Protect API endpoints from abuse
- 📈 **Structured Logging**: Comprehensive logging with Loguru
- 🧪 **Testing Support**: Pytest integration for comprehensive test coverage

---

## 📁 Project Structure

```
CogniFlow/
│
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # Application entry point
│   │   │
│   │   ├── api/                     # API Layer
│   │   │   ├── api.py              # Main API router
│   │   │   ├── deps.py             # Dependency injection
│   │   │   └── endpoints/           # API endpoints
│   │   │       ├── auth.py         # Authentication (login, register, refresh)
│   │   │       ├── users.py        # User management
│   │   │       ├── documents.py     # Document upload & retrieval
│   │   │       ├── sessions.py     # Study session management
│   │   │       ├── session_summary.py # Session analytics
│   │   │       └── study_plan.py   # Study plan generation
│   │   │
│   │   ├── core/                    # Core Configuration
│   │   │   ├── config.py           # Application settings (DB, Redis, Gemini API)
│   │   │   ├── security.py         # JWT token handling, password hashing
│   │   │   ├── exceptions.py       # Custom exception classes
│   │   │   ├── logging.py          # Logging configuration
│   │   │   ├── rate_limit.py       # Rate limiting middleware
│   │   │   └── redis.py            # Redis client setup
│   │   │
│   │   ├── db/                      # Database Layer
│   │   │   ├── session.py          # SQLAlchemy session factory
│   │   │   ├── models.py           # Database models (User, StudyPlan, etc.)
│   │   │   ├── init_db.py          # Database initialization
│   │   │   └── deps.py             # Database dependency injection
│   │   │
│   │   ├── schemas/                 # Pydantic Schemas (Request/Response)
│   │   │   ├── user.py             # User schemas
│   │   │   ├── document.py         # Document schemas
│   │   │   ├── study_session.py    # Study session schemas
│   │   │   ├── study_plan.py       # Study plan schemas
│   │   │   ├── note.py             # Note schemas
│   │   │   └── session_summary.py  # Session summary schemas
│   │   │
│   │   └── services/                # Business Logic Layer
│   │       ├── auth.py             # Authentication service
│   │       ├── user.py             # User service (CRUD)
│   │       ├── document.py         # Document service (CRUD)
│   │       ├── study_session.py    # Study session service
│   │       ├── study_plan.py       # Study plan service
│   │       ├── note.py             # Note service
│   │       │
│   │       ├── ai/                 # AI Services
│   │       │   ├── openai_client.py        # Gemini API wrapper
│   │       │   ├── document_analyzer.py    # Document analysis with Gemini AI
│   │       │   ├── study_planner.py        # AI study plan generation
│   │       │   ├── concept_mapper.py       # Concept relationship mapping
│   │       │   └── content_recommender.py  # Content recommendations
│   │       │
│   │       ├── file_processor/      # Document Processing
│   │       │   └── document_processor.py   # PDF/DOCX processing
│   │       │
│   │       └── summarizer/          # Text Summarization
│   │           └── summarizer.py   # Document summarization logic
│   │
│   ├── scripts/
│   │   └── create_test_user.py     # Utility script for test user creation
│   │
│   ├── uploads/                     # User uploaded files
│   │   └── documents/
│   │
│   └── requirements.txt             # Python dependencies
│
├── frontend/                         # Next.js Frontend (TypeScript)
│   └── app/
│       ├── _components/             # Reusable React components
│       ├── dashboard/               # Dashboard page & components
│       ├── plan/                    # Study plan management
│       └── session/                 # Study session interface
│
├── README.md                        # This file
└── frontend_requirements.md         # Frontend implementation specs
```

### Backend Architecture Details

The backend follows a **clean, layered architecture** pattern:

1. **API Layer** (`app/api/`)
   - Handles HTTP requests and responses
   - Input validation using Pydantic schemas
   - Dependency injection for database sessions and user authentication
   - Route organization by resource type

2. **Service Layer** (`app/services/`)
   - Contains all business logic
   - Separated into specialized services (auth, AI, document processing, etc.)
   - Orchestrates interactions between different components
   - AI services use Google Gemini for intelligent features

3. **Data Layer** (`app/db/`)
   - SQLAlchemy ORM models
   - Database session management
   - Uses SQLite for simplicity and portability (suitable for development and small-scale production)

4. **Core Layer** (`app/core/`)
   - Application configuration
   - Security utilities (JWT, password hashing)
   - Cross-cutting concerns (logging, rate limiting, caching)

### Database Schema

**Main Entities:**
- **User**: Authentication and user profile
- **StudyPlan**: AI-generated study plans with sessions and recommendations
- **StudySession**: Individual study sessions with timing and analytics
- **Pomodoro**: Pomodoro technique cycles within sessions
- **Document**: Uploaded study materials with AI-generated analysis
- **Note**: Session notes and reflections

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.103.1 (high-performance async Python web framework)
- **Database**: SQLAlchemy 2.0.20 (ORM), SQLite (file-based database)
- **Authentication**: JWT tokens (python-jose), bcrypt password hashing
- **AI/ML**: Google Gemini API for document analysis and study plan generation
- **Document Processing**: PyPDF2 (PDFs), python-docx (Word documents)
- **Caching**: Redis for AI response caching and rate limiting
- **Graph Processing**: NetworkX for concept mapping
- **Visualization**: Matplotlib for concept relationship diagrams
- **Logging**: Loguru for structured logging
- **Testing**: Pytest with asyncio support

### Frontend
- **Framework**: Next.js with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS
- **API Communication**: React Query for data fetching and caching
- **Authentication**: JWT handling

### Infrastructure
- **Server**: Uvicorn (ASGI server)
- **Cache/Queue**: Redis
- **Database**: SQLite (simple, file-based, zero-configuration database)

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (for backend)
- **Node.js 16+** and npm/yarn (for frontend)
- **SQLite** (comes pre-installed with Python, no separate installation needed)
- **Redis** (optional but recommended for caching and rate limiting)
- **Google Gemini API Key** (required for AI features)

---

## ⚙️ Commands to Run

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   
   **On Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the `backend` directory with the following configuration:
   
   ```env
   # API Configuration
   API_V1_STR=/api/v1                # Base path for API version 1 endpoints
   SECRET_KEY=your-super-secret-key-change-this-in-production  # JWT signing key (change in production!)
   ACCESS_TOKEN_EXPIRE_MINUTES=11520  # Token expiration: 8 days (11520 minutes)
   ALGORITHM=HS256                    # JWT signing algorithm
   
   # Database
   # SQLite is used by default (no setup required, creates app.db file)
   DATABASE_URL=sqlite:///./app.db
   
   # Google Gemini API
   GEMINI_API_KEY=your-gemini-api-key-here
   
   # For PostgreSQL (advanced, optional):
   # DATABASE_URL=postgresql://user:password@localhost:5432/cogniflow
   # POSTGRES_SERVER=localhost
   # POSTGRES_USER=postgres
   # POSTGRES_PASSWORD=your-password
   # POSTGRES_DB=cogniflow
   
   # Redis (optional)
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=
   
   # CORS
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   
   # Logging
   LOG_LEVEL=INFO
   ```

   **Environment Variable Explanations:**
   
   - **API_V1_STR**: Base path prefix for all API endpoints (e.g., `/api/v1`)
   - **SECRET_KEY**: Secret key used to sign JWT tokens. **MUST be changed in production!** Generate a secure random string.
   - **ACCESS_TOKEN_EXPIRE_MINUTES**: How long JWT tokens remain valid (11520 minutes = 8 days)
   - **ALGORITHM**: Algorithm used for JWT token signing (HS256 is standard HMAC with SHA-256)
   - **DATABASE_URL**: SQLite database file location (creates `app.db` in backend folder)
   - **GEMINI_API_KEY**: Your Google Gemini API key for AI features ([Get one here](https://aistudio.google.com/app/apikey))
   - **REDIS_HOST/PORT/DB**: Redis connection settings for caching (optional, improves performance)
   - **BACKEND_CORS_ORIGINS**: Allowed frontend origins for CORS (add your frontend URL)
   - **LOG_LEVEL**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

5. **Initialize the database:**
   ```bash
   python -m app.db.init_db
   ```

6. **Create a test user (optional):**
   ```bash
   python scripts/create_test_user.py
   ```
   
   This creates a user with:
   - Email: `test@example.com`
   - Password: `testpassword`

7. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The API will be available at:
   - **API**: http://localhost:8000
   - **Swagger UI Documentation**: http://localhost:8000/docs
   - **ReDoc Documentation**: http://localhost:8000/redoc

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables:**
   
   Create a `.env.local` file in the `frontend` directory:
   
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_API_VERSION=/api/v1
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   
   The frontend will be available at: http://localhost:3000

### Running Both Backend and Frontend

Open two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Running Redis (Optional but Recommended)

**Using Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Or install Redis locally** and run:
```bash
redis-server
```

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest
```

**Run tests with coverage:**
```bash
pytest --cov=app tests/
```

---

## 📚 API Documentation

The API follows RESTful principles and includes comprehensive documentation.

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (beautiful API documentation)

### Main API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/refresh` - Refresh access token

#### Documents
- `POST /api/v1/documents/upload` - Upload study document (PDF, DOCX)
- `GET /api/v1/documents` - List user's documents
- `GET /api/v1/documents/{id}` - Get document with AI analysis

#### Study Plans
- `POST /api/v1/study-plans` - Generate AI-powered study plan
- `GET /api/v1/study-plans` - List user's study plans
- `GET /api/v1/study-plans/{id}` - Get specific study plan

#### Study Sessions
- `POST /api/v1/study-sessions` - Create study session
- `GET /api/v1/study-sessions` - List user's sessions
- `PUT /api/v1/study-sessions/{id}` - Update session (progress, ratings)
- `GET /api/v1/study-sessions/{id}/summary` - Get session analytics

#### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile

---

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt with salt for password storage
- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: Protection against API abuse
- **Input Validation**: Pydantic schemas validate all inputs

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Google for Gemini AI API
- FastAPI framework and community
- Next.js and React teams
- All open-source contributors whose libraries make this project possible