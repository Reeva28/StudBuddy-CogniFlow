"""
Schema exports
"""
from app.schemas.base import Message
from app.schemas.user import (
    User, UserCreate, UserUpdate, UserInDB,
    Token, TokenPayload, UserStats
)
from app.schemas.study_session import (
    StudySession, StudySessionCreate, StudySessionUpdate,
    Pomodoro, PomodoroCreate, PomodoroUpdate
)
from app.schemas.document import (
    Document, DocumentCreate, DocumentUpdate,
    DocumentSummary, DocumentSummaryCreate,
    Flashcard, FlashcardCreate, FlashcardUpdate
)
from app.schemas.study_plan import (
    StudyPlan, StudyPlanCreate, StudyPlanUpdate,
    StudyPlanGenerateRequest
)
from app.schemas.note import (
    Note, NoteCreate, NoteUpdate
)
from app.schemas.analytics import (
    SessionStats, NoteStats, ProductivityStats,
    RecentSession, TimeDistribution, DailyActivity,
    AnalyticsDashboard
)
from app.schemas.mood import (
    Mood, MoodCreate, MoodUpdate,
    MoodTrend, MoodStats
)