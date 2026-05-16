"""
Search Engine for Charm Crush
Handles full-text and regex search across sessions and files
"""
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class SearchMode(Enum):
    SIMPLE = "simple"
    REGEX = "regex"
    FUZZY = "fuzzy"


class SearchScope(Enum):
    ALL = "all"
    SESSIONS_ONLY = "sessions"
    FILES_ONLY = "files"
    TAGGED_SESSIONS = "tagged"


@dataclass
class SearchQuery:
    query: str
    mode: SearchMode = SearchMode.SIMPLE
    scope: SearchScope = SearchScope.ALL
    tags: List[str] = field(default_factory=list)


@dataclass
class SearchResult:
    session_id: str
    session_name: str
    matches_in: str # 'name', 'description', or 'file_content'
    preview: str
    relevance: float


class SearchEngine:
    """Provides advanced searching capabilities across all user data"""
    
    def __init__(self):
        self._history = []
        self._stats = {'total_searches': 0, 'total_results_found': 0}
        
    def search(self, query: SearchQuery, sessions: List[Dict[str, Any]]) -> List[SearchResult]:
        self._stats['total_searches'] += 1
        self._add_to_history(query.query)
        
        results = []
        
        # Compile regex if needed
        pattern = None
        if query.mode == SearchMode.REGEX:
            try:
                pattern = re.compile(query.query, re.IGNORECASE)
            except:
                return []
        
        for session in sessions:
            relevance = 0.0
            found = False
            preview = ""
            matches_in = ""
            
            # 1. Search in session name
            if query.scope in [SearchScope.ALL, SearchScope.SESSIONS_ONLY]:
                if self._matches(query.query, session.get('name', ''), pattern):
                    relevance += 1.0
                    matches_in = "name"
                    found = True
                    
            # 2. Search in tags
            if not found and query.scope == SearchScope.TAGGED_SESSIONS:
                session_tags = session.get('tags', [])
                if any(tag in query.tags for tag in session_tags):
                    relevance += 1.0
                    matches_in = "tags"
                    found = True
                    
            # 3. Search in description
            if not found and query.scope in [SearchScope.ALL, SearchScope.SESSIONS_ONLY]:
                desc = session.get('description', '')
                if self._matches(query.query, desc, pattern):
                    relevance += 0.8
                    matches_in = "description"
                    preview = desc[:50] + "..." if len(desc) > 50 else desc
                    found = True
                    
            # 4. Search in file contents
            if not found and query.scope in [SearchScope.ALL, SearchScope.FILES_ONLY]:
                for file_info in session.get('files', []):
                    content = file_info.get('content', '')
                    if isinstance(content, bytes):
                        try: content = content.decode('utf-8')
                        except: content = str(content)
                    
                    if self._matches(query.query, content, pattern):
                        relevance += 0.6
                        matches_in = "file_content"
                        # Create preview
                        idx = content.lower().find(query.query.lower()) if query.mode == SearchMode.SIMPLE else 0
                        start = max(0, idx - 20)
                        end = min(len(content), idx + len(query.query) + 20)
                        preview = f"...{content[start:end]}..."
                        found = True
                        break
            
            if found:
                results.append(SearchResult(
                    session_id=session['id'],
                    session_name=session['name'],
                    matches_in=matches_in,
                    preview=preview,
                    relevance=relevance
                ))
                
        # Sort by relevance
        results.sort(key=lambda x: x.relevance, reverse=True)
        self._stats['total_results_found'] += len(results)
        return results
        
    def _matches(self, query: str, text: str, pattern=None) -> bool:
        if not text: return False
        if pattern:
            return bool(pattern.search(text))
        return query.lower() in text.lower()
        
    def _add_to_history(self, query: str):
        if query and (not self._history or self._history[0] != query):
            self._history.insert(0, query)
            if len(self._history) > 50:
                self._history.pop()
                
    def get_search_history(self) -> List[str]:
        return self._history
        
    def get_suggestions(self, partial: str, sessions: List[Dict]) -> List[str]:
        suggestions = set()
        # Add from history
        for q in self._history:
            if q.lower().startswith(partial.lower()):
                suggestions.add(q)
        # Add from session names
        for s in sessions:
            if s['name'].lower().startswith(partial.lower()):
                suggestions.add(s['name'])
        return list(suggestions)
        
    def get_statistics(self) -> Dict:
        return self._stats
