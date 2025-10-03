from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
import jwt
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
CORS(app, supports_credentials=True)

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# Email validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Generate JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

# Verify JWT token
def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Check if user exists
def user_exists(user_id, email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ? OR email = ?', (user_id, email))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Register new user
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validation
        if not user_id or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        if len(user_id) < 3:
            return jsonify({'error': 'User ID must be at least 3 characters long'}), 400

        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        # Check if user already exists
        if user_exists(user_id, email):
            return jsonify({'error': 'User ID or email already exists'}), 409

        # Hash password and save user
        password_hash = generate_password_hash(password)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (user_id, email, password_hash) VALUES (?, ?, ?)',
            (user_id, email, password_hash)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully'}), 201

    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

# Login user
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '')

        if not user_id or not password:
            return jsonify({'error': 'User ID and password are required'}), 400

        # Find user by user_id or email
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_id, password_hash FROM users WHERE user_id = ? OR email = ?',
            (user_id, user_id)
        )
        user = cursor.fetchone()
        conn.close()

        if not user or not check_password_hash(user[1], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate token
        token = generate_token(user[0])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user_id': user[0]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

# Verify token
@app.route('/api/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        return jsonify({'user_id': user_id}), 200

    except Exception as e:
        return jsonify({'error': 'Token verification failed'}), 500

# Forgot password
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if email exists
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'Email not found'}), 404

        # In a real application, you would send an email here
        # For now, we'll just return a success message
        return jsonify({'message': 'Password reset instructions sent to your email'}), 200

    except Exception as e:
        return jsonify({'error': 'Password reset request failed'}), 500

# Get user profile
@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Token is required'}), 401

        token = token.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, email, created_at FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user_id': user[0],
            'email': user[1],
            'created_at': user[2]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)