# Service Desk Notes - User Documentation

## Overview

Service Desk Notes is a custom note-taking application specifically designed for service desk professionals. It provides a streamlined way to create, save, and search notes related to service tickets, with features tailored to improve efficiency in a service desk environment.

## Features

### Quick Access Features
- **Global Hotkey**: Press `Ctrl+Alt+N` from anywhere to open the application
- **Minimalist Interface**: Clean, focused interface for distraction-free note-taking
- **System Tray Integration**: Application runs in the background and can be accessed from the system tray
- **Fast Saving**: Quickly save notes with automatic naming based on ticket numbers and timestamps

### Service Desk Specific Features
- **Ticket Number Linking**: Automatically link notes to ticket numbers
- **Predefined Templates**: Choose from templates designed for common service desk scenarios
- **Automatic Timestamping**: Notes are automatically timestamped when saved
- **User Information**: Your username is automatically included in notes

### Advanced Features
- **Search Functionality**: Powerful search capability to find notes by ticket number or content
- **Voice-to-Text**: Convert spoken words to text for hands-free note-taking
- **Keyboard Shortcuts**: Efficient keyboard shortcuts for common actions

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Installation Steps

1. Ensure Python and pip are installed on your system
2. Download and extract the Service Desk Notes package
3. Open a terminal/command prompt and navigate to the extracted directory
4. Run the installation script:

```bash
# On Linux/Mac
chmod +x install.sh
./install.sh

# On Windows
install.bat
```

This will:
- Create a virtual environment
- Install all required dependencies
- Set up the application for first use

## Usage

### Starting the Application

You can start the application in several ways:

1. **Using the launcher script**:
   ```bash
   # On Linux/Mac
   ./launch.sh
   
   # On Windows
   launch.bat
   ```

2. **Using the global hotkey**: Press `Ctrl+Alt+N` from anywhere (after the application has been started once)

### Creating Notes

1. When the application opens, you'll see a simple interface with fields for:
   - Ticket number
   - Template selection
   - Note content

2. Enter a ticket number in the "Ticket #" field
   - The application will automatically check your clipboard for ticket numbers when it opens

3. Select a template from the dropdown menu (optional)
   - Templates will automatically populate with the ticket number and current date/time

4. Enter your note content in the main text area
   - You can type directly or use the Voice-to-Text feature

5. Click "Save Note" or press `Ctrl+S` to save your note
   - Notes are saved in the data directory with filenames that include the ticket number and timestamp

### Using Templates

1. Select a template from the dropdown menu
2. The template will be loaded with placeholders filled in automatically:
   - `{ticket}` - Current ticket number
   - `{date}` - Current date and time
   - `{username}` - Your username

3. Default templates include:
   - **Issue Resolution**: For documenting problem resolution
   - **User Request**: For tracking user requests
   - **Follow-up**: For follow-up actions

### Searching Notes

1. Click the "Search Notes" button or press `Ctrl+F`
2. In the search dialog:
   - Enter a search term or ticket number
   - Click "Search" or press Enter
   - Results will appear in the list on the left
   - Click on a result to view its content on the right

3. Search is performed on:
   - Ticket numbers
   - Note content
   - Filenames

### Using Voice-to-Text

1. Click the "Voice to Text" button or press `Ctrl+Shift+V`
2. In the voice recording dialog:
   - Click "Start Recording" to begin recording
   - Speak clearly into your microphone
   - Click "Stop Recording" when finished or wait for the automatic timeout (60 seconds)
   - The transcribed text will be inserted at the cursor position in your note

**Note**: Voice-to-Text requires additional packages. If not already installed, you'll be prompted to install them.

## Keyboard Shortcuts

- `Ctrl+Alt+N`: Global hotkey to show/hide the application
- `Ctrl+S`: Save the current note
- `Ctrl+F`: Open the search dialog
- `Ctrl+Shift+V`: Open the voice recording dialog

## Customization

### Adding Custom Templates

1. Create a text file with your template content
2. Save it in the `templates` directory with a `.txt` extension
3. Use placeholders like `{ticket}`, `{date}`, and `{username}` as needed
4. Restart the application to see your new template in the dropdown menu

### Changing the Global Hotkey

The global hotkey can be changed by editing the configuration in the main.py file:

```python
CONFIG = {
    "hotkey": "ctrl+alt+n",  # Change this to your preferred hotkey
    # other settings...
}
```

## Troubleshooting

### Application Won't Start

- Ensure Python is installed and in your PATH
- Verify that all dependencies are installed
- Check that the virtual environment is properly set up
- Try running the application directly with:
  ```bash
  cd service_desk_notes
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  python main.py
  ```

### Voice-to-Text Not Working

- Ensure you have a working microphone
- Install the required packages:
  ```bash
  pip install SpeechRecognition pyaudio
  ```
- On Linux, you might need additional system packages:
  ```bash
  sudo apt-get install python3-pyaudio portaudio19-dev
  ```

### Search Not Finding Notes

- Make sure notes have been saved properly
- Update the search index by opening and closing the search dialog
- Check that you're searching for text that actually exists in your notes

## File Locations

- **Notes**: Stored in the `data` directory
- **Templates**: Stored in the `templates` directory
- **Configuration**: Settings are in the main.py file

## Support

For issues or feature requests, please contact your system administrator or the developer who provided this application.
