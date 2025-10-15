// validators/authValidator.js
const { body } = require('express-validator');

const registerValidation = [
  body('name')
    .trim()
    .notEmpty().withMessage('Name is required')
    .isLength({ max: 100 }).withMessage('Name max length is 100'),
  body('gender')
    .notEmpty().withMessage('Gender is required')
    .isIn(['male', 'female', 'other']).withMessage('Gender must be male, female or other'),
  body('age')
    .notEmpty().withMessage('Age is required')
    .isInt({ min: 0, max: 120 }).withMessage('Age must be a valid number'),
  body('phone')
    .notEmpty().withMessage('Phone is required')
    .isMobilePhone('any').withMessage('Phone must be valid'),
  body('phone2')
    .optional({ nullable: true })
    .isMobilePhone('any').withMessage('Phone2 must be valid'),
  body('email')
    .trim()
    .notEmpty().withMessage('Email is required')
    .isEmail().withMessage('Email must be valid'),
  body('password')
    .notEmpty().withMessage('Password is required')
    .isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
  body('recommend_contact_doctor')
    .optional()
    .isBoolean().withMessage('recommend_contact_doctor must be boolean')
];

const loginValidation = [
  body('emailOrPhone')
    .trim()
    .notEmpty().withMessage('Email or phone is required'),
  body('password')
    .notEmpty().withMessage('Password is required')
];

module.exports = { registerValidation, loginValidation };
