import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# Load background image
# bg_image = cv2.imread("background.jpg") # Replace with your background image path

# Open webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for a mirror effect
    h, w, _ = frame.shape
    bg_image = cv2.GaussianBlur(frame, (55, 55), 0)
    # Resize background image to match frame size
    bg_resized = cv2.resize(bg_image, (w, h))

    # Convert frame to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Perform segmentation
    result = segmentation.process(frame_rgb)

    # Create mask: 255 (foreground), 0 (background)
    mask = (result.segmentation_mask > 0.5).astype(np.uint8) * 255
    
    # Convert mask to 3 channels
    mask_3d = cv2.merge([mask, mask, mask])

    # Blend original and background images
    foreground = cv2.bitwise_and(frame, mask_3d)
    background = cv2.bitwise_and(bg_resized, cv2.bitwise_not(mask_3d))
    output = cv2.add(foreground, background)

    # Display the output
    cv2.imshow("Virtual Background", output)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
