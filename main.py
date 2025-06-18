import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import pygame
import os
import google.generativeai as genai
import webbrowser
import requests
import musicLibrary  


pygame.mixer.init()

recognizer = sr.Recognizer()

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")

def speak(text):
    """Speak the given text using gTTS and pygame."""
    tts = gTTS(text)
    tts.save("temp.mp3")
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

def aiProcess(command):
    """Send the command to the AI model and return the response."""
    chat = model.start_chat()
    response = chat.send_message(command)
    return response.text

def processCommand(c, log_func):
    """Process commands for opening sites, playing music, news, or fallback AI."""
    c = c.lower()
    if "open google" in c:
        webbrowser.open("https://google.com")
        log_func("Opening Google...")
        speak("Opening Google")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        log_func("Opening YouTube...")
        speak("Opening YouTube")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
        log_func("Opening Facebook...")
        speak("Opening Facebook")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
        log_func("Opening LinkedIn...")
        speak("Opening LinkedIn")
    elif c.startswith("play"):
        # play song from your musicLibrary dictionary
        parts = c.split(" ", 1)
        if len(parts) < 2:
            speak("Please specify a song name.")
            log_func("No song specified in play command.")
            return
        song = parts[1]
        if song in musicLibrary.music:
            link = musicLibrary.music[song]
            webbrowser.open(link)
            log_func(f"Playing {song}...")
            speak(f"Playing {song}")
        else:
            speak("Sorry, I don't have that song.")
            log_func(f"Song not found: {song}")
    elif "news" in c:
        r = requests.get("NEWS_API_KEY")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            for article in articles[:5]:  # speak top 5 headlines
                log_func(article['title'])
                speak(article['title'])
        else:
            speak("Sorry, I couldn't fetch the news right now.")
            log_func("News API request failed.")
    else:
        response = aiProcess(c)
        log_func("Jarvis: " + response)
        speak(response)

def listen_for_wakeword(log_func, stop_event):
    """Background thread function to listen for wake word and commands."""
    while not stop_event.is_set():
        try:
            with sr.Microphone() as source:
                log_func("Listening for wake word 'jarvis'...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            wake_word = recognizer.recognize_google(audio).lower()
            log_func(f"Heard: {wake_word}")
            if "jarvis" in wake_word:
                speak("Yes, how can I help?")
                log_func("Listening for command...")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=10)
                command = recognizer.recognize_google(audio).lower()
                log_func(f"Command: {command}")
                
                if any(word in command for word in ["open google", "open youtube", "open facebook", "open linkedin", "play", "news"]):
                    processCommand(command, log_func)
                else:
                    response = aiProcess(command)
                    log_func("Jarvis: " + response)
                    speak(response)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            log_func("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            log_func(f"Speech recognition error: {e}")
        except Exception as e:
            log_func(f"Unexpected error: {e}")

def start_listening_thread(log_func, stop_event):
    """Starts the background thread for listening."""
    threading.Thread(target=listen_for_wakeword, args=(log_func, stop_event), daemon=True).start()

def main():
    stop_event = threading.Event()

    window = tk.Tk()
    window.title("Jarvis Assistant")

    # Create a scrolled text widget for logs/output
    txt_log = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20)
    txt_log.pack(padx=10, pady=10)

    def log(message):
        txt_log.insert(tk.END, message + "\n")
        txt_log.see(tk.END)

    btn_listen = tk.Button(window, text="Start Listening", command=lambda: start_listening_thread(log, stop_event))
    btn_listen.pack(pady=5)

    btn_quit = tk.Button(window, text="Quit", command=lambda: (stop_event.set(), window.destroy()))
    btn_quit.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    main()
