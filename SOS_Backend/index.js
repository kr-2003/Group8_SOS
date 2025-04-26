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

const rooms = {}; // Format: { roomID: { users: [{ userId, user }], transcripts: [{ userId, text, timestamp }] } }

io.on("connection", (socket) => {
  console.log("User connected:", socket.id);

  // Handle video chunks
  socket.on("video-chunk", (data) => {
    const { roomID, userId, chunk } = data;

    // Save chunk to a temporary file
    const outputPath = path.join(__dirname, `temp_${userId}_${roomID}.webm`);
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

  // Handle screen share stream
  socket.on("screen-share-start", (data) => {
    const { roomID, userId, screenStream } = data;

    // Send screen stream to all users in the room except the one sharing
    socket.to(roomID).emit("screen-share-stream", {
      screenStream,
      userId,
    });
  });

  // Handle screen share end
  socket.on("screen-share-end", (data) => {
    const { roomID, userId } = data;
    socket.to(roomID).emit("screen-share-ended", { userId });
  });


  socket.on("screen-share-start", (data) => {
    const { roomID, userId, screenStream } = data;

    // Send screen stream to all users in the room except the one sharing
    socket.to(roomID).emit("screen-share-stream", {
      screenStream,
      userId,
    });
  });

  // Handle screen share end
  socket.on("screen-share-end", (data) => {
    const { roomID, userId } = data;
    socket.to(roomID).emit("screen-share-ended", { userId });
  });

  // Handle transcript
  socket.on("transcript", (data) => {
    const { roomID, userId, text } = data;
    if (!rooms[roomID]) {
      rooms[roomID] = { users: [], transcripts: [] };
    }
    // Append transcript with timestamp
    const transcriptEntry = {
      userId,
      text,
      timestamp: new Date().toISOString(),
      username: data.username,
    };
    rooms[roomID].transcripts.push(transcriptEntry);
    console.log(`Transcript received for room ${roomID}:`, transcriptEntry);

    // Broadcast transcripts to all users in the room (including sender)
    io.to(roomID).emit("room-transcripts", {
      roomID,
      transcripts: rooms[roomID].transcripts,
    });
  });

  // Handle join room
  socket.on("join room", (data) => {
    const { roomID, user } = data;
    if (!rooms[roomID]) {
      rooms[roomID] = { users: [], transcripts: [] };
    }
    rooms[roomID].users.push({ userId: socket.id, user });
    socket.join(roomID);
    socket.to(roomID).emit("user joined", {
      signal: null,
      callerID: socket.id,
      user,
    });
    socket.emit("all users", rooms[roomID].users.filter((u) => u.userId !== socket.id));
    // Send existing transcripts to the joining user
    socket.emit("room-transcripts", {
      roomID,
      transcripts: rooms[roomID].transcripts,
    });
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
      rooms[roomID].users = rooms[roomID].users.filter((u) => u.userId !== socket.id);
      if (rooms[roomID].users.length === 0) {
        console.log(`Room ${roomID} is empty, deleting...`);
        delete rooms[roomID];
      } else {
        socket.to(roomID).emit("user left", socket.id);
      }
    });
    console.log("User disconnected:", socket.id);
  });
});

// Placeholder function for sign language processing
function processSignLanguage(videoPath) {
  // Integrate your sign language recognition model here
  // For example, use OpenCV, MediaPipe, or a pre-trained ML model
  return "Recognized sign language text";
}

server.listen(5555, () => {
  console.log("Server running on http://localhost:5555");
});