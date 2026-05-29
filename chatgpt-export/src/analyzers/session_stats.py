from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List


@dataclass
class SessionStats:
    total_conversations: int = 0
    total_messages: int = 0
    avg_messages_per_conv: float = 0.0
    avg_length_chars: float = 0.0
    avg_length_tokens: float = 0.0
    most_common_topics: List[tuple] = field(default_factory=list)
    most_active_source: str = ""
    top_keywords: List[tuple] = field(default_factory=list)
    activity_by_hour: dict = field(default_factory=dict)
    activity_by_day: dict = field(default_factory=dict)


def compute(conversations: list) -> SessionStats:
    stats = SessionStats()
    stats.total_conversations = len(conversations)

    msg_counts = []
    topics = Counter()
    sources = Counter()
    hour_counts = Counter()
    day_counts = Counter()
    word_counts = Counter()
    total_chars = 0

    for conv in conversations:
        messages = conv.get("messages", [])
        msg_counts.append(len(messages))
        total_chars += sum(len(m.get("content", "")) for m in messages)

        topic = conv.get("topic", "general")
        topics[topic] += 1

        source = conv.get("source", "unknown")
        sources[source] += 1

        for msg in messages:
            content = msg.get("content", "")
            words = [w.lower().strip(".,!?;:'\"()[]") for w in content.split() if len(w) > 3]
            word_counts.update(w for w in words if w)

        date_str = conv.get("date", "")
        if date_str:
            try:
                from datetime import datetime
                if "T" in date_str:
                    dt = datetime.fromisoformat(date_str)
                else:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                hour_counts[dt.hour] += 1
                day_counts[dt.strftime("%A")] += 1
            except (ValueError, TypeError):
                pass

    stats.total_messages = sum(msg_counts)
    stats.avg_messages_per_conv = round(stats.total_messages / max(1, stats.total_conversations), 2)
    stats.avg_length_chars = round(total_chars / max(1, stats.total_conversations), 1)
    stats.avg_length_tokens = round((total_chars // 4) / max(1, stats.total_conversations), 1)
    stats.most_common_topics = topics.most_common(10)
    stats.most_active_source = sources.most_common(1)[0][0] if sources else ""
    stats.top_keywords = word_counts.most_common(20)
    stats.activity_by_hour = dict(sorted(hour_counts.items()))
    stats.activity_by_day = dict(sorted(day_counts.items(), key=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(x[0]) if x[0] in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] else 0))

    return stats
