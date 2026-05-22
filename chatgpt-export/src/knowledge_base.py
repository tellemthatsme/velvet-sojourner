import sqlite3
import os
from datetime import datetime


class KnowledgeBase:
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS conversations USING fts5(
                title, content, topic, date, source, tags
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_conversation(self, conversation):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations(title, content, topic, date, source, tags)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (
            conversation.get('title', ''),
            conversation.get('content', ''),
            conversation.get('topic', 'general'),
            conversation.get('date', datetime.now().strftime("%Y-%m-%d")),
            conversation.get('source', 'unknown'),
            conversation.get('tags', '')
        ))
        conn.commit()
        conn.close()

    def add_conversations_batch(self, conversations):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        data = [(
            c.get('title', ''),
            c.get('content', ''),
            c.get('topic', 'general'),
            c.get('date', datetime.now().strftime("%Y-%m-%d")),
            c.get('source', 'unknown'),
            c.get('tags', '')
        ) for c in conversations]
        cursor.executemany("""
            INSERT INTO conversations(title, content, topic, date, source, tags)
            VALUES(?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        conn.close()

    def search(self, query, limit=50):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, content, topic, date, source, tags, rank
            FROM conversations
            WHERE conversations MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        results = cursor.fetchall()
        conn.close()
        return [{"title": r[0], "content": r[1][:200], "topic": r[2], "date": r[3], "source": r[4], "tags": r[5]} for r in results]

    def stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT topic, COUNT(*) FROM conversations GROUP BY topic")
        by_topic = dict(cursor.fetchall())
        cursor.execute("SELECT source, COUNT(*) FROM conversations GROUP BY source")
        by_source = dict(cursor.fetchall())
        conn.close()
        return {"total": total, "by_topic": by_topic, "by_source": by_source}
