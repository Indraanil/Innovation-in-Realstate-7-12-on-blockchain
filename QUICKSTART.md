# 🚀 BharatPropChain - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Get Test ALGO (2 minutes)

1. Visit https://bank.testnet.algorand.network/
2. Enter your Algorand address
3. Click "Dispense" to get 10 test ALGO
4. Save your address and mnemonic

### Step 2: Configure Environment (1 minute)

```bash
cd BharatPropChain
copy .env.example .env
```

Edit `.env` file:
```
ADMIN_MNEMONIC=your 25 word mnemonic here
ADMIN_ADDRESS=your algorand address
```

### Step 3: Install & Run (2 minutes)

```bash
# Run setup
deployment\setup.bat

# Activate environment
venv\Scripts\activate

# Start backend
python backend/app.py
```

In a new terminal:
```bash
# Start frontend
python -m http.server 8000 --directory frontend
```

### Step 4: Access Platform

- Frontend: http://localhost:8000
- Backend API: http://localhost:5000
- API Health: http://localhost:5000/api/health

---

## 🎮 Quick Demo

### Register a Property (2 minutes)

1. Open http://localhost:8000
2. Click "Connect Wallet" → Enter any address
3. Click "Register Property"
4. Fill form with test data:
   - Name: Tech Park Tower
   - Type: Commercial
   - City: Mumbai
   - Area: 50000 sq ft
   - Value: 50000000
   - Tokens: 1000
5. Click "Register Property"
6. View AI verification results
7. Click "Tokenize on Algorand"

### View on Blockchain

1. Copy the Asset ID from success message
2. Visit https://testnet.algoexplorer.io/asset/{ASSET_ID}
3. See your property token on Algorand!

---

## 📁 Project Structure

```
BharatPropChain/
├── blockchain/          # Algorand + PyTeal contracts
├── ai/                  # OCR, fraud detection, risk scoring
├── compliance/          # KYC, DigiLocker, tax reporting
├── backend/             # Flask REST API
├── frontend/            # Web interface
├── deployment/          # Setup scripts
└── docs/                # Documentation
```

---

## 🔑 Key Files

- **README.md** - Complete documentation
- **requirements.txt** - Python dependencies
- **.env.example** - Configuration template
- **backend/app.py** - Main API server
- **frontend/index.html** - Landing page
- **docs/demo_script.md** - Demo walkthrough
- **docs/test_data.json** - Sample data

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Module not found" error
```bash
# Activate virtual environment
venv\Scripts\activate
```

### Frontend not loading
```bash
# Use simple HTTP server
python -m http.server 8000 --directory frontend
```

### Algorand connection issues
- Check internet connection
- Verify TestNet is accessible
- Try https://testnet-api.algonode.cloud directly

---

## 📞 Support

- Check [README.md](file:///c:/Users/nayak/OneDrive/Desktop/MLSC/all/BharatPropChain/README.md) for detailed docs
- Review [walkthrough.md](file:///C:/Users/nayak/.gemini/antigravity/brain/f3326605-2c44-4baf-aeae-930c06ff8631/walkthrough.md) for features
- See [demo_script.md](file:///c:/Users/nayak/OneDrive/Desktop/MLSC/all/BharatPropChain/docs/demo_script.md) for presentation

---

**Ready to tokenize India's real estate! 🇮🇳**
