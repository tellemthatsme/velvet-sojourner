import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from export_sorter import ExportParser, ExportOrganizer, ExportSorter, ChatExport
from pathlib import Path
import tempfile
import json


class TestExportParser:
    def setup_method(self):
        self.parser = ExportParser()
    
    def test_detect_format_json(self):
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            f.write('{"test": "data"}')
            path = f.name
        result = self.parser.detect_format(Path(path))
        assert result == 'json'
        os.unlink(path)
    
    def test_detect_format_pdf(self):
        with tempfile.NamedTemporaryFile(suffix='.pdf', mode='w', delete=False) as f:
            f.write('test')
            path = f.name
        result = self.parser.detect_format(Path(path))
        assert result == 'pdf'
        os.unlink(path)
    
    def test_detect_format_html(self):
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
            f.write('<html><body>test</body></html>')
            path = f.name
        result = self.parser.detect_format(Path(path))
        assert result == 'html'
        os.unlink(path)
    
    def test_detect_format_chatgpt_txt(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
            f.write('ChatGPT conversation about coding')
            path = f.name
        result = self.parser.detect_format(Path(path))
        assert result == 'chatgpt'
        os.unlink(path)
    
    def test_detect_format_claude(self):
        with tempfile.NamedTemporaryFile(suffix='.md', mode='w', delete=False) as f:
            f.write('Claude AI assistant response')
            path = f.name
        result = self.parser.detect_format(Path(path))
        assert result == 'claude'
        os.unlink(path)
    
    def test_parse_text_with_conversation(self):
        content = """User: Hello, how are you?
Assistant: I'm doing well, thank you!
User: Can you help me with Python?
Assistant: Sure, what do you need?"""
        
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
            f.write(content)
            path = f.name
        
        result = self.parser.parse_file(Path(path))
        assert result is not None
        assert len(result.messages) == 4
        assert result.messages[0]['role'] == 'user'
        assert result.messages[1]['role'] == 'assistant'
        os.unlink(path)
    
    def test_parse_json_with_messages(self):
        data = {
            "model": "gpt-4",
            "created_at": "2026-05-22",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            json.dump(data, f)
            path = f.name
        
        result = self.parser.parse_file(Path(path))
        assert result is not None
        assert result.model == 'gpt-4'
        assert len(result.messages) == 2
        os.unlink(path)
    
    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix='.xyz', mode='w', delete=False) as f:
            f.write('test')
            path = f.name
        result = self.parser.parse_file(Path(path))
        assert result is None
        os.unlink(path)


class TestExportOrganizer:
    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.organizer = ExportOrganizer(self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_classify_code(self):
        chat = ChatExport(
            source="chatgpt",
            title="Python help",
            model="gpt-4",
            date="2026-05-22",
            first_prompt="How do I write a Python function?",
            messages=[{"role": "user", "content": "How do I write a Python function?"}]
        )
        result = self.organizer._classify_type(chat)
        assert result == "code"
    
    def test_classify_design(self):
        chat = ChatExport(
            source="chatgpt",
            title="Design feedback",
            model="gpt-4",
            date="2026-05-22",
            first_prompt="Can you review this UI design?",
            messages=[]
        )
        result = self.organizer._classify_type(chat)
        assert result == "design"
    
    def test_classify_general(self):
        chat = ChatExport(
            source="chatgpt",
            title="Random chat",
            model="gpt-4",
            date="2026-05-22",
            first_prompt="What's the weather like?",
            messages=[]
        )
        result = self.organizer._classify_type(chat)
        assert result == "general"
    
    def test_organize_creates_file(self):
        chat = ChatExport(
            source="chatgpt",
            title="Test Conversation",
            model="gpt-4",
            date="2026-05-22",
            first_prompt="Hello world",
            messages=[{"role": "user", "content": "Hello world"}]
        )
        result = self.organizer.organize(chat)
        assert result is not None
        assert result.exists()
        assert result.suffix == '.md'
    
    def test_deduplication(self):
        chat = ChatExport(
            source="chatgpt",
            title="Duplicate",
            model="gpt-4",
            date="2026-05-22",
            first_prompt="Same content",
            messages=[{"role": "user", "content": "Same content"}]
        )
        first = self.organizer.organize(chat)
        second = self.organizer.organize(chat)
        assert first is not None
        assert second is None
    
    def test_sanitize_filename(self):
        result = self.organizer._sanitize_filename("Hello World! @#$ Test")
        assert result == "hello-world-test"
    
    def test_extract_tags(self):
        chat = ChatExport(
            source="chatgpt",
            title="Test",
            model="gpt-4-turbo",
            date="2026-05-22",
            first_prompt="How do I build a Python API?",
            messages=[]
        )
        tags = self.organizer._extract_tags(chat)
        assert "chatgpt" in tags
        assert any("model" in t for t in tags)
    
    def test_format_chat_has_frontmatter(self):
        chat = ChatExport(
            source="chatgpt",
            title="Test",
            model="gpt-4",
            date="2026-05-22",
            first_prompt="Hello",
            messages=[{"role": "user", "content": "Hello"}]
        )
        output = self.organizer._format_chat(chat)
        assert "---" in output
        assert "title: Test" in output
        assert "source: chatgpt" in output


class TestExportSorter:
    def test_scan_input_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sorter = ExportSorter(Path(tmpdir), Path(tmpdir))
            files = sorter.scan_input()
            assert len(files) == 0
    
    def test_scan_input_with_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            Path(tmpdir, "test1.txt").write_text("ChatGPT test")
            Path(tmpdir, "test2.json").write_text("{}")
            Path(tmpdir, "subdir").mkdir()
            Path(tmpdir, "subdir", "test3.md").write_text("Claude test")
            
            sorter = ExportSorter(Path(tmpdir), Path(tmpdir))
            files = sorter.scan_input()
            assert len(files) == 3
