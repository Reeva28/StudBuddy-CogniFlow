# CogniFlow - 5 Hour MVP Implementation Plan
## Interview Preparation Checklist

**Target**: Working MVP for interview demonstration
**Timeline**: 5 hours
**Status**: 🔴 Not Started

---

## 🎯 CRITICAL PATH (Must Complete)

### ⚡ PHASE 1: AI Integration with Free API (45 minutes)
**Goal**: Make AI features actually work

#### 1.1 Choose & Setup Free AI API (15 min)
- [ ] **Option A: Google Gemini** (RECOMMENDED)
  ```bash
  pip install google-generativeai
  ```
  - Get free API key: https://makersuite.google.com/app/apikey
  - Add to `.env`: `GEMINI_API_KEY=your-key-here`

- [ ] **Option B: Groq**
  ```bash
  pip install groq
  ```
  - Get free API key: https://console.groq.com
  - Add to `.env`: `GROQ_API_KEY=your-key-here`

#### 1.2 Replace OpenAI Client (20 min)
**File**: `backend/app/services/ai/openai_client.py`
- [ ] Rename to `ai_client.py` or `gemini_client.py`
- [ ] Replace OpenAI calls with Gemini/Groq
- [ ] Implement `_structure_summary()`, `_parse_study_plan()`, `_parse_questions()`
- [ ] Test basic completion

#### 1.3 Connect AI to Endpoints (10 min)
- [ ] Update document processing to use real AI summaries
- [ ] Update study plan generation to use AI
- [ ] Test one complete flow: upload doc → get AI summary

**Deliverable**: AI-powered document summary and study plan generation working

---

### ⚡ PHASE 2: Minimal Functional Frontend (2.5 hours)
**Goal**: Create a working web interface that demonstrates key features

#### 2.1 Setup Next.js Project (20 min)
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
```
- [ ] Install dependencies: `axios`, `@tanstack/react-query`, `jwt-decode`
- [ ] Setup API configuration
- [ ] Create authentication context

#### 2.2 Authentication Pages (30 min)
**Priority**: HIGH (Shows project completeness)
- [ ] Login page (`app/login/page.tsx`)
- [ ] Register page (`app/register/page.tsx`)  
- [ ] JWT storage and auth state management
- [ ] Protected route wrapper

#### 2.3 Dashboard (Main Interface) (40 min)
**Priority**: CRITICAL (First thing shown in interview)
**File**: `app/dashboard/page.tsx`

Must Show:
- [ ] User greeting with name
- [ ] Statistics cards:
  - Total study hours
  - Documents uploaded
  - Sessions completed
  - Study streak
- [ ] Recent sessions list (last 5)
- [ ] Quick action buttons (Upload, New Session, New Plan)
- [ ] Beautiful, professional layout

#### 2.4 Document Upload & View (30 min)
**Priority**: CRITICAL (Demonstrates AI features)
**File**: `app/documents/page.tsx`

- [ ] File upload dropzone (drag & drop if possible)
- [ ] Document list with status badges
- [ ] Click to view document summary
- [ ] Show AI-generated key points
- [ ] Loading states during processing

#### 2.5 Study Session Interface (20 min)
**Priority**: HIGH (Core feature)
**File**: `app/session/page.tsx`

- [ ] Active session display
- [ ] Pomodoro timer (25 min countdown)
- [ ] Start/Pause/Complete buttons
- [ ] Session notes textarea
- [ ] Show linked documents

#### 2.6 Study Plan View (10 min)
**Priority**: MEDIUM (Nice to have)
**File**: `app/plan/page.tsx`

- [ ] Display generated study plan sessions
- [ ] Show recommendations
- [ ] Progress tracker

**Deliverable**: Working frontend that can demo all core features

---

### ⚡ PHASE 3: Integration & Testing (1 hour)
**Goal**: Everything works end-to-end

#### 3.1 API Integration (30 min)
- [ ] Create API service layer (`lib/api.ts`)
- [ ] Connect all frontend pages to backend endpoints
- [ ] Handle authentication headers
- [ ] Test CORS configuration

#### 3.2 End-to-End Testing (20 min)
Test complete user flow:
- [ ] Register new user
- [ ] Login
- [ ] Upload a document (use sample PDF)
- [ ] Wait for AI summary
- [ ] Create study session
- [ ] Generate study plan
- [ ] View dashboard stats

#### 3.3 Critical Bug Fixes (10 min)
- [ ] Fix any blocking errors
- [ ] Ensure error messages are user-friendly
- [ ] Verify data persistence

**Deliverable**: Complete working demo flow

---

### ⚡ PHASE 4: Polish & Demo Prep (45 min)
**Goal**: Make it interview-ready

#### 4.1 UI Polish (20 min)
- [ ] Consistent color scheme
- [ ] Loading spinners for async operations
- [ ] Success/error toast notifications
- [ ] Responsive layout checks
- [ ] Clean up console errors

#### 4.2 Sample Data (10 min)
- [ ] Create test user with good username/name
- [ ] Upload 2-3 sample documents
- [ ] Create completed study sessions (for stats)
- [ ] Generate a study plan

#### 4.3 Demo Script Preparation (15 min)
Create talking points for interview:
- [ ] Project overview (30 sec)
- [ ] Architecture explanation (1 min)
- [ ] Live demo flow (2-3 min)
- [ ] Technical highlights to mention
- [ ] Future enhancements ideas

**Deliverable**: Polished, demo-ready application

---

## 📱 MINIMUM VIABLE PAGES

### Must Have (Complete these):
1. ✅ **Login/Register** - Shows you can do auth
2. ✅ **Dashboard** - First impression, stats
3. ✅ **Documents** - Upload + AI summary (killer feature)
4. ✅ **Session** - Core study functionality

### Nice to Have (if time permits):
5. ⚠️ **Study Plans** - Shows planning feature
6. ⚠️ **Profile/Settings** - Completeness

---

## 🎨 DESIGN QUICK WINS

Use these for professional look without much effort:
- **Tailwind UI Components**: Copy from https://tailwindui.com/components (free components)
- **Heroicons**: `npm install @heroicons/react`
- **Shadcn UI**: `npx shadcn-ui@latest init` (beautiful components)
- **Color Scheme**: Stick to one - suggest Indigo/Purple for education app

---

## 🚨 INTERVIEW DEMO SCRIPT (2-3 minutes)

### Opening (30 sec)
> "I built CogniFlow, an AI-powered study companion that helps students optimize their learning. The application uses machine learning to analyze study materials, generate personalized plans, and track progress."

### Demo Flow (2 min)
1. **Start logged in** - "This is the dashboard showing study analytics"
2. **Upload Document** - "I can upload PDFs/DOCX, and the AI analyzes them" → Show AI summary appearing
3. **Study Session** - "Students can track study time with Pomodoro technique"
4. **Study Plan** - "AI generates personalized study plans based on goals and materials"

### Technical Highlights (30 sec)
> "Built with:
> - **Backend**: FastAPI (Python) with async processing
> - **Frontend**: Next.js (TypeScript) with React Query
> - **AI**: Google Gemini API for document analysis
> - **Database**: PostgreSQL with SQLAlchemy ORM
> - **Auth**: JWT-based authentication with bcrypt
> - **Architecture**: Clean separation - API/Service/Data layers"

### Closing
> "The codebase is modular and well-tested, ready for scaling. Future enhancements include collaborative features, mobile app, and advanced analytics."

---

## 📦 QUICK SETUP COMMANDS

### Backend:
```bash
cd backend
pip install google-generativeai  # or groq
# Add API key to .env
python -m app.db.init_db
python scripts/create_test_user.py
uvicorn app.main:app --reload
```

### Frontend:
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install axios @tanstack/react-query jwt-decode @heroicons/react
npm run dev
```

