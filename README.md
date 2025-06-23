# Talk-Text: Live Speech-to-Text Converter

A real-time speech recognition application using Deepgram's API and PyQt5 for GUI. Captures microphone input and displays live transcriptions.

## Features

- ✅ **Real-time transcription** – Converts speech to text instantly
- ✅ **Microphone streaming** – Uses PyAudio for live audio capture
- ✅ **GUI controls** – Start/Stop listening and clear text
- ✅ **Error handling** – Displays API and connection errors
- ✅ **Threaded processing** – Prevents UI freezing during transcription

## Prerequisites

- Python 3.7+
- A valid [Deepgram API Key](https://console.deepgram.com/signup) (Free tier available)

## Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/ALLURKARSUSHANTH/TALK-TEXT.git
   cd Talk-Text
2. **Install dependencies**
   ```sh
   pip install PyQt5 pyaudio deepgram-sdk
3. **Run the application**
   ```sh
   python spt.py

