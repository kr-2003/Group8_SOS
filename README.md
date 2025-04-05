# EquaSpace

EquaSpace is an innovative and comprehensive video conferencing platform designed to revolutionize remote communication. Unlike traditional video conferencing tools, EquaSpace goes beyond basic functionality to offer a truly inclusive and feature-rich experience. At the heart of our mission is the commitment to making virtual communication accessible to everyone, especially people with special needs. We recognize the challenges faced by individuals with hearing or visual impairments and have designed EquaSpace to bridge those gaps. It provides real-time video and audio conferencing, intelligent chat, advanced meeting management, accessibility features, and high-end security measures, ensuring that no one is left behind in the digital age. The platform includes sign language recognition, AI-powered transcription, and haptic feedback notifications, enabling seamless interaction for users with disabilities. By prioritizing inclusivity, EquaSpace aims to redefine how people connect and collaborate in an increasingly remote world.

## Tech Stack

- React.js - Frontend framework
- Socket.io - Real-time communication
- Tailwind CSS - Styling framework
- Bootstrap - UI components
- Node.js & Express.js - Backend support
- WebRTC - Video and audio streaming
- Firebase

## Installation & Setup

### Prerequisites

- Node.js v10+ installed on your system
- Python pre-installed on your system

### Modules
1. SOS_Frontend - Contains code for frontend part of the application
2. SOS_Backend - Contains code for backend part of the application

### Steps to Run the Project

1. Clone the repository:
   ```sh
   git clone https://github.com/kr-2003/Group8_SOS.git
   ```
2. Navigate to the project directory:
   ```sh
   cd Group8_SOS
   ```
3. Install dependencies:
   ```sh
   npm install
   ```
4. Start the development server:
   ```sh
   npm start
   ```
5. Open `http://localhost:3000` in your browser.

### Steps to run the sign translation application

1. Navigate to application directory:
   ```sh
   cd ./SOS_Backend/scripts/sign_lang
   ```
2. Install the requirements:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python prediction.py
   ```

### Sign Language Translation Feature

EquaSpace includes a cutting-edge sign language translation feature located in `./SOS_Backend/scripts/sign_lang`. This feature leverages a machine learning model to process live streaming video input and translate it into corresponding sign language. The system is designed to facilitate seamless communication for individuals with hearing impairments by providing real-time sign language interpretation. This functionality is a significant step toward making virtual communication more inclusive and accessible for everyone.

### Environment Variables Setup

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in the required values:
     - `GROQ_API_KEY` (Get it from [Groq Playground](https://console.groq.com/playground) under API Keys)

This API key is used for generating summaries of images. The related code is implemented in `./features/image_summary.py`.

## Deployment Links

- [Frontend Deployment](https://group-8-sos-frontend-drab.vercel.app/)
- [Backend Deployment](https://group8-sos-backend.onrender.com/)

