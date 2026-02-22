# CogniFlow Frontend Requirements

## 1. Technical Stack Requirements
- Next.js framework with TypeScript
- Redux Toolkit for state management
- Tailwind CSS for styling and UI components
- JWT handling for authentication
- React Query for API data fetching and caching

## 2. API Integration Details

### 2.1 Base Configuration
```typescript
BASE_URL: 'http://localhost:8000'
API_VERSION: '/api/v1'
```

### 2.2 Authentication Endpoints
```typescript
POST /api/v1/auth/login
Request: {
  email: string
  password: string
}
Response: {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
    full_name: string
    is_active: boolean
    role: string
  }
}

POST /api/v1/auth/register
Request: {
  email: string
  password: string
  full_name: string
}

POST /api/v1/auth/refresh
Request: {
  refresh_token: string
}
```

### 2.3 Document Management Endpoints
```typescript
POST /api/v1/documents/upload
- Multipart form data
- Supports PDF, DOCX formats
- Max file size: 10MB

GET /api/v1/documents
Response: {
  documents: [{
    id: number
    title: string
    file_type: string
    created_at: string
    summary?: string
    status: 'processing' | 'completed' | 'error'
  }]
}

GET /api/v1/documents/{id}
Response: {
  id: number
  title: string
  content: string
  summary: {
    main_points: string[]
    key_concepts: string[]
    recommendations: string[]
  }
  metadata: {
    file_type: string
    created_at: string
    updated_at: string
    size: number
  }
}
```

### 2.4 Study Plan Endpoints
```typescript
POST /api/v1/study-plans
Request: {
  title: string
  subject: string
  goal: string
  duration_minutes: number
  difficulty: number
  preferences?: {
    learning_style?: string
    prior_knowledge?: string
  }
}
Response: {
  id: number
  title: string
  sessions: [{
    id: number
    title: string
    duration_minutes: number
    focus_areas: string[]
    resources: string[]
  }]
  recommendations: string[]
}

GET /api/v1/study-plans
GET /api/v1/study-plans/{id}
PUT /api/v1/study-plans/{id}
DELETE /api/v1/study-plans/{id}
```

### 2.5 Study Session Endpoints
```typescript
POST /api/v1/sessions
Request: {
  plan_id: number
  session_id: number
}
Response: {
  id: number
  status: 'active' | 'paused' | 'completed'
  start_time: string
  duration: number
  progress: number
}

PUT /api/v1/sessions/{id}
PATCH /api/v1/sessions/{id}/pause
PATCH /api/v1/sessions/{id}/resume
PATCH /api/v1/sessions/{id}/complete
```

## 3. Required Pages and Components

### 3.1 Authentication Pages
- Login Page
- Registration Page
- Password Reset Page
- Email Verification Page

### 3.2 Dashboard
Components needed:
- Recent Documents List
- Active Study Plans
- Progress Overview
- Quick Actions Menu
- Notification Center

### 3.3 Document Management
Components needed:
- Document Upload
- Document List View
- Document Detail View
- Summary View
- Flashcard Generation
- Progress Indicator for Processing

### 3.4 Study Plan Interface
Components needed:
- Plan Creation Form
- Plan List View
- Plan Detail View
- Session Timer
- Progress Tracking
- Resource Management

### 3.5 Study Session Interface
Components needed:
- Session Timer
- Note Taking Area
- Resource Display
- Progress Tracker
- Break Timer

## 4. UI/UX Requirements

### 4.1 Color Scheme
```css
--primary: '#2563eb'    /* Blue 600 */
--secondary: '#475569'  /* Slate 600 */
--accent: '#8b5cf6'    /* Violet 500 */
--success: '#22c55e'   /* Green 500 */
--warning: '#f59e0b'   /* Amber 500 */
--error: '#ef4444'     /* Red 500 */
--background: '#ffffff'
--text-primary: '#1e293b' /* Slate 800 */
--text-secondary: '#64748b' /* Slate 500 */
```

### 4.2 Typography
```css
--font-primary: 'Inter', sans-serif
--font-secondary: 'Roboto', sans-serif
--font-mono: 'JetBrains Mono', monospace
```

### 4.3 Responsive Breakpoints
```css
--mobile: '640px'
--tablet: '768px'
--laptop: '1024px'
--desktop: '1280px'
```

## 5. State Management

### 5.1 Redux Store Structure
```typescript
interface RootState {
  auth: {
    user: User | null
    token: string | null
    loading: boolean
    error: string | null
  }
  documents: {
    list: Document[]
    current: Document | null
    loading: boolean
    error: string | null
  }
  studyPlans: {
    list: StudyPlan[]
    current: StudyPlan | null
    loading: boolean
    error: string | null
  }
  sessions: {
    active: Session | null
    history: Session[]
    loading: boolean
    error: string | null
  }
  ui: {
    theme: 'light' | 'dark'
    sidebarOpen: boolean
    notifications: Notification[]
  }
}
```

## 6. Error Handling

### 6.1 Error Types to Handle
```typescript
interface ApiError {
  status: number
  message: string
  details?: any
}

// HTTP Status codes to handle:
401: 'Unauthorized'
403: 'Forbidden'
404: 'Not Found'
422: 'Validation Error'
429: 'Rate Limit Exceeded'
500: 'Internal Server Error'
```

## 7. Loading States

### 7.1 Required Loading Indicators
- Page loading skeletons
- Button loading states
- File upload progress
- Document processing progress
- API request loading states

## 8. Performance Requirements

### 8.1 Target Metrics
- First Contentful Paint: < 1.2s
- Time to Interactive: < 2.5s
- First Input Delay: < 100ms
- Cumulative Layout Shift: < 0.1

### 8.2 Optimizations Required
- Image optimization
- Code splitting
- Route prefetching
- API response caching
- Progressive loading for large documents

## 9. Security Requirements

### 9.1 Authentication
- JWT token storage in httpOnly cookies
- Token refresh mechanism
- Session timeout handling
- CSRF protection

### 9.2 Data Protection
- Input sanitization
- XSS prevention
- CORS configuration
- Sensitive data encryption

## 10. Accessibility Requirements
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Color contrast compliance
- Focus management
- Alt text for images
- ARIA labels where needed

## 11. Browser Support
- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)
- Mobile browsers (iOS Safari, Chrome for Android)