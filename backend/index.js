require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

// Setup MongoDB
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/blindhire')
  .then(() => console.log("Connected to MongoDB"))
  .catch(err => console.error("MongoDB connection error:", err));

const ResumeSchema = new mongoose.Schema({
  filename: String,
  skills_found: [String],
  experience_years: Number,
  tier1_college: Boolean,
  gender: String,
  fair_score: Number,
  biased_score: Number,
  bias_detected: Boolean,
  skill_recommendations: [String],
  createdAt: { type: Date, default: Date.now }
});

const Resume = mongoose.model('Resume', ResumeSchema);

// Setup File Upload
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir)
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname)
  }
});
const upload = multer({ storage: storage });

// API Route to analyze resume
app.post('/api/analyze', upload.single('resume'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;
  console.log("Analyzing file:", filePath);

  // Determine python executable path based on OS and whether venv exists
  const isWindows = process.platform === "win32";
  const venvPath = isWindows ? path.join(__dirname, 'venv', 'Scripts', 'python.exe') : path.join(__dirname, 'venv', 'bin', 'python');
  
  const pythonExecutable = fs.existsSync(venvPath) ? venvPath : 'python';

  const pythonProcess = spawn(pythonExecutable, [path.join(__dirname, 'analyzer.py'), filePath]);

  let dataString = '';
  let errorString = '';

  pythonProcess.stdout.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorString += data.toString();
  });

  pythonProcess.on('close', async (code) => {
    console.log(`Python process exited with code ${code}`);
    if (code !== 0) {
      console.error(errorString);
      return res.status(500).json({ error: 'Failed to analyze resume' });
    }

    try {
      const result = JSON.parse(dataString);
      if (result.error) {
        return res.status(400).json(result);
      }

      // Save to MongoDB if connected
      if (mongoose.connection.readyState === 1) {
        const newResume = new Resume({
          filename: req.file.originalname,
          ...result
        });
        await newResume.save();
      } else {
        console.warn("MongoDB not connected, skipping save.");
      }

      res.json(result);
    } catch (e) {
      console.error("Error parsing python output:", e);
      res.status(500).json({ error: 'Failed to parse analysis result' });
    } finally {
        // Optionally clean up the uploaded file
        // fs.unlinkSync(filePath);
    }
  });
});

app.get('/api/history', async (req, res) => {
    try {
        const history = await Resume.find().sort({ createdAt: -1 });
        res.json(history);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch history' });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
