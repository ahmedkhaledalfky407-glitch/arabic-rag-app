from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List

from config import MAX_MEMORY_MESSAGES


@dataclass
class ChatTurn:
    role: str
    content: str


@dataclass
class ConversationMemory:
    turns: Deque[ChatTurn] = field(default_factory=deque)

    def add_turn(self, role: str, content: str) -> None:
        self.turns.append(ChatTurn(role=role, content=content))
        while len(self.turns) > MAX_MEMORY_MESSAGES:
            self.turns.popleft()

    def clear(self) -> None:
        self.turns.clear()

    def to_prompt_block(self) -> str:
        if not self.turns:
            return ""
        lines = ["سجل المحادثة:"]
        for turn in list(self.turns):
            prefix = "المستخدم" if turn.role == "user" else "المساعد"
            lines.append(f"- {prefix}: {turn.content}")
        return "\n".join(lines)

    def as_list(self) -> List[dict]:
        return [{"role": turn.role, "content": turn.content} for turn in self.turns]
