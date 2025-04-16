const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const fs = require("fs");
const path = require("path");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000", // Adjust to your frontend URL
    methods: ["GET", "POST"],
  },
});

const rooms = {};

io.on("connection", (socket) => {
  console.log("User connected:", socket.id);

  // Handle video chunks
  socket.on("video-chunk", (data) => {
    const { roomID, userId, chunk } = data;
  
    // Save chunk to a temporary file
    const outputPath = path.join(__dirname, `temp_${userId}_${roomID}.webm`);
    // chunk should be an ArrayBuffer; convert to Buffer for writing
    fs.appendFileSync(outputPath, Buffer.from(chunk));
  
    // Placeholder: Process video chunk for sign language recognition
    const processedText = processSignLanguage(outputPath);
  
    // Send processed text back to client
    socket.emit("sign-language-text", { text: processedText });
  });
  // Handle stream end
  socket.on("video-stream-end", (data) => {
    const { roomID, userId } = data;
    const outputPath = path.join(__dirname, `temp_${userId}_${roomID}.webm`);
    console.log(`Stream ended for user ${userId} in room ${roomID}`);
    // Clean up temporary file
    if (fs.existsSync(outputPath)) {
      fs.unlinkSync(outputPath);
    }
  });

  // Existing socket events (e.g., join room, send message, etc.)
  socket.on("join room", (data) => {
    const { roomID, user } = data;
    if (!rooms[roomID]) rooms[roomID] = [];
    rooms[roomID].push({ userId: socket.id, user });
    socket.join(roomID);
    socket.to(roomID).emit("user joined", {
      signal: null,
      callerID: socket.id,
      user,
    });
    socket.emit("all users", rooms[roomID].filter((u) => u.userId !== socket.id));
  });

  socket.on("send message", (data) => {
    socket.to(data.roomID).emit("message", data);
  });

  socket.on("sending signal", (payload) => {
    io.to(payload.userToSignal).emit("user joined", {
      signal: payload.signal,
      callerID: socket.id,
      user: payload.user,
    });
  });

  socket.on("returning signal", (payload) => {
    io.to(payload.callerID).emit("receiving returned signal", {
      signal: payload.signal,
      id: socket.id,
    });
  });

  socket.on("disconnect", () => {
    Object.keys(rooms).forEach((roomID) => {
      rooms[roomID] = rooms[roomID].filter((u) => u.userId !== socket.id);
      if (rooms[roomID].length === 0) delete rooms[roomID];
      socket.to(roomID).emit("user left", socket.id);
    });
    console.log("User disconnected:", socket.id);
  });
});

// Placeholder function for sign language processing
function processSignLanguage(videoPath) {
  // Integrate your sign language recognition model here
  // For example, use OpenCV, MediaPipe, or a pre-trained ML model
  // This is a placeholder returning dummy text
  return "Recognized sign language text";
}

server.listen(5555, () => {
  console.log("Server running on http://localhost:5555");
});