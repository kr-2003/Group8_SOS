import queue
import sys
import threading
import time
from datetime import datetime

import numpy as np
import pyaudio
import torch
from faster_whisper import WhisperModel

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms chunks
CHANNELS = 1
FORMAT = pyaudio.paInt16

# Load Whisper model
print("Loading Whisper model...")
model_size = "tiny.en"
model = WhisperModel(model_size, device="cpu", compute_type="float32")
print("Model loaded!")

TRANSCRIPT_FILE = "transcription.txt"
BUFFER_DURATION = 5.0 

class AudioProcessor:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Create or clear the transcript file
        with open(TRANSCRIPT_FILE, 'w') as f:
            f.write(f"Transcription started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback function"""
        audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def process_audio(self):
        """Process audio segments from the queue and transcribe them continuously"""
        audio_buffer = np.array([], dtype=np.float32)
        buffer_size_samples = int(RATE * BUFFER_DURATION)
        
        while not self.stop_event.is_set():
            # Get audio from queue
            try:
                audio_data = self.audio_queue.get(timeout=0.5)
                audio_buffer = np.concatenate((audio_buffer, audio_data))
                
                # Process audio when buffer reaches the fixed duration
                if len(audio_buffer) >= buffer_size_samples:
                    # Create a copy of the buffer for processing
                    with self.lock:
                        process_buffer = audio_buffer.copy()
                        # Overlap buffers to avoid cutting words
                        overlap_samples = int(RATE * 1.0)  # 1 second overlap
                        if len(audio_buffer) > overlap_samples:
                            audio_buffer = audio_buffer[-overlap_samples:]
                        else:
                            audio_buffer = np.array([], dtype=np.float32)
                    
                    # Transcribe the audio in a separate thread to avoid blocking
                    transcribe_thread = threading.Thread(
                        target=self.transcribe_audio, 
                        args=(process_buffer,)
                    )
                    transcribe_thread.daemon = True
                    transcribe_thread.start()
                
            except queue.Empty:
                pass

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper model"""
        try:
            # Convert audio to the format expected by Whisper
            audio_data = audio_data.astype(np.float32)
            
            # Transcribe audio
            print("\nTranscribing chunk...")
            start_time = time.time()
            
            segments, info = model.transcribe(audio_data, beam_size=5)
            
            # Print results and save to file
            print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            # Prepare data for file output
            timestamp = datetime.now().strftime('%H:%M:%S')
            transcript_text = ""
            detailed_transcript = f"[{timestamp}] Language: {info.language} (probability: {info.language_probability:.2f})\n"
            
            for segment in segments:
                segment_text = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"
                print(segment_text)
                transcript_text += segment.text.strip() + " "
                detailed_transcript += f"  {segment_text}\n"
            
            # Print and save overall transcript
            if transcript_text:
                full_transcript = transcript_text.strip()
                print(f"\nTranscript: {full_transcript}")
                print(f"Processing time: {time.time() - start_time:.2f}s")
                
                # Save to file
                with open(TRANSCRIPT_FILE, 'a') as f:
                    f.write(f"{detailed_transcript}\n")
                    f.write(f"Complete segment: {full_transcript}\n")
                    f.write(f"Time: {time.time() - start_time:.2f}s\n")
                    f.write("-" * 80 + "\n\n")
            else:
                print("No speech detected in this segment.")
                
        except Exception as e:
            print(f"Error in transcription: {e}")
            with open(TRANSCRIPT_FILE, 'a') as f:
                f.write(f"[ERROR] {datetime.now().strftime('%H:%M:%S')}: {str(e)}\n")

    def start_recording(self):
        """Start recording audio from microphone"""
        p = pyaudio.PyAudio()
        
        # Print available input devices to help with selection
        print("Available audio input devices:")
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            if dev_info.get('maxInputChannels') > 0:  # Only input devices
                print(f"Device {i}: {dev_info.get('name')}")
        
        # Ask for device selection
        try:
            device_index = int(input("Enter input device index (or press Enter for default): ").strip() or -1)
        except ValueError:
            device_index = -1
            
        print(f"Using {'default device' if device_index == -1 else f'device {device_index}'} for audio input")
        
        # Open audio stream
        try:
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=None if device_index == -1 else device_index,
                frames_per_buffer=CHUNK,
                stream_callback=self.callback
            )
        except Exception as e:
            print(f"Error opening audio stream: {e}")
            print("Try selecting a different input device or check your microphone.")
            p.terminate()
            return
        
        # Start the processing thread
        processing_thread = threading.Thread(target=self.process_audio)
        processing_thread.daemon = True
        processing_thread.start()
        
        print("Recording started. Speak into your microphone.")
        print(f"Transcriptions are being saved to '{TRANSCRIPT_FILE}'")
        print("Press Ctrl+C to stop recording.")
        
        try:
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping recording...")
        finally:
            self.stop_event.set()
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Add final timestamp to transcript file
            with open(TRANSCRIPT_FILE, 'a') as f:
                f.write(f"\nTranscription ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            print("Recording stopped.")
            print(f"Final transcript saved to '{TRANSCRIPT_FILE}'")

if __name__ == "__main__":
    # Check if CUDA is available when device is set to "cuda"
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA not available, falling back to CPU. Processing will be slower.")
        # Change model to CPU
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    processor = AudioProcessor()
    processor.start_recording()