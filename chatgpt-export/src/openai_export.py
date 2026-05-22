import openai
from datetime import datetime


class OpenAIExporter:
    def __init__(self, api_key=None):
        self.client = openai.OpenAI(api_key=api_key) if api_key else None

    def export_conversations(self, limit=100):
        if not self.client:
            raise ValueError("OpenAI API key required")
        conversations = []
        threads = self.client.beta.threads.list(limit=limit)
        for thread in threads.data:
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            conversation = {
                "id": thread.id,
                "title": thread.metadata.get("title", "Untitled"),
                "created_at": str(datetime.fromtimestamp(thread.created_at)),
                "messages": []
            }
            for msg in messages.data:
                for content in msg.content:
                    if content.type == "text":
                        conversation["messages"].append({
                            "role": msg.role,
                            "content": content.text.value,
                            "timestamp": str(datetime.fromtimestamp(msg.created_at))
                        })
            conversations.append(conversation)
        return conversations
