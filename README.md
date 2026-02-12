# 🏛️ BharatPropChain - Property Tokenization Platform

> India's first blockchain-powered property tokenization platform built on Algorand

[![Algorand](https://img.shields.io/badge/Blockchain-Algorand-blue)](https://algorand.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🎯 Problem Statement

Real estate investment in India faces multiple challenges:
- **High Entry Barriers**: Properties worth crores are inaccessible to average investors
- **Liquidity Issues**: Selling property takes months, limiting investment flexibility
- **Fraud & Verification**: Document forgery and title disputes are common
- **Opacity**: Lack of transparent pricing and ownership records
- **Manual Processes**: Rental income distribution and governance are inefficient

## 💡 Solution

BharatPropChain democratizes real estate investment through:

1. **Fractional Ownership**: Convert properties into digital tokens, enabling investment from ₹10,000
2. **Blockchain Security**: Immutable records on Algorand for transparency and trust
3. **AI Verification**: ML-powered document authentication and fraud detection
4. **Automated Management**: Smart contracts for income distribution and governance
5. **Legal Compliance**: KYC/AML, DigiLocker integration, and government registry linking

## ✨ Key Features

### 🔗 Blockchain Layer (Algorand)
- Property tokenization using Algorand Standard Assets (ASA)
- PyTeal smart contracts for automated operations
- Transparent, immutable transaction records
- Integration with Pera Wallet

### 🤖 AI Verification
- **OCR Processing**: Extract text from property documents (English + Hindi)
- **Fraud Detection**: ML models to identify fake/forged documents
- **Risk Scoring**: Multi-factor risk assessment (location, legal, market, financial)
- **Valuation Model**: AI-powered property price prediction

### ⚖️ Legal Compliance
- KYC/AML verification (Aadhaar + PAN)
- DigiLocker integration for government documents
- Government land registry linking
- Tax reporting (capital gains, rental income)
- Audit trail generation

### 💼 Business Features
- Tokenization fees (2.5% of property value)
- Transaction fees (1% per trade)
- Subscription tiers (Free, Premium, Enterprise)
- Revenue analytics dashboard

## 🏗️ Architecture

```
BharatPropChain/
├── blockchain/          # Algorand integration & PyTeal contracts
│   ├── algorand_client.py
│   └── contracts/
│       ├── property_token.py
│       ├── income_distribution.py
│       └── governance.py
├── ai/                  # AI/ML modules
│   ├── ocr_processor.py
│   ├── fraud_detector.py
│   ├── risk_scorer.py
│   └── valuation_model.py
├── compliance/          # Legal & compliance
│   ├── kyc_verifier.py
│   ├── digilocker_integration.py
│   └── tax_reporter.py
├── backend/             # Flask REST API
│   ├── app.py
│   ├── storage.py
│   └── business/
│       └── fee_calculator.py
├── frontend/            # Web interface
│   ├── index.html
│   ├── marketplace.html
│   ├── register-property.html
│   ├── styles.css
│   └── app.js
└── deployment/          # Setup & deployment scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+ (optional, for advanced frontend)
- Algorand TestNet account ([Get test ALGO](https://bank.testnet.algorand.network/))

### Installation

1. **Clone the repository**
```bash
cd BharatPropChain
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
copy .env.example .env
# Edit .env and add your Algorand account mnemonic
```

5. **Run the backend**
```bash
python backend/app.py
```

6. **Open frontend**
```bash
# Open frontend/index.html in your browser
# Or use a simple HTTP server:
python -m http.server 8000 --directory frontend
```

Visit `http://localhost:8000` to access the platform!

## 📖 Usage Guide

### For Property Owners

1. **Connect Wallet**: Click "Connect Wallet" and enter your Algorand address
2. **Complete KYC**: Verify your identity with Aadhaar and PAN
3. **Register Property**: Upload property details and documents
4. **AI Verification**: System automatically verifies documents and calculates risk
5. **Tokenize**: Mint property tokens on Algorand blockchain
6. **Manage**: Track ownership, distribute income, create governance proposals

### For Investors

1. **Browse Marketplace**: Explore tokenized properties
2. **View Details**: Check AI verification, risk scores, and valuations
3. **Buy Tokens**: Purchase fractional ownership
4. **Earn Income**: Receive automated rental income distributions
5. **Vote**: Participate in property governance decisions

## 🔐 Security & Compliance

### Blockchain Security
- All property records stored on Algorand blockchain
- Cryptographic hashing of documents
- Multi-signature support for high-value transactions

### Privacy Protection
- Document encryption using AES-256
- Off-chain storage with on-chain hashes
- GDPR-compliant data handling

### Legal Framework
- **Disclaimer**: Blockchain records serve as verification layers, NOT legal replacements
- Property ownership requires proper legal documentation
- Platform facilitates but doesn't replace legal processes

## 🇮🇳 India-Specific Features

- **Multi-language Support**: English + Hindi OCR
- **Aadhaar Integration**: Mock KYC verification
- **PAN Verification**: Tax compliance
- **DigiLocker**: Government document verification
- **Land Registry Linking**: Integration with state registries
- **Indian Tax Reporting**: Capital gains and rental income reports

## 📊 API Documentation

### Authentication
```
POST /api/auth/register
POST /api/auth/login
```

### KYC
```
POST /api/kyc/verify
GET /api/kyc/status
```

### Properties
```
POST /api/properties/register
POST /api/properties/{id}/upload-document
POST /api/properties/{id}/verify
POST /api/properties/{id}/tokenize
GET /api/properties
GET /api/properties/{id}
```

### Trading
```
POST /api/trade/buy
```

### Analytics
```
GET /api/analytics/platform
GET /api/user/dashboard
```

## 🧪 Testing

### Run Backend Tests
```bash
python tests/test_api.py
python tests/test_ai.py
python tests/test_contracts.py
```

### Test on Algorand TestNet

1. Get test ALGO: https://bank.testnet.algorand.network/
2. Deploy contracts: `python deployment/deploy_contracts.py`
3. View on AlgoExplorer: https://testnet.algoexplorer.io

## 🎤 Demo Script (3-4 minutes)

**[Slide 1: Problem]**
"Real estate investment in India is broken. Only the wealthy can invest, fraud is rampant, and processes are manual."

**[Slide 2: Solution]**
"BharatPropChain tokenizes properties on Algorand blockchain, enabling fractional ownership from ₹10,000."

**[Live Demo]**
1. Show marketplace with tokenized properties
2. Register new property with document upload
3. Demonstrate AI verification (OCR + fraud detection)
4. Mint tokens on Algorand TestNet
5. Show transaction on AlgoExplorer
6. Display automated income distribution

**[Slide 3: Impact]**
"We're democratizing real estate for 1.4 billion Indians while ensuring legal compliance and security."

## 💰 Business Model

### Revenue Streams
1. **Tokenization Fees**: 2.5% of property value
2. **Transaction Fees**: 1% per trade
3. **Subscription Plans**:
   - Free: 1 property, basic features
   - Premium (₹999/month): Unlimited properties, priority support
   - Enterprise (Custom): White-label solution

### Market Opportunity
- India real estate market: $200B+
- Target: 1% tokenization in 5 years = $2B market
- Revenue potential: ₹100Cr+ annually

## 🛣️ Roadmap

### Phase 1 (Hackathon) ✅
- Core tokenization platform
- AI verification
- Algorand TestNet deployment

### Phase 2 (Q2 2024)
- MainNet deployment
- Real DigiLocker/Aadhaar integration
- Mobile app (iOS + Android)

### Phase 3 (Q3 2024)
- Multi-state land registry integration
- Institutional investor onboarding
- Secondary market with AMM

### Phase 4 (Q4 2024)
- International expansion
- DeFi integrations (lending, staking)
- DAO governance

## 🤝 Team & Credits

Built for hackathon demonstration by passionate blockchain and AI enthusiasts.

## ⚠️ Important Disclaimers

1. **Legal Status**: This is a demonstration platform. Blockchain records do NOT replace legal property ownership documents.
2. **Mock Integrations**: DigiLocker, Aadhaar, and PAN integrations are simulated. Production requires official partnerships.
3. **TestNet Only**: Currently deployed on Algorand TestNet. Not for real transactions.
4. **Regulatory Compliance**: Full deployment requires approval from SEBI, RBI, and state authorities.

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- **AlgoExplorer TestNet**: https://testnet.algoexplorer.io
- **Algorand Dispenser**: https://bank.testnet.algorand.network/
- **Pera Wallet**: https://perawallet.app/

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Email: support@bharatpropchain.com (demo)

---

**Built with ❤️ for India's blockchain future**
