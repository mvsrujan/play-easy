from typing import Dict


class SessionManager:
    """Simple in-memory session storage (use Redis/DB in production)"""

    def __init__(self):
        self._sessions: Dict[str, str] = {}

    def create_session(self, session_id: str, access_token: str):
        self._sessions[session_id] = access_token

    def get_session(self, session_id: str) -> str:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)


# Global session manager instance
session_manager = SessionManager()