---

## ⏰ TIME TRACKING

| Phase | Estimated | Actual | Status |
|-------|-----------|--------|--------|
| Phase 1: AI Integration | 45 min | ___ | ⬜ |
| Phase 2: Frontend | 150 min | ___ | ⬜ |
| Phase 3: Integration | 60 min | ___ | ⬜ |
| Phase 4: Polish | 45 min | ___ | ⬜ |
| **TOTAL** | **300 min (5 hrs)** | ___ | ⬜ |

---

## 🎯 SUCCESS CRITERIA

Before the interview, you must be able to:
- [ ] Login to the application
- [ ] Upload a document and see AI-generated summary
- [ ] Start and track a study session
- [ ] View study statistics on dashboard
- [ ] Show clean, professional UI
- [ ] Explain the architecture confidently
- [ ] Demo runs without errors

---

## 🆘 IF RUNNING OUT OF TIME

### Cut these features:
1. Study Plan page (mention "not implemented in current sprint")
2. User profile/settings
3. Advanced animations
4. Mobile responsiveness
5. Comprehensive error handling

### Keep these MANDATORY:
1. Login/Auth
2. Dashboard with stats
3. Document upload + AI summary
4. One complete study session
5. Professional looking UI

---

## 💡 INTERVIEW TIPS

### What to Emphasize:
- ✅ "Built in X days as a learning project"
- ✅ "Focused on clean architecture and scalability"
- ✅ "Used industry best practices (JWT, async, ORM)"
- ✅ "AI integration with modern APIs"

### If Asked About Missing Features:
- ✅ "This is the MVP - I prioritized core user flow"
- ✅ "On my roadmap: [concept mapping, mobile app, collaboration]"
- ✅ "Built with extensibility in mind"

### Technical Depth:
- Know your database schema
- Explain API endpoint structure
- Discuss state management choices
- Mention async processing for documents

---

## 📝 NOTES

- Test the demo flow at least 3 times before interview
- Have backup if live demo fails (video/screenshots)
- Clear browser cache/localStorage before demo
- Use incognito mode for clean demo
- Have sample PDF ready to upload
- Know your API key limits (don't run out mid-demo!)

---

**Good luck! Focus on working software over perfect code. Better to have 4 features working perfectly than 10 features half-broken.**
