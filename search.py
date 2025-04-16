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
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e: 
                print(f"Error loading index file: {e}")
                return {"files": {}, "last_update": ""}
        else:
            return {"files": {}, "last_update": ""}
    
    def save_index(self):
        """Save the index to disk"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f: 
                json.dump(self.index, f, indent=4) 
        except Exception as e:
             print(f"Error saving index file: {e}")

    def update_index(self):
        """Update the search index with all notes in the data directory"""
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
        except FileNotFoundError:
            print(f"Error: Data directory not found: {self.data_dir}")
            # Optionally create the directory here if desired
            # os.makedirs(self.data_dir, exist_ok=True) 
            return False 

        updated = False
        indexed_files = set(self.index["files"].keys())
        current_files = set(files)

        for filename in files:
            try:
                file_path = os.path.join(self.data_dir, filename)
                file_stat = os.stat(file_path)
                file_mtime = file_stat.st_mtime
                
                if filename not in self.index["files"] or self.index["files"][filename].get("mtime") != file_mtime: # Use .get for safety
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f: 
                            content = f.read()
                    except Exception as e:
                        print(f"Error reading file {filename}: {e}")
                        continue 
                    
                    ticket_match = re.search(r'ticket[_\s]*(\d+)', filename, re.IGNORECASE)
                    ticket_num = ticket_match.group(1) if ticket_match else ""
                    
                    self.index["files"][filename] = {
                        "title": filename, 
                        "content": content,
                        "mtime": file_mtime,
                        "ticket": ticket_num, 
                        "path": file_path
                    }
                    updated = True
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue 

        files_to_remove = indexed_files - current_files
        for filename in files_to_remove:
            if filename in self.index["files"]:
                 del self.index["files"][filename]
                 updated = True
        
        if updated:
            self.index["last_update"] = datetime.datetime.now().isoformat()
            self.save_index()
            print(f"Search index updated. Total files indexed: {len(self.index['files'])}")
        
        return updated
    
    def search(self, query):
        """Search the index for the given query"""
        # Update index first
        self.update_index()
        
        # Normalize query
        query = query.strip().lower()
        if not query:
            return [] # Return empty list for empty query
        results = []
        
        # Check if query is a ticket number
        is_ticket_search = query.isdigit()
        
        for filename, file_info in self.index["files"].items():
            # Safely get data, defaulting to empty strings
            content_lower = file_info.get("content", "").lower()
            title_lower = file_info.get("title", "").lower() 
            ticket_num = file_info.get("ticket", "") # String, might be ""

            # Check for matches in each relevant field
            query_in_content = query in content_lower
            query_in_title = query in title_lower
            # Check for partial ticket number match (if ticket_num exists)
            query_in_ticket = bool(ticket_num and query in ticket_num) 

            # If the query matches *any* field, calculate relevance
            if query_in_content or query_in_title or query_in_ticket:
                current_relevance = 0

                # --- Relevance Calculation ---

                # 1. Ticket Number Relevance (Highest Priority)
                if query_in_ticket:
                    if query == ticket_num: # Exact match gives huge boost
                        current_relevance += 100 
                    else: # Partial match gives significant boost
                        current_relevance += 50 # Score for partial ticket match

                # 2. Title Relevance (High Priority)
                if query_in_title:
                    title_occurrences = title_lower.count(query)
                    # Add relevance based on occurrences in title
                    current_relevance += title_occurrences * 15 
                    # Add bonus for any match in title
                    current_relevance += 10 

                # 3. Content Relevance (Standard Priority)
                if query_in_content:
                    content_occurrences = content_lower.count(query)
                    # Add relevance based on occurrences in content
                    current_relevance += content_occurrences * 5 
                    
                    # Bonus for query appearing early in the content
                    try:
                        first_pos_content = content_lower.find(query)
                        # Add bonus if found within the first 100 characters
                        if first_pos_content != -1 and first_pos_content < 100: 
                            current_relevance += 20
                    except: 
                        # Ignore potential errors if content isn't string-like (shouldn't happen here)
                        pass 

                # --- Add to results if relevant ---
                # Ensure we only add if there was actually a match contributing relevance
                if current_relevance > 0:
                    results.append({
                        "filename": filename,
                        "path": file_info.get("path", ""), 
                        "content": file_info.get("content", ""), 
                        "relevance": current_relevance 
                    })

        # Sort results by relevance (highest first)
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
