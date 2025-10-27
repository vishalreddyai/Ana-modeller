# Quick Setup Guide - Ana Designer

## 🚀 Quick Start (5 minutes)

### Step 1: Install Backend Dependencies
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Get Free Groq API Key
1. Visit: https://console.groq.com/keys
2. Sign up (free)
3. Copy your API key

### Step 3: Configure Backend
```powershell
# Create .env file
copy .env.example .env

# Edit .env and add your key:
# GROQ_API_KEY=gsk_your_key_here
```

### Step 4: Install Frontend Dependencies
```powershell
cd ..\frontend
npm install
```

### Step 5: Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn asgi:application --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Step 6: Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs

---

## 📝 Creating User Story Excel Files

### File Structure
Create an Excel file with sheets named: **Story 1**, **Story 2**, **Story 3**, etc.

### Sheet Format (Column A = Field, Column B = Value)

| Column A | Column B |
|----------|----------|
| Title | User Story 1: Real-Time Inventory Dashboard |
| User Story | As a Supply Chain Operations Team member, I want to have a centralized dashboard... |
| Story Points | 5 |
| Sprint | Sprint 1 |
| Assignee | Alice J. |
| Updated By | N/A |
| Created Date | 2025-07-30 |
| Revised Date | N/A |
| Acceptance Criteria | The dashboard displays real-time inventory levels... |

### Required Fields
- **Title** or **User Story 1** (at least one)
- **User Story** (description)

### Optional Fields
- Story Points, Sprint, Assignee, Dates, Acceptance Criteria

---

## 🎯 Application Flow

1. **Login** → Use test@gmail.com or create account
2. **Home** → Click "📁 Upload User Stories"
3. **Upload** → Drag & drop Excel file
4. **Processing** → AI categorizes stories automatically
5. **Categorize** → View DISCO & Persona tables
6. **Export** → Download results as CSV/Excel

---

## 🎨 Design Theme

The application uses a **consistent green theme** across all pages:
- Primary Color: `#00D26A` (Green)
- Clean, modern UI matching login/signup pages
- Multi-step wizard (Upload → Categorize → Design → Structure)
- Responsive design for desktop and mobile

---

## 🔍 What Gets Categorized

### DISCO Categories
- **Input**: Data entry, upload, import features
- **Output**: Display, export, presentation features
- **System**: Automation, background processes
- **Calculation**: Computing, analytics, processing
- **Data**: Storage, management, retrieval

### Persona Categories
Identifies who uses the feature:
- Supply Chain Operations Team
- Admin
- User
- Analyst
- Manager
- Custom personas from your stories

---

## 📊 Example Output

**User Story 1: Real-Time Inventory Dashboard**

### DISCO Category: Output
Description: Creates a centralized dashboard that displays real-time inventory levels, generates automated alerts for stock thresholds, and provides exportable reports for supply chain decision-making.

### Persona: Supply Chain Operations Team
Description: Operations team members need immediate visibility into inventory status across all locations to proactively manage stock levels and prevent stockouts or overstock situations.

---

## 🆘 Troubleshooting

### "GROQ_API_KEY not set" Warning
- Get key from https://console.groq.com/keys
- Add to `backend/.env`
- **Note**: App works without key but uses mock data

### Backend Won't Start
```powershell
# Check if virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Check for port conflicts
netstat -ano | findstr :8000
```

### Frontend Errors
```powershell
# Clear and reinstall
rm -r node_modules, package-lock.json
npm install

# Check if backend is running
curl http://localhost:8000/api/health
```

### Excel Upload Fails
- Check sheet names: "Story 1", "Story 2", etc.
- Ensure at least Title or User Story field is filled
- File size must be < 10MB
- Supported formats: .xlsx, .xls

---

## 📞 Support

- **API Docs**: http://localhost:8000/api/docs
- **Test Accounts**: test@gmail.com, demo@gmail.com
- **Logs**: Check terminals for detailed error messages

## 🎉 You're Ready!

The system is now fully functional. Upload your user stories and let AI categorize them automatically!
