from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    description: str
    status: str = "pending"
    created_at: str = field(default_factory=utc_timestamp)
    processed_at: str | None = None

    def mark_processed(self) -> "Task":
        return Task(
            id=self.id,
            description=self.description,
            status="processed",
            created_at=self.created_at,
            processed_at=utc_timestamp(),
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "processed_at": self.processed_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Task":
        return cls(
            id=str(payload["id"]),
            description=str(payload["description"]),
            status=str(payload.get("status", "pending")),
            created_at=str(payload.get("created_at", utc_timestamp())),
            processed_at=str(payload["processed_at"]) if payload.get("processed_at") is not None else None,
        )
