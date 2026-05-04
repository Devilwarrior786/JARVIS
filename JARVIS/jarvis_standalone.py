import os
import json
import time
import threading
import datetime
import webbrowser
import subprocess
import tkinter as tk
import speech_recognition as sr
import pyttsx3
import customtkinter as ctk
from plyer import notification
import sounddevice as sd
import numpy as np
from groq import Groq
import AppOpener

# ==========================================
# CONFIGURATION
# ==========================================
# 1. Create a free account at https://console.groq.com
# 2. Go to API Keys and create a new key
# 3. Paste it below:
GROQ_API_KEY = "gsk_" 

# ==========================================
# 1. MEMORY MANAGER
# ==========================================
class MemoryManager:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return {}
        return {}

    def save_memory(self):
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def remember(self, key, value):
        self.memory[key] = value
        self.save_memory()
        return f"I will remember that your {key} is {value}."

    def recall(self, key):
        return self.memory.get(key, f"I don't remember anything about your {key}.")

# ==========================================
# 2. VOICE MANAGER
# ==========================================
class VoiceManager:
    def __init__(self, app_callback):
        self.app_callback = app_callback
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 1.0)
        
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)
            
        self.recognizer = sr.Recognizer()

    def speak(self, text):
        print(f"Jarvis: {text}")
        self.app_callback("status", "Speaking...")
        # Force UI update before speaking
        if hasattr(self.app_callback, '__self__'):
            self.app_callback.__self__.update()
            
        self.engine.say(text)
        self.engine.runAndWait()
        
        self.app_callback("status", "Ready")
        self.app_callback("reset_button")

    def record_and_process(self):
        """Records for 5 seconds when the user clicks the button"""
        sample_rate = 16000
        duration = 5 # seconds
        
        self.app_callback("status", "Listening... (Speak now)")
        try:
            print("[Debug] Recording started...")
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait() # Wait for 5 seconds
            print("[Debug] Recording finished.")
            
            self.app_callback("status", "Processing Speech...")
            audio_data = sr.AudioData(recording.tobytes(), sample_rate, 2)
            
            try:
                text = self.recognizer.recognize_google(audio_data).lower()
                print(f"[Debug] Heard: {text}")
                self.app_callback("process_command", text)
            except sr.UnknownValueError:
                print("[Debug] Could not understand audio.")
                self.app_callback("status", "Didn't catch that. Try again.")
                self.app_callback("reset_button")
            except sr.RequestError as e:
                print(f"[Debug] Network error: {e}")
                self.app_callback("status", "Network Error.")
                self.app_callback("reset_button")
                
        except Exception as e:
            print(f"Listener error: {e}")
            self.app_callback("reset_button")

# ==========================================
# 3. AI MANAGER (GROQ)
# ==========================================
class AIManager:
    def __init__(self, api_key):
        self.api_key = api_key
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception:
            self.client = None
            
        self.context = [
            {"role": "system", "content": "You are a helpful, concise AI assistant named Jarvis. Keep your answers brief and conversational. Do not use formatting like bolding or lists, since your response will be read aloud by a Text-to-Speech engine."}
        ]

    def ask(self, prompt):
        if not self.client or self.api_key.startswith("gsk_..."):
            return "My Groq API key is missing. Please add it to the configuration file."
            
        self.context.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                messages=self.context,
                model="llama-3.3-70b-versatile",
                max_tokens=150,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
            self.context.append({"role": "assistant", "content": answer})
            
            if len(self.context) > 11:
                self.context = [self.context[0]] + self.context[-10:]
                
            return answer
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "I'm having trouble connecting to my AI brain."

# ==========================================
# 4. COMMAND PROCESSOR
# ==========================================
class CommandProcessor:
    def __init__(self, ai_manager, memory_manager):
        self.ai = ai_manager
        self.memory = memory_manager

    def process(self, text):
        text = text.lower()
        
        if "time" in text and "what" in text:
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        elif "date" in text and "what" in text:
            return f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}."
        elif "lock" in text and ("pc" in text or "laptop" in text or "computer" in text):
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking the computer."
        elif "shut down" in text or "shutdown" in text:
            # Added a 5 second delay so it's not dangerously instant
            os.system("shutdown /s /t 5")
            return "Shutting down the computer in 5 seconds."
        elif "restart" in text and ("pc" in text or "laptop" in text or "computer" in text):
            os.system("shutdown /r /t 5")
            return "Restarting the computer in 5 seconds."
        elif text.startswith("open "):
            app_name = text.replace("open ", "").strip()
            
            websites = {
                "youtube": "https://www.youtube.com",
                "google": "https://www.google.com",
                "chatgpt": "https://chatgpt.com",
                "facebook": "https://www.facebook.com",
                "spotify": "https://open.spotify.com"
            }
            if app_name in websites:
                webbrowser.open(websites[app_name])
                return f"Opening {app_name}."
                
            try:
                AppOpener.open(app_name, match_closest=True, throw_error=True)
                return f"Opening {app_name}."
            except Exception:
                return f"I couldn't find an application named {app_name} on your computer."
        elif "remember that my" in text:
            parts = text.split("remember that my")
            if len(parts) > 1:
                fact = parts[1].strip()
                if " is " in fact:
                    key, value = fact.split(" is ", 1)
                    return self.memory.remember(key.strip(), value.strip())
        elif "what is my" in text:
            parts = text.split("what is my")
            if len(parts) > 1:
                return self.memory.recall(parts[1].strip())
        else:
            return self.ai.ask(text)

# ==========================================
# 5. UI MANAGER & MAIN APP
# ==========================================
class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Jarvis AI Assistant")
        self.geometry("300x250")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.memory = MemoryManager()
        self.ai = AIManager(GROQ_API_KEY)
        self.processor = CommandProcessor(self.ai, self.memory)
        self.voice = VoiceManager(self.handle_event)

        self.setup_ui()
        self.show_notification("System Online", "Jarvis has been initialized.")

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="J.A.R.V.I.S.", font=("Helvetica", 24, "bold"))
        self.title_label.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", font=("Helvetica", 14), text_color="cyan")
        self.status_label.pack(pady=10)
        
        self.toggle_btn = ctk.CTkButton(self, text="Click to Speak (5s)", command=self.start_recording, font=("Helvetica", 14, "bold"), height=50)
        self.toggle_btn.pack(pady=20)

    def show_notification(self, title, message):
        try:
            notification.notify(title=title, message=message, app_name="Jarvis", timeout=5)
        except Exception:
            pass

    def handle_event(self, event_type, data=None):
        if event_type == "status":
            self.after(0, lambda: self.status_label.configure(text=f"Status: {data}"))
        elif event_type == "process_command":
            threading.Thread(target=self.execute_command, args=(data,), daemon=True).start()
        elif event_type == "reset_button":
            self.after(0, lambda: self.toggle_btn.configure(state="normal", text="Click to Speak (5s)", fg_color=["#3a7ebf", "#1f538d"]))

    def execute_command(self, command):
        self.handle_event("status", "Thinking...")
        response = self.processor.process(command)
        
        if response:
            # Speak on the main thread to prevent pyttsx3 from silencing
            self.after(0, lambda: self.voice.speak(response))

    def start_recording(self):
        self.toggle_btn.configure(state="disabled", text="Recording...", fg_color="red")
        threading.Thread(target=self.voice.record_and_process, daemon=True).start()

if __name__ == "__main__":
    app = JarvisApp()
    app.mainloop()
