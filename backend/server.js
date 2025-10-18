// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');
const authRoutes = require('./routes/auth');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Middlewares
app.use(cors());
app.use(express.json({ limit: '5mb' })); // parse JSON bodies

// Routes
app.use('/api/auth', authRoutes);

// Test route
app.get('/', (req, res) => res.send('Auth API is live'));

// Error Handler (keep after routes)
app.use(errorHandler);

// Start server after DB connect
const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI;

if (!MONGO_URI) {
  console.error('MONGO_URI is not defined in environment variables.');
  process.exit(1);
}

connectDB(MONGO_URI).then(() => {
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
});
