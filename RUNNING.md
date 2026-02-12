# 🎯 BharatPropChain - Running Instructions

## ✅ Backend Server is Running!

The Flask backend server has been started successfully and is running on:
- **API URL**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## 🌐 How to Access the Frontend

Since you're on Windows, here are the easiest ways to access the platform:

### Option 1: Open Directly in Browser (Recommended)
1. Open your web browser (Chrome, Edge, or Firefox)
2. Navigate to this file path:
   ```
   file:///c:/Users/nayak/OneDrive/Desktop/MLSC/all/BharatPropChain/frontend/index.html
   ```
3. Or simply double-click on `index.html` in the frontend folder

### Option 2: Use Python HTTP Server
Open a **NEW** terminal window and run:
```bash
cd c:\Users\nayak\OneDrive\Desktop\MLSC\all\BharatPropChain
python -m http.server 8000 --directory frontend
```
Then open: http://localhost:8000

## 🎮 Quick Demo Steps

1. **Open the Frontend** (using either option above)

2. **Connect Wallet**
   - Click "Connect Wallet" button
   - Enter any demo address (or press OK for auto-generated)

3. **Register a Property**
   - Click "Register Property" in navigation
   - Fill in the form with test data:
     - Name: `Tech Park Tower`
     - Type: `Commercial`
     - City: `Mumbai`
     - Location: `Bandra Kurla Complex, Mumbai`
     - Area: `50000` sq ft
     - Value: `50000000` (₹5 Crores)
     - Tokens: `1000`
   - Click "Register Property"

4. **View AI Verification**
   - The system will show:
     - Risk Score
     - Predicted Valuation
     - Token Value

5. **Tokenize on Algorand**
   - Click "Tokenize on Algorand" button
   - View the success message with Asset ID

6. **Explore Marketplace**
   - Navigate to "Marketplace"
   - See all tokenized properties

## 📊 Test the API Directly

You can also test the backend API directly:

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Platform Analytics
```bash
curl http://localhost:5000/api/analytics/platform
```

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"wallet_address\":\"DEMO123\",\"name\":\"Test User\",\"email\":\"test@example.com\"}"
```

## 🔍 What's Running

- ✅ **Backend API**: Flask server on port 5000
- ✅ **Dependencies**: All Python packages installed
- ✅ **Storage**: Directories created for uploads
- ⏳ **Frontend**: Needs to be opened in browser (see options above)

## 📁 Project Structure

```
BharatPropChain/
├── backend/app.py          ← Currently running!
├── frontend/index.html     ← Open this in browser
├── blockchain/             ← Algorand integration
├── ai/                     ← AI verification modules
├── compliance/             ← KYC and legal compliance
└── docs/                   ← Documentation
```

## 🆘 Troubleshooting

### Backend Not Responding?
Check if it's still running. You should see Flask debug output in the terminal.

### Frontend Not Loading?
Make sure you're opening the file with the full path or using the HTTP server.

### API Errors?
The backend is using in-memory storage, so data resets when you restart the server.

## 🎯 Next Steps

1. Open the frontend in your browser
2. Try the demo workflow above
3. Check out the comprehensive docs:
   - `README.md` - Full documentation
   - `docs/demo_script.md` - Presentation guide
   - `docs/test_data.json` - Sample data

---

**Your BharatPropChain platform is ready! 🚀**
