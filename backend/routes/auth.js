// routes/auth.js
const express = require('express');
const router = express.Router();
const { register, login, getMe } = require('../controllers/authController');
const { registerValidation, loginValidation } = require('../validators/authValidator');
const authMiddleware = require('../middleware/authMiddleware');

// Register
router.post('/register', registerValidation, register);

// Login
router.post('/login', loginValidation, login);

// Get current user
router.get('/me', authMiddleware, getMe);

module.exports = router;
