#!/usr/bin/env python3
"""
Voice-to-text integration for Service Desk Notes
"""

import os
import sys
import threading
import time
import queue
import tempfile
import subprocess
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

class VoiceRecorder(QObject):
    """Class to handle voice recording and transcription"""
    
    # Define signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    transcription_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recording = False
        self.audio_queue = queue.Queue()
        self.temp_file = None
    
    def start_recording(self):
        """Start recording audio"""
        if self.recording:
            return
        
        # Create temporary file for audio
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_file.close()
        
        # Start recording thread
        self.recording = True
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self.recording_started.emit()
    
    def stop_recording(self):
        """Stop recording audio"""
        if not self.recording:
            return
        
        self.recording = False
        self.recording_stopped.emit()
        
        # Wait for recording thread to finish
        if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
        
        # Start transcription
        self.transcribe_thread = threading.Thread(target=self._transcribe_audio)
        self.transcribe_thread.daemon = True
        self.transcribe_thread.start()
    
    def _record_audio(self):
        """Record audio to file (runs in separate thread)"""
        try:
            # Check if we have pyaudio installed
            try:
                import pyaudio
                import wave
                
                # PyAudio parameters
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 16000
                
                # Initialize PyAudio
                p = pyaudio.PyAudio()
                
                # Open stream
                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)
                
                frames = []
                
                # Record audio
                while self.recording:
                    data = stream.read(CHUNK)
                    frames.append(data)
                
                # Stop and close stream
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                # Save to WAV file
                wf = wave.open(self.temp_file.name, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
            except ImportError:
                # Fallback to using system tools if pyaudio is not available
                self.error_occurred.emit("PyAudio not installed. Using system audio recording if available.")
                
                # Try using arecord (Linux) or other system tools
                try:
                    subprocess.run(['arecord', '-f', 'cd', '-d', '60', self.temp_file.name], 
                                  check=True, 
                                  stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    self.error_occurred.emit(f"Error recording audio: {e}")
                    return
                except FileNotFoundError:
                    self.error_occurred.emit("No audio recording tools found. Please install PyAudio or system audio tools.")
                    return
        
        except Exception as e:
            self.error_occurred.emit(f"Error during recording: {str(e)}")
    
    def _transcribe_audio(self):
        """Transcribe recorded audio to text (runs in separate thread)"""
        try:
            # Check if we have speech_recognition installed
            try:
                import speech_recognition as sr
                
                # Initialize recognizer
                r = sr.Recognizer()
                
                # Load audio file
                with sr.AudioFile(self.temp_file.name) as source:
                    audio_data = r.record(source)
                
                # Try to recognize speech
                try:
                    # Try Google's speech recognition service
                    text = r.recognize_google(audio_data)
                    self.transcription_complete.emit(text)
                except sr.UnknownValueError:
                    self.error_occurred.emit("Speech could not be understood")
                except sr.RequestError as e:
                    self.error_occurred.emit(f"Could not request results from service: {e}")
            
            except ImportError:
                # If speech_recognition is not installed
                self.error_occurred.emit("Speech recognition package not installed. Please install 'speech_recognition' package.")
                
                # Try to provide a helpful message about installation
                self.error_occurred.emit("To enable voice-to-text, please run: pip install SpeechRecognition pyaudio")
        
        except Exception as e:
            self.error_occurred.emit(f"Error during transcription: {str(e)}")
        
        finally:
            # Clean up temporary file
            if self.temp_file and os.path.exists(self.temp_file.name):
                try:
                    os.unlink(self.temp_file.name)
                except:
                    pass


class VoiceRecordDialog(QDialog):
    """Dialog for recording voice and converting to text"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recorder = VoiceRecorder()
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Voice Recording")
        self.setGeometry(200, 200, 400, 150)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Press 'Start Recording' to begin")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Timer for updating progress bar
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
    
    def connect_signals(self):
        """Connect signals from the recorder"""
        self.recorder.recording_started.connect(self.on_recording_started)
        self.recorder.recording_stopped.connect(self.on_recording_stopped)
        self.recorder.transcription_complete.connect(self.on_transcription_complete)
        self.recorder.error_occurred.connect(self.on_error)
    
    def toggle_recording(self):
        """Toggle recording state"""
        if not self.recorder.recording:
            self.recorder.start_recording()
        else:
            self.recorder.stop_recording()
    
    def on_recording_started(self):
        """Handle recording started signal"""
        self.record_button.setText("Stop Recording")
        self.status_label.setText("Recording... (max 60 seconds)")
        
        # Start progress timer
        self.progress_value = 0
        self.timer.start(600)  # Update every 600ms for 60 seconds total
    
    def on_recording_stopped(self):
        """Handle recording stopped signal"""
        self.timer.stop()
        self.progress_bar.setValue(100)
        self.status_label.setText("Transcribing audio...")
        self.record_button.setEnabled(False)
    
    def on_transcription_complete(self, text):
        """Handle transcription complete signal"""
        self.result_text = text
        self.accept()
    
    def on_error(self, message):
        """Handle error signal"""
        QMessageBox.warning(self, "Error", message)
        self.reject()
    
    def update_progress(self):
        """Update progress bar during recording"""
        self.progress_value += 1
        if self.progress_value >= 100:
            self.recorder.stop_recording()
            return
        
        self.progress_bar.setValue(self.progress_value)
    
    def get_text(self):
        """Get the transcribed text"""
        if hasattr(self, 'result_text'):
            return self.result_text
        return ""
