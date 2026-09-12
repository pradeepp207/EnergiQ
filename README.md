# GridMind AI ⚡
### Autonomous Energy Orchestration Platform

---

## What's included

```
gridmind/
├── backend/
│   ├── server.py          ← Python Flask API (AI engine + simulator)
│   └── requirements.txt   ← Python dependencies
├── frontend/
│   ├── index.html         ← Main dashboard
│   ├── controller.html    ← Remote control panel
│   └── manual.html        ← Manual meter input
└── README.md
```

---

## Step 1 — Install Python (if not already)

1. Go to https://python.org/downloads
2. Download Python 3.11 or newer
3. During install, tick **"Add Python to PATH"**
4. Open terminal and check: `python --version`

---

## Step 2 — Install VS Code

1. Go to https://code.visualstudio.com
2. Download and install
3. Open VS Code → File → Open Folder → select the `gridmind` folder

---

## Step 3 — Set up the Backend

Open a terminal in VS Code (View → Terminal) and run:

```bash
cd backend
pip install -r requirements.txt
python server.py
```

You should see:
```
 * Running on http://127.0.0.1:8000
 * Debug mode: on
```

Leave this terminal running. The backend is now live.

---

## Step 4 — Open the Frontend

Open a NEW terminal (click the + button in the terminal panel):

```bash
cd frontend
python -m http.server 3000
```

Then open your browser and go to:
```
http://localhost:3000/index.html
```

---

## Step 5 — You should see

- ✅ Live energy dashboard updating every 2 seconds
- ✅ AI decisions panel showing recommendations
- ✅ 6-hour solar forecast chart
- ✅ Load toggles working (EV, pump)
- ✅ Remote control at /controller.html
- ✅ Manual input at /manual.html

---

## Deploying online (Free)

### Option A: Deploy frontend to Vercel (recommended)

1. Go to https://vercel.com and create a free account
2. Install Vercel CLI: `npm install -g vercel`
3. In the `frontend` folder, run: `vercel`
4. Follow the prompts — your site goes live in 60 seconds
5. You get a URL like: `https://gridmind-ai.vercel.app`

### Option B: Deploy backend to Railway

1. Go to https://railway.app and create a free account
2. Click "New Project" → "Deploy from GitHub"
3. Push your code to GitHub first (see below)
4. Select the `backend` folder as root
5. Railway auto-detects Python and deploys
6. You get a URL like: `https://gridmind-backend.railway.app`
7. Update the `API` variable in all 3 HTML files to this URL

### Pushing to GitHub

```bash
git init
git add .
git commit -m "GridMind AI initial commit"
# Create repo on github.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/gridmind.git
git push -u origin main
```

---

## Common errors

| Error | Fix |
|-------|-----|
| `pip not found` | Reinstall Python, tick "Add to PATH" |
| `ModuleNotFoundError: flask` | Run `pip install flask flask-cors` |
| `Address already in use` | Change port: `python server.py` → edit server.py port 8000→8001 |
| Dashboard shows "Backend offline" | Make sure `python server.py` is still running |
| CORS error in browser | The flask-cors package handles this — make sure it's installed |