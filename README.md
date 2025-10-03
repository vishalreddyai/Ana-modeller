# Full-Stack Authentication Website

A production-ready full-stack web application with React/Next.js frontend and Python Flask backend, featuring complete user authentication system.

## Features

- **User Authentication**: Login, Signup, Forgot Password
- **Frontend**: React with Next.js, TypeScript, modern UI design
- **Backend**: Python Flask with SQLite database
- **Security**: JWT tokens, password hashing, input validation
- **Responsive Design**: Mobile-friendly interface
- **Production Ready**: Proper error handling, validation, and security measures

## Project Structure

```
├── backend/
│   ├── app.py              # Flask application with authentication API
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── pages/              # Next.js pages
│   │   ├── index.tsx       # Homepage (protected)
│   │   ├── login.tsx       # Login page
│   │   ├── signup.tsx      # Signup page
│   │   ├── forgot-password.tsx # Forgot password page
│   │   └── _app.tsx        # App wrapper
│   ├── lib/
│   │   └── auth.ts         # Authentication service
│   ├── styles/
│   │   └── globals.css     # Global styles
│   ├── package.json        # Node.js dependencies
│   ├── next.config.js      # Next.js configuration
│   └── tsconfig.json       # TypeScript configuration
└── README.md               # This file
```

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication Endpoints

- `POST /api/register` - Register a new user
- `POST /api/login` - Login user
- `POST /api/verify` - Verify JWT token
- `POST /api/forgot-password` - Request password reset
- `GET /api/profile` - Get user profile (requires authentication)

### Request/Response Examples

#### Register User
```json
POST /api/register
{
  "user_id": "john_doe",
  "email": "john@example.com",
  "password": "password123"
}
```

#### Login User
```json
POST /api/login
{
  "user_id": "john_doe",
  "password": "password123"
}
```

## Usage

1. **Sign Up**: Visit `/signup` to create a new account
2. **Login**: Visit `/login` to sign in with your credentials
3. **Homepage**: After successful login, you'll be redirected to the homepage
4. **Forgot Password**: Visit `/forgot-password` to request password reset
5. **Logout**: Click the "Sign Out" button on the homepage

## Security Features

- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Configured for secure cross-origin requests
- **Unique User IDs**: Prevents duplicate user IDs and emails
- **Token Expiration**: JWT tokens expire after 24 hours

## Database

The application uses SQLite database (`users.db`) with the following schema:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

## Development

### Running in Development Mode

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Start the frontend server (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

### Building for Production

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

## Environment Variables

For production deployment, consider setting these environment variables:

- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `DATABASE_URL`: Database connection string

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change the port in `app.py` (backend) or `package.json` (frontend)
2. **CORS Errors**: Ensure the backend is running on the correct port
3. **Database Issues**: Delete `users.db` to reset the database

### Logs

- Backend logs are displayed in the terminal where `python app.py` is running
- Frontend logs are available in the browser's developer console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.