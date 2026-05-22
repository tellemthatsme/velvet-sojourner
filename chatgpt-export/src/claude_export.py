import anthropic
from datetime import datetime


class ClaudeExporter:
    def __init__(self, api_key=None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def export_conversations(self, limit=100):
        if not self.client:
            raise ValueError("Anthropic API key required")
        conversations = []
        try:
            conversations_data = self.client.messages.list(limit=limit)
            for conv in conversations_data.data:
                conversation = {
                    "id": conv.id,
                    "title": getattr(conv, 'title', 'Untitled'),
                    "created_at": str(datetime.fromtimestamp(conv.created_at)),
                    "messages": []
                }
                conversations.append(conversation)
        except Exception as e:
            raise ValueError(f"Claude API export error: {e}")
        return conversations
