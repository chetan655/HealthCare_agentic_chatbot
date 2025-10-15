// controllers/authController.js
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { validationResult } = require('express-validator');
const User = require('../models/User');

const createToken = (user, jwtSecret, expiresIn) => {
  return jwt.sign({ id: user._id }, jwtSecret, { expiresIn });
};

// POST /api/auth/register
const register = async (req, res, next) => {
  try {
    // validation
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      name,
      gender,
      age,
      phone,
      phone2,
      email,
      password,
      recommend_contact_doctor
    } = req.body;

    // Check if email or phone already exist
    const existingEmail = await User.findOne({ email: email.toLowerCase() });
    if (existingEmail) {
      return res.status(400).json({ message: 'Email already registered' });
    }
    const existingPhone = await User.findOne({ phone });
    if (existingPhone) {
      return res.status(400).json({ message: 'Phone number already registered' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashed = await bcrypt.hash(password, salt);

    const user = new User({
      name,
      gender,
      age,
      phone,
      phone2,
      email: email.toLowerCase(),
      password: hashed,
      recommend_contact_doctor: !!recommend_contact_doctor
    });

    await user.save();

    const token = createToken(user, process.env.JWT_SECRET, process.env.JWT_EXPIRES_IN || '7d');

    return res.status(201).json({
      message: 'User registered successfully',
      user: user, // toJSON removes password
      token
    });
  } catch (err) {
    next(err);
  }
};

// POST /api/auth/login
// Accepts { emailOrPhone, password }
const login = async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { emailOrPhone, password } = req.body;

    // Determine whether it looks like an email
    let user = null;
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailOrPhone)) {
      user = await User.findOne({ email: emailOrPhone.toLowerCase() });
    } else {
      user = await User.findOne({ phone: emailOrPhone });
    }

    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    const token = createToken(user, process.env.JWT_SECRET, process.env.JWT_EXPIRES_IN || '7d');

    return res.json({
      message: 'Logged in successfully',
      user: user,
      token
    });
  } catch (err) {
    next(err);
  }
};

// GET /api/auth/me
const getMe = async (req, res, next) => {
  try {
    // authMiddleware sets req.userId
    const user = await User.findById(req.userId).select('-password');
    if (!user) return res.status(404).json({ message: 'User not found' });
    return res.json({ user });
  } catch (err) {
    next(err);
  }
};

module.exports = { register, login, getMe };
