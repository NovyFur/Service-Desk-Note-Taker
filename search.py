#!/usr/bin/env python3
"""
Search functionality for Service Desk Notes
"""

import os
import json
import datetime
import re
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QPushButton, QListWidget, QLabel, QSplitter,
                            QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QTimer

class SearchIndex:
    """Class to handle search indexing and searching"""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.index_file = os.path.join(data_dir, "search_index.json")
        self.index = self.load_index()
    
    def load_index(self):
        """Load existing index or create a new one"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                return {"files": {}, "last_update": ""}
        else:
            return {"files": {}, "last_update": ""}
    
    def save_index(self):
        """Save the index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f)
    
    def update_index(self):
        """Update the search index with all notes in the data directory"""
        # Get all text files in the data directory
        files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
        
        # Track new or modified files
        updated = False
        
        for filename in files:
            file_path = os.path.join(self.data_dir, filename)
            file_stat = os.stat(file_path)
            file_mtime = file_stat.st_mtime
            
            # Check if file is new or modified
            if filename not in self.index["files"] or self.index["files"][filename]["mtime"] != file_mtime:
                # Read file content
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Extract ticket number if present
                ticket_match = re.search(r'ticket[_\s]*(\d+)', filename, re.IGNORECASE)
                ticket_num = ticket_match.group(1) if ticket_match else ""
                
                # Store file info and content in index
                self.index["files"][filename] = {
                    "content": content,
                    "mtime": file_mtime,
                    "ticket": ticket_num,
                    "path": file_path
                }
                updated = True
        
        # Remove entries for deleted files
        for filename in list(self.index["files"].keys()):
            if filename not in files:
                del self.index["files"][filename]
                updated = True
        
        # Update last update timestamp
        if updated:
            self.index["last_update"] = datetime.datetime.now().isoformat()
            self.save_index()
        
        return updated
    
    def search(self, query):
        """Search the index for the given query"""
        # Update index first
        self.update_index()
        
        # Normalize query
        query = query.lower()
        results = []
        
        # Check if query is a ticket number
        is_ticket_search = query.isdigit()
        
        for filename, file_info in self.index["files"].items():
            # For ticket number search
            if is_ticket_search and query in file_info["ticket"]:
                results.append({
                    "filename": filename,
                    "path": file_info["path"],
                    "content": file_info["content"],
                    "relevance": 100  # Highest relevance for exact ticket match
                })
            # For text search
            elif query in file_info["content"].lower():
                # Calculate relevance based on number of occurrences
                content_lower = file_info["content"].lower()
                occurrences = content_lower.count(query)
                
                # Higher relevance for occurrences in the beginning
                first_pos = content_lower.find(query)
                relevance = occurrences * 10
                if first_pos < 100:  # If found in first 100 chars
                    relevance += 20
                
                results.append({
                    "filename": filename,
                    "path": file_info["path"],
                    "content": file_info["content"],
                    "relevance": relevance
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results


class SearchDialog(QDialog):
    """Search dialog for finding notes"""
    
    def __init__(self, data_dir, parent=None):
        super().__init__(parent)
        self.data_dir = data_dir
        self.search_index = SearchIndex(data_dir)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Search Notes")
        self.setGeometry(100, 100, 800, 500)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Search input and button
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term or ticket number...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # Connect enter key to search
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Results area with splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.currentItemChanged.connect(self.show_note_content)
        
        # Note content preview
        self.note_preview = QTextEdit()
        self.note_preview.setReadOnly(True)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.results_list)
        self.splitter.addWidget(self.note_preview)
        self.splitter.setSizes([300, 500])
        
        # Status label
        self.status_label = QLabel("Ready to search")
        
        # Add all to main layout
        layout.addLayout(search_layout)
        layout.addWidget(self.splitter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Update index on startup
        QTimer.singleShot(100, self.update_index)
    
    def update_index(self):
        """Update the search index"""
        updated = self.search_index.update_index()
        if updated:
            self.status_label.setText(f"Search index updated with {len(self.search_index.index['files'])} files")
        else:
            self.status_label.setText(f"Search index is up to date with {len(self.search_index.index['files'])} files")
    
    def perform_search(self):
        """Perform search with the current query"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a search term or ticket number.")
            return
        
        # Clear previous results
        self.results_list.clear()
        self.note_preview.clear()
        
        # Perform search
        results = self.search_index.search(query)
        
        if not results:
            self.status_label.setText("No results found")
            return
        
        # Display results
        for result in results:
            filename = result["filename"]
            self.results_list.addItem(filename)
        
        self.status_label.setText(f"Found {len(results)} results")
        
        # Select first result
        self.results_list.setCurrentRow(0)
    
    def show_note_content(self, current, previous):
        """Show the content of the selected note"""
        if not current:
            return
        
        filename = current.text()
        file_path = os.path.join(self.data_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            self.note_preview.setText(content)
        else:
            self.note_preview.setText("Error: File not found")
