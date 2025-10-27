# Ana Designer - User Story Categorization System

A full-stack application for uploading, processing, and categorizing user stories using AI. Built with FastAPI (backend) and Next.js (frontend).

## Features

- 📁 **File Upload**: Support for Excel (.xlsx, .xls), CSV, Word (.docx), and PDF files
- 🤖 **AI-Powered Categorization**: Automatic categorization using Groq LLM
  - **DISCO Categories**: Input, Output, System, Calculation, Data
  - **Persona Identification**: Extract user personas from stories
- 📊 **Interactive Tables**: View and export categorization results
- 🎨 **Modern UI**: Consistent design theme throughout the application
- 🔐 **Authentication**: Secure login/signup system
- 📤 **Export Functionality**: Download results as CSV/Excel

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Groq API**: Fast LLM inference for categorization
- **OpenPyXL & Pandas**: Excel file processing
- **Pydantic**: Data validation
- **JWT**: Authentication

### Frontend
- **Next.js**: React framework
- **TypeScript**: Type-safe JavaScript
- **CSS Modules**: Scoped styling

## Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API Key (free from https://console.groq.com/keys)

## Installation

### 1. Clone the Repository

```bash
cd Ana-modeller
```

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_api_key_here
```

### 3. Frontend Setup

```powershell
# Navigate to frontend directory
cd ..\frontend

# Install dependencies
npm install

# Or use yarn
yarn install
```

## Getting Groq API Key

1. Visit https://console.groq.com/keys
2. Sign up for a free account
3. Create a new API key
4. Copy the key and paste it in `backend/.env`

**Note**: The application will work without the API key but will use mock data for categorization.

## Running the Application

### Start Backend Server

```powershell
# From backend directory
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn asgi:application --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/api/docs

### Start Frontend Server

```powershell
# From frontend directory (in a new terminal)
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Usage

### 1. Sign Up / Login

- Navigate to http://localhost:3000
- Create an account or login with existing credentials
- Default test accounts:
  - Email: test@gmail.com
  - Email: demo@gmail.com

### 2. Upload User Stories

- Click "📁 Upload User Stories" from the home page
- Drag & drop your Excel file or click "Choose File"
- **Excel Format**: Each user story should be in a separate sheet named "Story {number}"
- **Required Fields**:
  - Title/User Story 1
  - User Story description
  - Acceptance Criteria (optional)

### 3. View Categorization

- After upload, the system automatically processes stories
- View results in two tables:
  - **DISCO Category**: Shows Input/Output/System/Calculation/Data categorization
  - **Persona**: Shows identified user personas and their descriptions
- Export tables to Excel/CSV using the "Export" button

### 4. Excel File Format Example

Create sheets named "Story 1", "Story 2", etc. with the following structure:

```
Column A                 | Column B
------------------------|---------------------------------
Title                   | Real-Time Inventory Dashboard
User Story              | As a Supply Chain Operations Team member, I want...
Story Points            | 5
Sprint                  | Sprint 1
Assignee                | Alice J.
Acceptance Criteria     | The dashboard displays real-time inventory levels...
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `POST /api/auth/forgot-password` - Request password reset

### User Stories
- `POST /api/stories/upload` - Upload and validate file
- `POST /api/stories/upload-and-process` - Upload and immediately categorize
- `POST /api/stories/process` - Process already uploaded file

## Project Structure

```
Ana-modeller/
├── backend/
│   ├── app/
│   │   ├── models/       # Pydantic models
│   │   │   ├── user.py
│   │   │   └── story.py
│   │   ├── routers/      # API endpoints
│   │   │   ├── auth.py
│   │   │   └── stories.py
│   │   ├── services/     # Business logic
│   │   │   ├── user_service.py
│   │   │   ├── excel_parser.py
│   │   │   └── llm_service.py
│   │   ├── data/         # JSON storage
│   │   ├── auth.py       # JWT utilities
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── pages/
│   │   ├── index.tsx     # Login page
│   │   ├── signup.tsx    # Signup page
│   │   ├── home.tsx      # Dashboard
│   │   ├── upload.tsx    # File upload
│   │   └── categorize.tsx # Results page
│   ├── lib/
│   │   └── api.ts        # API client
│   ├── styles/           # CSS modules
│   └── package.json
│
└── README.md
```

## Troubleshooting

### Backend Issues

**"GROQ_API_KEY not set" warning**
- Get a free API key from https://console.groq.com/keys
- Add it to `backend/.env` file

**Import errors**
- Ensure virtual environment is activated: `.\.venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

**Port 8000 already in use**
- Change port: `uvicorn asgi:application --reload --port 8001`
- Update frontend API_BASE_URL accordingly

### Frontend Issues

**Cannot connect to backend**
- Ensure backend is running on port 8000
- Check `frontend/lib/api.ts` - API_BASE_URL should be `http://localhost:8000`

**Node modules errors**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

## LLM Categorization

The system uses Groq's **Llama 3.1 70B** model for fast and accurate categorization. The LLM:

1. Analyzes each user story
2. Identifies DISCO category (Input/Output/System/Calculation/Data)
3. Extracts user persona
4. Generates contextual descriptions

### Customizing the System Prompt

Edit `backend/app/services/llm_service.py` to customize categorization logic:

```python
self.system_prompt = """Your custom prompt here..."""
```

## Future Enhancements

- [ ] Database integration (PostgreSQL)
- [ ] Batch processing for large files
- [ ] User story editing in UI
- [ ] Advanced filtering and search
- [ ] Design and Structure steps (steps 3 & 4)
- [ ] Real-time collaboration
- [ ] Export to various formats (JSON, PDF)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Check API docs at http://localhost:8000/api/docs
- Review logs in terminal for detailed error messages

## Credits

Built with ❤️ using FastAPI, Next.js, and Groq AI
