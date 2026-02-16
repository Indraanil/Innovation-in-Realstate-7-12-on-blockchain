# BharatPropChain API Reference

This document provides the technical specification for the BharatPropChain backend API.

## Base URL
`http://localhost:5000`

## Authentication
Most endpoints require a JWT token in the `Authorization` header:
`Authorization: Bearer <your_access_token>`

### [POST] /api/auth/register
Register a new wallet user.
- **Request Body**: `{ "wallet_address": "...", "name": "...", "email": "..." }`
- **Response**: `{ "success": true, "access_token": "..." }`

### [POST] /api/auth/login
Login an existing user.
- **Request Body**: `{ "wallet_address": "..." }`
- **Response**: `{ "success": true, "access_token": "...", "user": {...} }`

---

## KYC & Trust Protocol

### [GET] /api/kyc/status
Retrieve current user's KYC verification status.
- **Header**: Required `Authorization`
- **Response**: `{ "status": "verified|pending|none", "verification_steps": {...} }`

### [POST] /api/kyc/verify
Submit KYC data for verification.
- **Request Body**: `{ "aadhaar_number": "...", "pan_number": "...", ... }`
- **Response**: `{ "success": true, "message": "Verification successful" }`

---

## Property & Marketplace

### [GET] /api/properties
Fetch all institutional assets.
- **Response**: `{ "properties": [...] }`

### [POST] /api/properties/register
Register a new asset. **Requires KYC 'verified' status.**
- **Request Body**: `{ "name": "...", "total_value": 0, "total_tokens": 1000, ... }`
- **Response**: `{ "success": true, "property_id": "..." }`

### [POST] /api/properties/<property_id>/tokenize
Mint the asset on the Algorand blockchain.
- **Response**: `{ "success": true, "asset_id": 123456, "explorer_url": "..." }`

---

## Trading

### [POST] /api/trade/buy
Buy fractional tokens. Integrates with Payment Gateway.
- **Request Body**: `{ "property_id": "...", "token_amount": 10, "payment_ref": "...", "order_id": "..." }`
- **Response**: `{ "success": true, "transaction": {...} }`

### [POST] /api/trade/sell
Sell fractional tokens (Payout).
- **Request Body**: `{ "property_id": "...", "token_amount": 5, "payment_ref": "...", "order_id": "..." }`
- **Response**: `{ "success": true, "payout": {...} }`
