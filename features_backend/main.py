from fastapi import FastAPI, UploadFile, File
from fastapi_socketio import SocketManager
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import mediapipe as mp
import tempfile
import os

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins, adjust as needed
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# Initialize SocketManager for WebSocket communication
sio = SocketManager(app=app, mount_location="/socket.io", cors_allowed_origins=["http://localhost:3000"])

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

@app.get("/")
async def root():
    return {"message": "Welcome to the Virtual Background API!"}

@sio.on("ping")
async def handle_ping(sid):
    """
    Handle ping events from the client.
    """
    print(f"Ping received from {sid}")
    await sio.emit("pong", to=sid)

@sio.on("video-stream")
async def handle_video_stream(sid, data):
    """
    Handle incoming video chunks from the client, process them, and send back the processed chunks.
    """
    print("Received video chunk")
    try:
        # Save the incoming video chunk to a temporary file
        print("Received video chunk")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_file.write(data)
        temp_file.close()

        # Open the video file
        cap = cv2.VideoCapture(temp_file.name)
        if not cap.isOpened():
            print("Failed to open video chunk")
            return
        
        # downlaod this cap
        output_path = os.path.join(os.getcwd(), "downloaded_video.mp4")
        with open(output_path, "wb") as f:
            f.write(data)
        print(f"Video chunk downloaded to {output_path}")

        # Process the video frame-by-frame
        while cap.isOpened():
            print("Processing video stream")
            ret, frame = cap.read()
            print(ret)
            print(frame)
            if not ret:
                break

            # Flip the frame for a mirror effect
            print("flipping")
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            bg_image = cv2.GaussianBlur(frame, (55, 55), 0)
            bg_resized = cv2.resize(bg_image, (w, h))

            # Convert frame to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform segmentation
            print("seg")
            result = segmentation.process(frame_rgb)

            # Create mask: 255 (foreground), 0 (background)
            mask = (result.segmentation_mask > 0.5).astype(np.uint8) * 255

            # Convert mask to 3 channels
            mask_3d = cv2.merge([mask, mask, mask])

            # Blend original and background images
            foreground = cv2.bitwise_and(frame, mask_3d)
            background = cv2.bitwise_and(bg_resized, cv2.bitwise_not(mask_3d))
            output = cv2.add(foreground, background)

            # Encode the processed frame to a video chunk
            _, buffer = cv2.imencode(".mp4", output)
            processed_chunk = buffer.tobytes()

            # downalod in cwd
            output_path = os.path.join(os.getcwd(), "output.mp4")
            with open(output_path, "wb") as f:
                f.write(processed_chunk)
            print(f"Processed chunk saved to {output_path}")

            # Send the processed chunk back to the client
            await sio.emit("processed-stream", processed_chunk, to=sid)
            print("Processed and sent video chunk")

        cap.release()

    except Exception as e:
        print(f"Error processing video stream: {e}")

    finally:
        # Clean up temporary files
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)