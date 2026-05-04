# JARVIS

# J.A.R.V.I.S. - Personal AI Voice Assistant

J.A.R.V.I.S. is a sleek, Python-based desktop voice assistant designed for extreme speed and utility. It uses a modern Push-to-Talk interface to instantly listen to your voice commands, process them locally or through an ultra-fast cloud AI, and speak the results back to you.

## Core Features

- **Lightning Fast AI (Groq)**: Uses the `Groq` API and the `llama-3.3-70b-versatile` model to process conversational queries in milliseconds, avoiding the slow loading times of traditional AI APIs.
- **Universal App Launcher**: Integrated with `AppOpener`, Jarvis can search your entire Windows system and instantly launch any installed application (e.g., "Open Spotify", "Open Settings", "Open Chrome") or websites.
- **System Control**: Built-in OS commands allow you to securely manage your laptop just by speaking:
  - *"Lock the PC"*
  - *"Shut down the computer"*
  - *"Restart the laptop"*
- **Persistent Memory System**: A local JSON-based memory manager allows you to ask Jarvis to remember specific facts (e.g., *"Remember that my favorite color is blue"*) and recall them later (*"What is my favorite color?"*).
- **Push-to-Talk Interface**: A minimalistic CustomTkinter GUI that replaces slow 24/7 background listening with a highly responsive "Click to Speak" button, guaranteeing perfect audio capture without hitting API rate limits.
- **Thread-Safe TTS**: Uses `pyttsx3` forced onto the main Tkinter thread to completely bypass notorious Windows COM audio freezing bugs, ensuring the robotic voice always works perfectly.

## Architecture

The script is cleanly divided into modular classes:
1. `MemoryManager`: Handles reading/writing to `memory.json`.
2. `VoiceManager`: Uses `sounddevice` to record raw PCM audio and `speech_recognition` to convert it to text. Handles TTS via `pyttsx3`.
3. `AIManager`: Maintains a conversational context array and connects to the Groq API.
4. `CommandProcessor`: An intent-router that intercepts hardcoded system commands (like launching apps or checking the time) before falling back to the AI for general questions.
5. `JarvisApp`: The main Tkinter application that ties all managers together and handles multithreading.

## Requirements

Requires Python 3.14+ (or lower) with the following dependencies:
```powershell
pip install sounddevice numpy speechrecognition pyttsx3 customtkinter plyer groq AppOpener
```
