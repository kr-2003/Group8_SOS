from gtts import gTTS
import simpleaudio as sa
import os

# Define the text to convert to speech
text = "Hello, my dog is cute."

# Convert text to speech and save as an MP3 file
tts = gTTS(text=text, lang='en')
tts.save("hello.mp3")

# Convert MP3 to WAV using FFmpeg (requires FFmpeg installed)
os.system("ffmpeg -i hello.mp3 hello.wav")

# Play the WAV file using simpleaudio
wave_obj = sa.WaveObject.from_wave_file("hello.wav")
play_obj = wave_obj.play()
play_obj.wait_done()  # Wait until playback is finished
