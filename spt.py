import sys
import pyaudio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QTextEdit, QPushButton, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

class SpeechToTextWorker(QThread):
    text_updated = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.running = False
        self.audio_stream = None
        self.dg_connection = None

    def run(self):
        self.running = True
        try:
            # Audio configuration
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = 1024

            # Initialize audio stream
            audio = pyaudio.PyAudio()
            self.audio_stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            # Initialize Deepgram client
            deepgram = DeepgramClient(self.api_key)

            # Configure Deepgram options
            options = LiveOptions(
                model="nova",
                language="en-US",
                smart_format=True,
                interim_results=True,
                encoding="linear16",
                sample_rate=RATE,
                channels=CHANNELS
            )

            # Create websocket connection
            self.dg_connection = deepgram.listen.live.v("1")

            # Define callback functions
            def on_message(_, result, **kwargs):
                transcript = result.channel.alternatives[0].transcript
                if transcript:
                    self.text_updated.emit(transcript)

            def on_error(_, error, **kwargs):
                self.error_occurred.emit(str(error))

            # Register event handlers
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)

            # Start the connection
            self.dg_connection.start(options)

            # Main audio loop
            while self.running:
                data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                self.dg_connection.send(data)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.cleanup()

    def stop(self):
        self.running = False
        self.cleanup()

    def cleanup(self):
        if self.dg_connection:
            try:
                self.dg_connection.finish()
            except:
                pass
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None

class SpeechToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Speech-to-Text Converter")
        self.setGeometry(100, 100, 600, 400)
        self.worker = None
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # API Key Input
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("Deepgram API Key:"))
        
        self.api_key_input = QTextEdit()
        self.api_key_input.setMaximumHeight(30)
        self.api_key_input.setPlaceholderText("Enter your Deepgram API key")
        api_layout.addWidget(self.api_key_input)
        layout.addLayout(api_layout)
        
        # Text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Transcript will appear here...")
        layout.addWidget(self.text_display)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Listening")
        self.start_button.clicked.connect(self.start_listening)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
    def start_listening(self):
        api_key = self.api_key_input.toPlainText().strip()
        if not api_key:
            self.text_display.setPlainText("Please enter a valid Deepgram API key")
            return
            
        self.worker = SpeechToTextWorker(api_key)
        self.worker.text_updated.connect(self.update_text)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.text_display.setPlainText("Listening...\n")
        
    def stop_listening(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.text_display.append("\nStopped listening")
        
    def update_text(self, text):
        current_text = self.text_display.toPlainText()
    
        # Clear initial "Listening..." message
        if current_text == "Listening...\n":
            current_text = ""
        
        # If we have existing text and the new text doesn't start with punctuation
        if current_text and text and not text[0] in '.!?,;':
            # Add space between words
            if not current_text.endswith(' '):
                current_text += ' '
        
        self.text_display.setPlainText(current_text + text)
    
        # Auto-scroll to bottom
        cursor = self.text_display.textCursor()
        cursor.movePosition(cursor.End)
        self.text_display.setTextCursor(cursor)
            
    def clear_text(self):
        self.text_display.clear()
        
    def show_error(self, error_msg):
        self.text_display.append(f"\nError: {error_msg}")
        self.stop_listening()
        
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpeechToTextApp()
    window.show()
    sys.exit(app.exec_())