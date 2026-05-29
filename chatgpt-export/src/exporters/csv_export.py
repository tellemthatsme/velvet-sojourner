import csv
from pathlib import Path


def export_conversations_csv(conversations: list, filepath: str):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "date", "source", "model", "topic", "tokens", "estimated_cost", "message_count"])
        for conv in conversations:
            content = " ".join(m.get("content", "") for m in conv.get("messages", []))
            tokens = max(1, len(content) // 4)
            writer.writerow([
                conv.get("id", ""),
                conv.get("title", ""),
                conv.get("date", ""),
                conv.get("source", ""),
                conv.get("model", ""),
                conv.get("topic", ""),
                tokens,
                round(tokens * 0.00003 * 30.0, 4),
                len(conv.get("messages", [])),
            ])
