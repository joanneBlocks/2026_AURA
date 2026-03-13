import speech_recognition as sr
from gtts import gTTS
import io
import streamlit as st

def speak(text):
    """
    Converts text to speech using Google TTS and plays it in Streamlit.
    """
    try:
        # Generate speech as audio bytes (in memory)
        tts = gTTS(text=text, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Play audio in the browser
        st.audio(audio_fp, format='audio/mp3', start_time=0)
        
    except Exception as e:
        st.error(f"Audio Error: {e}")

def listen():
    """
    Listens to the microphone and returns text.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now.")
        try:
            # Adjust for ambient noise to improve accuracy
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5)
            
            text = r.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return "No speech detected."
        except sr.UnknownValueError:
            return "Could not understand audio."
        except Exception as e:
            return f"Error: {e}"