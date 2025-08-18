# Import all models here so Alembic can detect them
from .user import User
from .organization import Organization
from .membership import Membership
from .project import Project
from .board import Board
from .column import Column
from .task import Task
from .task_comment import TaskComment
from .label import Label
from .task_label import TaskLabel
from .user_cred import UserCredential   # noqa: F401
from .user_session import UserSession   # noqa: F401
from .notification import Notification
from .notification_pref import NotificationPreference
from .webhook import Webhook
from .webhook_attempt import WebhookAttempt
from .file import File  # noqa: F401

# This ensures all models are registered with SQLAlchemy metadata
__all__ = [
    "User",
    "Organization", 
    "Membership",
    "Project",
    "Board",
    "Column",
    "Task",
    "TaskComment",
    "Label",
    "TaskLabel",
    "UserCredential",
    "UserSession",
    "Notification",
    "NotificationPreference",
    "Webhook",
    "WebhookAttempt",
    "File"
]
