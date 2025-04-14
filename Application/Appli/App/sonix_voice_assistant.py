import sys
import os
import sounddevice as sd
import numpy as np
import whisper
import pyttsx3
from datetime import datetime
from pymongo import MongoClient
from scipy.io.wavfile import write  # For saving audio

from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QPalette, QBrush, QLinearGradient, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QWidget
)

# Base directory for resource access
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load Whisper model once
try:
    whisper_model = whisper.load_model("base")
except Exception as e:
    print(f"⚠️ Whisper model loading failed: {e}")
    sys.exit(1)

class SonixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SONIX")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "mic.png")))

        self.engine = pyttsx3.init()
        self.is_dark_mode = True
        self.listening = False

        # Connect to MongoDB
        try:
            self.client = MongoClient("mongodb://127.0.0.1:27017")
            self.db = self.client["sonix_db"]
            self.history_collection = self.db["history"]
            self.history_collection.insert_one({"status": "✅ Connected to MongoDB from SONIX"})
            print("✅ Connected to MongoDB from SONIX")
        except Exception as e:
            print("❌ MongoDB connection failed:", e)
            self.history_collection = None

        self.initUI()
        self.apply_theme()

    def initUI(self):
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.left_panel = QVBoxLayout()
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignTop)
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.left_panel.addWidget(self.status_label, alignment=Qt.AlignTop)

        self.right_panel = QVBoxLayout()
        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 12px;")
        self.right_panel.addWidget(self.chat_output)

        self.control_layout = QHBoxLayout()

        self.mic_button = QPushButton()
        self.mic_button.setIcon(QIcon(os.path.join(BASE_DIR, "mic.png")))
        self.mic_button.setIconSize(QSize(36, 36))
        self.mic_button.setFixedSize(60, 60)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #b0b0b0;
            }
        """)
        self.mic_button.clicked.connect(self.start_listening)
        self.control_layout.addWidget(self.mic_button)

        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setIcon(QIcon(os.path.join(BASE_DIR, "lightmode.png")))
        self.toggle_button.setIconSize(QSize(24, 24))
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_theme)
        self.control_layout.addWidget(self.toggle_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(os.path.join(BASE_DIR, "stop.png")))
        self.stop_button.setIconSize(QSize(36, 36))
        self.stop_button.setFixedSize(60, 60)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #b0b0b0;
            }
        """)
        self.stop_button.clicked.connect(self.stop_listening)
        self.control_layout.addWidget(self.stop_button)

        self.right_panel.addLayout(self.control_layout)

        main_layout.addLayout(self.left_panel, 1)
        main_layout.addLayout(self.right_panel, 3)

    def apply_theme(self):
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 1, 1)

        if self.is_dark_mode:
            gradient.setColorAt(0.0, QColor("#0f172a"))
            gradient.setColorAt(1.0, QColor("#1e293b"))
            self.toggle_button.setIcon(QIcon(os.path.join(BASE_DIR, "lightmode.png")))
            self.chat_output.setStyleSheet("background-color: #0f172a; color: white; border: none;")
            self.status_label.setStyleSheet("color: white;")
        else:
            gradient.setColorAt(0.0, QColor("#f8fafc"))
            gradient.setColorAt(1.0, QColor("#e2e8f0"))
            self.toggle_button.setIcon(QIcon(os.path.join(BASE_DIR, "darkmode.png")))
            self.chat_output.setStyleSheet("background-color: #f1f5f9; color: black; border: none;")
            self.status_label.setStyleSheet("color: black;")

        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def start_listening(self):
        if self.listening:
            return
        self.status_label.setText("Listening...")
        self.chat_output.append("🎙️ Listening...")
        self.listening = True
        QTimer.singleShot(100, self.capture_voice)

    def stop_listening(self):
        self.status_label.setText("Stopped")
        self.chat_output.append("🛑 Stopped Listening")
        self.listening = False

    def capture_voice(self):
        if not self.listening:
            return
        try:
            self.status_label.setText("Recording...")
            duration = 10
            sample_rate = 16000
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()

            # Save audio to .wav file
            filename = os.path.join(BASE_DIR, f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            write(filename, sample_rate, audio)
            print(f"🎧 Saved audio to {filename}")

            audio_np = np.squeeze(audio)
            whisper_audio = whisper.pad_or_trim(audio_np)
            mel = whisper.log_mel_spectrogram(whisper_audio).to(whisper_model.device)

            self.status_label.setText("Transcribing...")
            result = whisper_model.decode(mel)
            query = result.text.strip()

            if query:
                self.chat_output.append(f"🗣️ You: {query}")
                self.process_command(query)
            else:
                self.chat_output.append("⚠️ Could not understand. Try again.")

        except Exception as e:
            self.chat_output.append(f"⚠️ Error: {str(e)}")
        finally:
            self.status_label.setText("Idle")
            self.listening = False

    def process_command(self, command):
        command = command.lower()
        response = "Sorry, I can't help with that."

        if "calculator" in command:
            os.system("calc" if os.name == "nt" else "gnome-calculator")
            response = "Opening Calculator"
        elif "notepad" in command:
            os.system("notepad" if os.name == "nt" else "gedit")
            response = "Opening Notepad"
        elif "browser" in command:
            os.system("start chrome" if os.name == "nt" else "xdg-open https://www.google.com")
            response = "Opening Browser"
        elif "document" in command:
            import subprocess

            if os.name == "nt":
                word_paths = [
                    r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"
                ]
                user = os.getlogin()
                normal_template = fr"C:\Users\{user}\AppData\Roaming\Microsoft\Templates\Normal.dotm"

                for path in word_paths:
                    if os.path.exists(path):
                        subprocess.Popen([path, '/t', normal_template])  # full absolute path!
                        response = "Opening Microsoft Word with a blank editable document"
                        break
                else:
                    os.system("start https://www.office.com/launch/word")
                    response = "Opening Word Online"
            # if os.name == "nt":
            #     word_path = [ r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE" ]
            #     possible_paths = [
            #         r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            #         r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            #         r"C:\Program Files\Microsoft Office\Office15\WINWORD.EXE",
            #         r"C:\Program Files (x86)\Microsoft Office\Office15\WINWORD.EXE"
            #     ]
            #     for path in possible_paths:
            #         if os.path.exists(path):
            #             os.startfile(path)
            #             response = "Opening Microsoft Word"
            #             break
            #     else:
            #         response = "Microsoft Word is not installed in default locations."
            # else:
            #     os.system("xdg-open https://www.office.com/launch/word")
            #     response = "Opening Word Online"

        # Save to MongoDB if available
        if self.history_collection is not None:
            try:
                self.history_collection.insert_one({
                    "command": command,
                    "response": response,
                    "timestamp": datetime.now()
                })
                print("📝 Command saved to MongoDB")
            except Exception as e:
                print("❌ Failed to save to MongoDB:", e)

        self.engine.say(response)
        self.engine.runAndWait()
        self.chat_output.append(f"🤖 Sonix: {response}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sonix = SonixApp()
    sonix.show()
    sys.exit(app.exec_())
