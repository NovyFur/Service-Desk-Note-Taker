#!/usr/bin/env python3
"""
Service Desk Notes - A custom note-taking application for service desk professionals
"""

import sys
import os
import json
import datetime
import keyboard
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QLabel, QComboBox, QSystemTrayIcon, QMenu, QAction,
                            QMessageBox, QShortcut, QStyle)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QKeySequence

# Import custom modules
from search import SearchDialog
from voice import VoiceRecordDialog

# Configuration
CONFIG = {
    "hotkey": "ctrl+alt+n",
    "data_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
    "templates_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
    "save_format": "%Y-%m-%d_%H-%M-%S",
    "username": os.environ.get("USER", "service_desk_user")
}

# Ensure directories exist
os.makedirs(CONFIG["data_dir"], exist_ok=True)
os.makedirs(CONFIG["templates_dir"], exist_ok=True)

class ServiceDeskNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_global_hotkey()
        self.setup_tray_icon()
        self.load_templates()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Service Desk Notes")
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Ticket information section
        ticket_layout = QHBoxLayout()
        ticket_label = QLabel("Ticket #:")
        self.ticket_input = QLineEdit()
        self.ticket_input.setPlaceholderText("Enter ticket number")
        ticket_layout.addWidget(ticket_label)
        ticket_layout.addWidget(self.ticket_input)
        
        # Template selection
        template_layout = QHBoxLayout()
        template_label = QLabel("Template:")
        self.template_combo = QComboBox()
        self.template_combo.addItem("None")
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_combo)
        
        # Connect template selection to update note content
        self.template_combo.currentIndexChanged.connect(self.apply_template)
        
        # Note content
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Enter your notes here...")
        
        # Button section
        button_layout = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton("Save Note")
        self.save_button.clicked.connect(self.save_note)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_note)
        
        # Search button
        self.search_button = QPushButton("Search Notes")
        self.search_button.clicked.connect(self.open_search)
        
        # Voice button
        self.voice_button = QPushButton("Voice to Text")
        self.voice_button.clicked.connect(self.open_voice_record)
        
        # Add buttons to layout
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.voice_button)
        
        # Add all sections to main layout
        main_layout.addLayout(ticket_layout)
        main_layout.addLayout(template_layout)
        main_layout.addWidget(self.note_edit)
        main_layout.addLayout(button_layout)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Set up keyboard shortcuts
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_note)
        
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(self.open_search)
        
        self.shortcut_voice = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.shortcut_voice.activated.connect(self.open_voice_record)
        
        # Try to get ticket number from clipboard
        QTimer.singleShot(100, self.check_clipboard_for_ticket)
    
    def check_clipboard_for_ticket(self):
        """Check if clipboard contains a ticket number"""
        clipboard_text = pyperclip.paste()
        # Simple check for ticket number format (can be customized)
        if clipboard_text and clipboard_text.strip().isdigit():
            self.ticket_input.setText(clipboard_text.strip())
    
    def setup_global_hotkey(self):
        """Set up global hotkey to show the application"""
        keyboard.add_hotkey(CONFIG["hotkey"], self.toggle_window)
    
    def setup_tray_icon(self):
        """Set up system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        # Use a default icon since we don't have a custom one
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        
        search_action = QAction("Search Notes", self)
        search_action.triggered.connect(self.open_search)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(search_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window()
    
    def toggle_window(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show_window()
    
    def show_window(self):
        """Show and activate the window"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        self.raise_()
    
    def quit_application(self):
        """Quit the application"""
        QApplication.quit()
    
    def load_templates(self):
        """Load available templates from templates directory"""
        # Clear existing templates except "None"
        while self.template_combo.count() > 1:
            self.template_combo.removeItem(1)
        
        # Add default templates
        self.add_default_templates()
        
        # Load templates from files
        template_files = [f for f in os.listdir(CONFIG["templates_dir"]) 
                         if f.endswith('.txt') or f.endswith('.json')]
        
        for template_file in template_files:
            template_name = os.path.splitext(template_file)[0]
            self.template_combo.addItem(template_name)
    
    def add_default_templates(self):
        """Add default templates"""
        default_templates = {
            "Issue Resolution": "Ticket: {ticket}\nDate: {date}\nUser: {username}\n\nIssue Description:\n\nTroubleshooting Steps:\n1. \n2. \n3. \n\nResolution:\n\n",
            "User Request": "Ticket: {ticket}\nDate: {date}\nUser: {username}\n\nRequest Details:\n\nAction Taken:\n\nStatus: Pending/Completed\n",
            "Follow-up": "Ticket: {ticket}\nDate: {date}\nUser: {username}\n\nFollow-up Notes:\n\nNext Steps:\n\n"
        }
        
        # Save default templates to files if they don't exist
        for name, content in default_templates.items():
            file_path = os.path.join(CONFIG["templates_dir"], f"{name}.txt")
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Add to combo box
            self.template_combo.addItem(name)
    
    def apply_template(self):
        """Apply the selected template to the note content"""
        template_name = self.template_combo.currentText()
        if template_name == "None":
            return
        
        # Load template content
        template_path = os.path.join(CONFIG["templates_dir"], f"{template_name}.txt")
        if not os.path.exists(template_path):
            template_path = os.path.join(CONFIG["templates_dir"], f"{template_name}.json")
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Replace placeholders
            now = datetime.datetime.now()
            ticket_num = self.ticket_input.text() or "[TICKET_NUMBER]"
            
            template_content = template_content.replace("{ticket}", ticket_num)
            template_content = template_content.replace("{date}", now.strftime("%Y-%m-%d %H:%M"))
            template_content = template_content.replace("{username}", CONFIG["username"])
            
            # Set the content
            self.note_edit.setText(template_content)
    
    def save_note(self):
        """Save the current note"""
        note_content = self.note_edit.toPlainText()
        if not note_content.strip():
            QMessageBox.warning(self, "Empty Note", "Cannot save an empty note.")
            return
        
        # Get ticket number
        ticket_num = self.ticket_input.text()
        
        # Create filename
        now = datetime.datetime.now()
        date_str = now.strftime(CONFIG["save_format"])
        
        if ticket_num:
            filename = f"ticket_{ticket_num}_{date_str}.txt"
        else:
            filename = f"note_{date_str}.txt"
        
        # Save the note
        file_path = os.path.join(CONFIG["data_dir"], filename)
        try:
            with open(file_path, 'w') as f:
                f.write(note_content)
            
            QMessageBox.information(self, "Note Saved", f"Note saved to {filename}")
            
            # Clear the note content but keep the ticket number
            self.note_edit.clear()
            self.template_combo.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note: {str(e)}")
    
    def clear_note(self):
        """Clear the note content"""
        self.note_edit.clear()
        self.template_combo.setCurrentIndex(0)
    
    def open_search(self):
        """Open the search dialog"""
        search_dialog = SearchDialog(CONFIG["data_dir"], self)
        if search_dialog.exec_():
            # If needed, handle search result selection here
            pass
    
    def open_voice_record(self):
        """Open the voice recording dialog"""
        voice_dialog = VoiceRecordDialog(self)
        if voice_dialog.exec_():
            # Get transcribed text and insert into note
            text = voice_dialog.get_text()
            if text:
                # Insert at cursor position or append to end
                cursor = self.note_edit.textCursor()
                cursor.insertText(text)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    
    window = ServiceDeskNotes()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
