
import time
import uuid
from datetime import datetime, timezone
from typing import Any


class ExecutionTracker:

    def __init__(self, user_query: str):
        self.execution_id = str(uuid.uuid4())
        self.user_query = user_query
        self.selected_agent = ""
        self.execution_status = "running"
        self.execution_time_ms = 0.0
        self.error = None

        self.created_at = datetime.now(timezone.utc)
        self._start_time = time.perf_counter()

    def complete(self, selected_agent: str) -> dict[str, Any]:
        """
        Mark execution as successful and return its record.
        """

        self.selected_agent = selected_agent
        self.execution_status = "success"
        self._calculate_execution_time()

        return self.to_dict()

    def fail(self, error: Exception) -> dict[str, Any]:
        """
        Mark execution as failed and capture the error.
        """

        self.execution_status = "failure"
        self.error = str(error)
        self._calculate_execution_time()

        return self.to_dict()

    def _calculate_execution_time(self) -> None:
        """
        Calculate total execution time in milliseconds.
        """

        elapsed_time = time.perf_counter() - self._start_time
        self.execution_time_ms = round(elapsed_time * 1000, 2)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert execution details into a dictionary.
        """

        return {
            "execution_id": self.execution_id,
            "user_query": self.user_query,
            "selected_agent": self.selected_agent,
            "execution_status": self.execution_status,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "created_at": self.created_at,
        }
