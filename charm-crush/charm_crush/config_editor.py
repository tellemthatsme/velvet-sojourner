"""
Config Editor for Charm Crush Session Manager
Handles file editing with syntax highlighting for JSON, YAML, INI, and TXT.
"""
import re
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (QPlainTextEdit, QTextEdit, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QComboBox, QPushButton,
                              QFileDialog, QMessageBox, QSplitter, QDialog,
                              QLineEdit, QCheckBox, QGridLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QRegularExpression
from PyQt6.QtGui import (QPainter, QColor, QFont, QSyntaxHighlighter, 
                          QTextFormat, QTextCursor, QKeySequence, QShortcut,
                          QFontDatabase, QTextCharFormat, QTextDocument)

from .utils import FileParser, FileFormat


class LineNumberArea(QWidget):
    """Line number area for the code editor"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QRect(0, 0, self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers and syntax highlighting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self._highlight_matching_bracket)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
        # Set font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        self.setFont(font)
        
        # Tab settings
        self.setTabStopDistance(40)
        
        # Bracket matching colors
        self._bracket_color = QColor("#264F78")
        self._matching_bracket_extra = QTextCharFormat()
        self._matching_bracket_extra.setBackground(QColor("#264F78").darker(120))
    
    def line_number_area_width(self):
        digit_count = len(str(self.blockCount()))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digit_count
        return space
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(
                    0, int(top), self.line_number_area.width(), 
                    self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlight_current_line(self):
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2d2d30")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def _highlight_matching_bracket(self):
        """Highlight matching bracket."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        
        char = cursor.document().characterAt(cursor.position())
        brackets = {'{': '}', '[': ']', '(': ')', '"': '"', "'": "'"}
        
        if char not in brackets:
            # Try current position
            cursor.movePosition(QTextCursor.MoveOperation.Right)
            char = cursor.document().characterAt(cursor.position())
        
        if char in brackets:
            matching_char = brackets[char]
            is_forward = char in '{(["\''
            
            # Find matching bracket
            find_cursor = QTextCursor(self.document())
            find_cursor.setPosition(cursor.position())
            
            bracket_count = 0
            found = False
            
            flags = QTextDocument.FindFlag(0)
            if not is_forward:
                flags |= QTextDocument.FindFlag.FindBackward
            
            # Implementation of manual bracket matching logic
            # (Simplifying for now to avoid the error)
            while True:
                find_cursor = self.document().find(matching_char if is_forward else char, find_cursor, flags)
                if find_cursor.isNull():
                    break
                # Simple case: find the first match
                found = True
                break
            
            if found:
                extra_selections = self.editor.extraSelections()
                selection = QTextEdit.ExtraSelection()
                selection.format = self._matching_bracket_extra
                selection.cursor = find_cursor
                selection.cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                extra_selections.append(selection)
                self.editor.setExtraSelections(extra_selections)
                return
        
        # Clear bracket highlighting if no match
        self.highlight_current_line()


class FindReplaceDialog(QDialog):
    """Find and replace dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = parent.editor if parent else None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(400)
        
        layout = QGridLayout()
        
        # Find label and field
        self.find_label = QLabel("Find:")
        layout.addWidget(self.find_label, 0, 0)
        
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Text to find...")
        layout.addWidget(self.find_edit, 0, 1)
        
        # Replace label and field
        self.replace_label = QLabel("Replace:")
        layout.addWidget(self.replace_label, 1, 0)
        
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Replacement text...")
        layout.addWidget(self.replace_edit, 1, 1)
        
        # Options
        self.case_sensitive = QCheckBox("Case sensitive")
        layout.addWidget(self.case_sensitive, 2, 0)
        
        self.whole_words = QCheckBox("Whole words")
        layout.addWidget(self.whole_words, 2, 1)
        
        self.regex_check = QCheckBox("Regular expression")
        layout.addWidget(self.regex_check, 3, 0)
        
        self.search_backward = QCheckBox("Search backward")
        layout.addWidget(self.search_backward, 3, 1)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel |
                                      QDialogButtonBox.StandardButton.Apply)
        
        self.find_next_btn = QPushButton("Find Next")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")
        
        button_box.addButton(self.find_next_btn, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(self.replace_btn, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(self.replace_all_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.find_next_btn.clicked.connect(self.find_next)
        self.replace_btn.clicked.connect(self.replace)
        self.replace_all_btn.clicked.connect(self.replace_all)
        
        layout.addWidget(button_box, 4, 0, 1, 2)
        
        self.setLayout(layout)
    
    def get_find_flags(self):
        """Get QTextCursor FindFlags based on options."""
        flags = QTextCursor.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextCursor.FindFlag.FindCaseSensitively
        if self.whole_words.isChecked():
            flags |= QTextCursor.FindFlag.FindWholeWords
        if self.regex_check.isChecked():
            flags |= QTextCursor.FindFlag.FindRegularExpression
        if self.search_backward.isChecked():
            flags |= QTextCursor.FindFlag.FindBackward
        return flags
    
    def find_next(self):
        """Find next occurrence."""
        if not self.editor:
            return
        
        text = self.find_edit.text()
        if not text:
            return
        
        flags = self.get_find_flags()
        
        # Start from current position
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor.selectionStart())
        
        found = cursor.movePosition(QTextCursor.MoveOperation.NoMove) if self.search_backward.isChecked() else cursor.find(text, flags)
        
        if not found:
            # Try from beginning
            cursor = QTextCursor(self.document())
            if self.search_backward.isChecked():
                cursor.movePosition(QTextCursor.MoveOperation.End)
            found = cursor.find(text, flags)
        
        if found:
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()
        else:
            QMessageBox.information(self, "Find", "Text not found")
    
    def replace(self):
        """Replace current occurrence."""
        if not self.editor:
            return
        
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_edit.text())
            self.editor.setTextCursor(cursor)
        self.find_next()
    
    def replace_all(self):
        """Replace all occurrences."""
        if not self.editor:
            return
        
        text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not text:
            return
        
        cursor = QTextCursor(self.document())
        flags = self.get_find_flags()
        count = 0
        
        # Clear selection
        cursor.clearSelection()
        
        while cursor.find(text, flags):
            cursor.insertText(replace_text)
            count += 1
            # Move back to avoid finding in replaced text
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
        
        QMessageBox.information(self, "Replace All", f"Replaced {count} occurrences")


class JsonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Key patterns
        key_pattern = QRegularExpression("\"[^\"]*\"\\s*:")
        self.highlighting_rules.append((key_pattern, QColor("#9cdcfe")))
        
        # String values
        string_pattern = QRegularExpression("\"[^\"]*\"")
        self.highlighting_rules.append((string_pattern, QColor("#ce9178")))
        
        # Numbers
        number_pattern = QRegularExpression("-?\\d+(\\.\\d+)?")
        self.highlighting_rules.append((number_pattern, QColor("#b5cea8")))
        
        # Booleans
        bool_pattern = QRegularExpression("(true|false|null)")
        self.highlighting_rules.append((bool_pattern, QColor("#569cd6")))
        
        # Brackets
        bracket_pattern = QRegularExpression("[\\[\\]{}]")
        self.highlighting_rules.append((bracket_pattern, QColor("#ffd700")))
    
    def highlightBlock(self, text):
        for pattern, color in self.highlighting_rules:
            match = pattern.match(text)
            while match.hasMatch():
                start = match.capturedStart(0)
                length = match.capturedLength(0)
                self.setFormat(start, length, color)
                match = pattern.match(text, start + length)


class YamlHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for YAML"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Keys (without colon)
        key_pattern = QRegularExpression("^\\s*[^#:]+:")
        self.highlighting_rules.append((key_pattern, QColor("#9cdcfe")))
        
        # String values
        string_pattern = QRegularExpression(":\\s*\"[^\"]*\"")
        self.highlighting_rules.append((string_pattern, QColor("#ce9178")))
        
        # Numbers
        number_pattern = QRegularExpression(":\\s*-?\\d+(\\.\\d+)?")
        self.highlighting_rules.append((number_pattern, QColor("#b5cea8")))
        
        # Booleans
        bool_pattern = QRegularExpression(":\\s*(true|false|yes|no)")
        self.highlighting_rules.append((bool_pattern, QColor("#569cd6")))
        
        # Comments
        comment_pattern = QRegularExpression("#.*")
        self.highlighting_rules.append((comment_pattern, QColor("#6a9955")))
        
        # Dashes
        dash_pattern = QRegularExpression("^\\s*-")
        self.highlighting_rules.append((dash_pattern, QColor("#ffd700")))
    
    def highlightBlock(self, text):
        for pattern, color in self.highlighting_rules:
            match = pattern.match(text)
            while match.hasMatch():
                start = match.capturedStart(0)
                length = match.capturedLength(0)
                self.setFormat(start, length, color)
                match = pattern.match(text, start + length)


class IniHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for INI files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Section headers
        section_pattern = QRegularExpression("\\[.*\\]")
        self.highlighting_rules.append((section_pattern, QColor("#ffd700")))
        
        # Keys
        key_pattern = QRegularExpression("^[^=]+=")
        self.highlighting_rules.append((key_pattern, QColor("#9cdcfe")))
        
        # Values
        value_pattern = QRegularExpression("=.*$")
        self.highlighting_rules.append((value_pattern, QColor("#ce9178")))
        
        # Comments
        comment_pattern = QRegularExpression("[;#].*$")
        self.highlighting_rules.append((comment_pattern, QColor("#6a9955")))
    
    def highlightBlock(self, text):
        for pattern, color in self.highlighting_rules:
            match = pattern.match(text)
            while match.hasMatch():
                start = match.capturedStart(0)
                length = match.capturedLength(0)
                self.setFormat(start, length, color)
                match = pattern.match(text, start + length)


class ConfigEditor(QWidget):
    """
    Configuration file editor widget with syntax highlighting.
    """
    
    contentChanged = pyqtSignal()
    fileSaved = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_file_path = None
        self.current_format = FileFormat.TXT
        self.modified = False
        self._find_dialog = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.format_label = QLabel("Format:")
        toolbar.addWidget(self.format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Auto-detect", "JSON", "YAML", "INI", "TXT"])
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        toolbar.addWidget(self.format_combo)
        
        toolbar.addStretch()
        
        # Editor
        self.editor = CodeEditor()
        self.highlighter = None
        
        layout.addLayout(toolbar)
        layout.addWidget(self.editor)
        
        self.setLayout(layout)
        
        # Connect signals
        self.editor.textChanged.connect(self.on_content_changed)
        
        # Set dark theme styles
        self.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
        }
        QPlainTextEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
        }
        """)
    
    def show_find_dialog(self):
        """Show find dialog."""
        if not self._find_dialog:
            self._find_dialog = FindReplaceDialog(self)
        self._find_dialog.show()
        self._find_dialog.find_edit.setFocus()
    
    def show_find_replace_dialog(self):
        """Show find/replace dialog."""
        if not self._find_dialog:
            self._find_dialog = FindReplaceDialog(self)
        self._find_dialog.show()
        self._find_dialog.replace_edit.setFocus()
    
    def find_text(self, text: str, forward: bool = True) -> bool:
        """Find text in editor."""
        if not text or not self.editor:
            return False
        
        cursor = self.editor.textCursor()
        if not forward:
            cursor.movePosition(QTextCursor.MoveOperation.Left)
        
        flags = QTextCursor.FindFlag(0) if forward else QTextCursor.FindFlag.FindBackward
        
        if cursor.find(text, flags):
            self.editor.setTextCursor(cursor)
            return True
        return False
    
    def load_file(self, file_path: str) -> bool:
        """
        Load a file into the editor.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful
        """
        try:
            format_type, content = FileParser.parse_file(file_path)
            
            if content is None:
                return False
            
            self.current_file_path = file_path
            self.current_format = format_type
            
            # Set format in combo
            format_names = ["JSON", "YAML", "INI", "TXT"]
            if format_type in format_names:
                self.format_combo.setCurrentText(format_type)
            
            # Format content for display
            if format_type in [FileFormat.JSON, FileFormat.YAML, FileFormat.INI]:
                display_content = FileParser.format_content(content, format_type)
            else:
                display_content = content if isinstance(content, str) else str(content)
            
            self.editor.setPlainText(display_content)
            self.modified = False
            
            # Apply syntax highlighting
            self.apply_highlighter(format_type)
            
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
            return False
    
    def load_content(self, content: str, file_format: str = None):
        """
        Load content directly into the editor.
        
        Args:
            content: Content to load
            file_format: File format (optional)
        """
        self.editor.setPlainText(content)
        self.current_format = file_format or FileFormat.TXT
        self.modified = False
        
        if file_format:
            format_names = ["JSON", "YAML", "INI", "TXT"]
            if file_format in format_names:
                self.format_combo.setCurrentText(file_format)
            self.apply_highlighter(file_format)
    
    def save_file(self, file_path: str = None) -> bool:
        """
        Save the current content to a file.
        
        Args:
            file_path: Path to save to (uses current if not provided)
            
        Returns:
            True if successful
        """
        save_path = file_path or self.current_file_path
        if not save_path:
            return False
        
        try:
            content = self.editor.toPlainText()
            
            # Parse and reformat based on format
            format_type = self.current_format
            
            if format_type in [FileFormat.JSON, FileFormat.YAML, FileFormat.INI]:
                # Parse and save formatted
                _, parsed = FileParser.parse_file(save_path)
                if parsed is not None:
                    formatted = FileParser.format_content(parsed, format_type)
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(formatted)
                else:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(content)
            else:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.modified = False
            self.fileSaved.emit(save_path)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
            return False
    
    def get_content(self) -> str:
        """Get the current content"""
        return self.editor.toPlainText()
    
    def get_parsed_content(self) -> tuple:
        """
        Get parsed content.
        
        Returns:
            Tuple of (format_type, parsed_content)
        """
        content = self.editor.toPlainText()
        return self.current_format, content
    
    def is_modified(self) -> bool:
        """Check if content has been modified"""
        return self.modified
    
    def on_content_changed(self):
        """Handle content changes"""
        self.modified = True
        self.contentChanged.emit()
    
    def on_format_changed(self, index):
        """Handle format change"""
        format_names = [FileFormat.TXT, FileFormat.JSON, FileFormat.YAML, FileFormat.INI]
        format_map = {
            0: FileFormat.TXT,  # Auto-detect -> TXT
            1: FileFormat.JSON,
            2: FileFormat.YAML,
            3: FileFormat.INI,
            4: FileFormat.TXT,
        }
        
        new_format = format_map.get(index, FileFormat.TXT)
        if new_format != self.current_format:
            self.current_format = new_format
            self.apply_highlighter(new_format)
    
    def apply_highlighter(self, format_type: str):
        """Apply syntax highlighting for the format"""
        # Remove existing highlighter
        if self.highlighter:
            self.highlighter.setDocument(None)
            self.highlighter.deleteLater()
            self.highlighter = None
        
        # Apply new highlighter
        if format_type == FileFormat.JSON:
            self.highlighter = JsonHighlighter(self.editor.document())
        elif format_type == FileFormat.YAML:
            self.highlighter = YamlHighlighter(self.editor.document())
        elif format_type == FileFormat.INI:
            self.highlighter = IniHighlighter(self.editor.document())
    
    def get_line_count(self) -> int:
        """Get the number of lines"""
        return self.editor.blockCount()
    
    def get_current_line(self) -> int:
        """Get the current line number (1-indexed)"""
        return self.editor.textCursor().blockNumber() + 1
    
    def get_current_column(self) -> int:
        """Get the current column number (1-indexed)"""
        return self.editor.textCursor().positionInBlock() + 1
    
    def go_to_line(self, line: int):
        """Go to a specific line"""
        cursor = QTextCursor(self.editor.document().findBlockByLineNumber(line - 1))
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
    
    def select_all(self):
        """Select all content"""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        self.editor.setTextCursor(cursor)
    
    def undo(self):
        """Undo last action"""
        self.editor.undo()
    
    def redo(self):
        """Redo last action"""
        self.editor.redo()
    
    def cut(self):
        """Cut selected content"""
        self.editor.cut()
    
    def copy(self):
        """Copy selected content"""
        self.editor.copy()
    
    def paste(self):
        """Paste content"""
        self.editor.paste()
    
    def set_read_only(self, read_only: bool):
        """Set editor read-only state"""
        self.editor.setReadOnly(read_only)
