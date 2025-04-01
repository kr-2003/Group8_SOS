import pyttsx3

engine = pyttsx3.init()  # Initialize the TTS engine
engine.say("Hello, this is a test of pyttsx3.")  # Text to be spoken
engine.runAndWait()  # Run the speech engine
