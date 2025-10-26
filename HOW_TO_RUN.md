# How to Run Your Full Stack Application

## Quick Start

### Both servers are starting! Here's what's running:

✅ **Frontend**: http://localhost:3001 (or whatever port Vite shows)  
✅ **Backend API**: http://localhost:5001

---

## How to Run (From Scratch)

### Terminal 1 - Backend API Server
```bash
cd backend
python api.py
```

You should see:
```
🚀 Flask Server Starting...
 * Serving Flask app 'api'
 * Running on http://127.0.0.1:5001
```

### Terminal 2 - Frontend React App
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v6.3.5  ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

---

## Open Your App

**Go to:** `http://localhost:3001` (or the port shown in terminal)

---

## What You Can Do Now

1. **Fill out the form**:
   - Add course names
   - Select quarter (Fall, Winter, Spring)
   - Choose days of week
   - Pick time preference (Morning, Afternoon, Evening)
   - Describe professor preferences

2. **Click "Generate Schedule"**
   - Uses Claude AI to generate multiple schedule options
   - Shows pros/cons for each schedule
   - Displays course details with professors

3. **Select a schedule**
   - Click on any schedule option to highlight it
   - Selected schedule will be highlighted in red

4. **Click "Add to Google Calendar"**
   - Adds selected schedule to your Google Calendar
   - Creates recurring events with dates/times
   - Shows success message when done

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5001 (backend)
lsof -ti:5001 | xargs kill -9

# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9
```

### Backend Won't Start
- Check your `backend/.env` file has real AWS credentials:
  ```bash
  AWS_ACCESS_KEY_ID=your_actual_key
  AWS_SECRET_ACCESS_KEY=your_actual_secret
  ```

### Frontend Won't Start
```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
ratemyprof_fetcher/
├── backend/           # Python Flask API
│   ├── api.py        # Main API server
│   ├── converse.py    # Original CLI script
│   ├── gcal.py       # Google Calendar integration
│   ├── ratemyprof_info.py  # RateMyProfessor API
│   └── .env          # AWS credentials
│
└── frontend/          # React TypeScript app
    └── src/
        └── App.tsx   # Main UI component
```

---

Enjoy your course scheduling system! 🎉

