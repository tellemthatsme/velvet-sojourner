import re

MODEL_PATTERNS = [
    (re.compile(r"gpt-4-turbo", re.IGNORECASE), "gpt-4-turbo", 0.95),
    (re.compile(r"gpt-4(?!-turbo)", re.IGNORECASE), "gpt-4", 0.90),
    (re.compile(r"gpt-3\.5-turbo", re.IGNORECASE), "gpt-3.5-turbo", 0.95),
    (re.compile(r"claude-3-opus", re.IGNORECASE), "claude-3-opus", 0.95),
    (re.compile(r"claude-3-sonnet", re.IGNORECASE), "claude-3-sonnet", 0.95),
    (re.compile(r"claude-3-haiku", re.IGNORECASE), "claude-3-haiku", 0.95),
    (re.compile(r"claude-2(?:\.[01])?", re.IGNORECASE), "claude-3-sonnet", 0.70),
    (re.compile(r"\bgemini-pro\b", re.IGNORECASE), "gemini-pro", 0.95),
    (re.compile(r"\bgemini\b", re.IGNORECASE), "gemini-pro", 0.60),
    (re.compile(r"\bo1\b", re.IGNORECASE), "o1", 0.90),
    (re.compile(r"\bo3\b", re.IGNORECASE), "o3", 0.90),
    (re.compile(r"model.*?(?:gpt-4|gpt-3\.5|claude|gemini)", re.IGNORECASE), None, 0.50),
]

SOURCE_MODEL_MAP = {
    "chatgpt": "gpt-4",
    "openai": "gpt-4",
    "claude": "claude-3-sonnet",
    "anthropic": "claude-3-sonnet",
    "gemini": "gemini-pro",
    "bard": "gemini-pro",
}


class ModelDetector:
    def detect(self, text: str) -> tuple:
        if not text:
            return "unknown", 0.0
        for pattern, model_name, confidence in MODEL_PATTERNS:
            match = pattern.search(text)
            if match:
                if model_name is None:
                    matched = match.group(0).lower()
                    for key in SOURCE_MODEL_MAP:
                        if key in matched:
                            return SOURCE_MODEL_MAP[key], 0.50
                else:
                    return model_name, confidence
        return "unknown", 0.0

    def detect_from_conversation(self, conv: dict) -> tuple:
        text_parts = []
        model_field = conv.get("model")
        if model_field:
            text_parts.append(str(model_field))
        metadata = conv.get("metadata", {})
        if isinstance(metadata, dict):
            text_parts.append(str(metadata))
        if isinstance(conv, dict) and "model" in conv:
            text_parts.append(str(conv["model"]))
        for msg in conv.get("messages", []):
            text_parts.append(msg.get("content", "")[:500])
            role = msg.get("role", "")
            if role in ("system", "assistant"):
                text_parts.append(msg.get("content", "")[:200])
        combined = " ".join(text_parts)
        return self.detect(combined)

    def detect_source_model(self, source: str) -> str:
        source_lower = source.lower()
        for key, model in SOURCE_MODEL_MAP.items():
            if key in source_lower:
                return model
        return "unknown"
