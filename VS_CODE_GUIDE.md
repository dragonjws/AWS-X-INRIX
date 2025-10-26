# VS Code Setup Guide

## Quick Start - Running in VS Code

### Method 1: Using Integrated Terminal (Easiest)

1. **Open VS Code in this workspace**
   - File → Open Folder → Select `ratemyprof_fetcher`

2. **Open Two Terminals**
   - Press `Ctrl+Shift+` ` (backtick) or Terminal → New Terminal (twice)

3. **Terminal 1 - Backend**
   ```bash
   cd backend
   python api.py
   ```
   You should see: `🚀 Flask Server Starting... Running on http://127.0.0.1:5001`

4. **Terminal 2 - Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   You should see: `➜ Local: http://localhost:5173/`

5. **Open Browser**
   - Go to `http://localhost:5173` (or the port shown)

---

### Method 2: Using Tasks (Recommended)

1. Press `Ctrl+Shift+P` (Cmd+Shift+P on Mac)
2. Type "Tasks: Run Task"
3. Select "Start Full Stack"
4. This runs both backend and frontend automatically!

---

### Method 3: Using the Debugger

1. Press `F5` or click Debug → Start Debugging
2. Select "Backend API"
3. The backend will start with debugging enabled
4. Then manually run frontend in a terminal: `cd frontend && npm run dev`

---

## Current Setup

✅ **Backend API**: Running on `http://localhost:5001`  
✅ **Frontend**: Running on `http://localhost:5173` or `http://localhost:3001`

## Troubleshooting

### Port Already in Use?
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Backend Won't Start?
- Check your `.env` file in `backend/` has real AWS credentials
- Make sure all dependencies are installed: `pip install -r backend/requirements.txt`

### Frontend Won't Start?
- Install dependencies: `cd frontend && npm install`

---

## File Structure

```
ratemyprof_fetcher/
├── .vscode/           ← VS Code config (just added!)
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── backend/           ← Python Flask API
│   ├── api.py
│   ├── converse.py
│   └── ...
├── frontend/          ← React app
│   ├── src/
│   └── ...
└── README.md
```

---

## Next Steps

1. Make sure your AWS credentials are in `backend/.env`
2. Run the full stack using any method above
3. Start building your features! 🚀

