// BharatPropChain Frontend JavaScript
// Handles wallet connection, API calls, and UI interactions

const API_BASE_URL = 'http://localhost:5000';
let currentUser = null;
let accessToken = null;
let peraWallet = null;

// ============= Wallet Connection =============

// Initialize Pera Wallet
function initializePeraWallet() {
    if (typeof PeraWalletConnect !== 'undefined') {
        peraWallet = new PeraWalletConnect({
            chainId: 416002 // Algorand TestNet
        });

        // Reconnect to session if exists
        peraWallet.reconnectSession().then((accounts) => {
            if (accounts.length) {
                handleWalletConnection(accounts);
            }
        }).catch(e => {
            console.log('No existing session');
        });
    }
}

async function connectWallet() {
    try {
        // Check if Pera Wallet SDK is loaded
        if (typeof PeraWalletConnect === 'undefined') {
            const useDemoMode = confirm(
                'Pera Wallet SDK not loaded. Would you like to:\n\n' +
                'OK = Use Demo Mode (simulated wallet)\n' +
                'Cancel = Install Pera Wallet'
            );

            if (!useDemoMode) {
                window.open('https://perawallet.app/', '_blank');
                return;
            }

            // Demo mode fallback
            return connectDemoWallet();
        }

        // Initialize Pera Wallet if not already done
        if (!peraWallet) {
            initializePeraWallet();
        }

        // Connect to Pera Wallet
        const accounts = await peraWallet.connect();
        await handleWalletConnection(accounts);

    } catch (error) {
        console.error('Wallet connection error:', error);

        // If user rejects, offer demo mode
        if (error.message && error.message.includes('rejected')) {
            const useDemoMode = confirm('Connection cancelled. Would you like to use Demo Mode instead?');
            if (useDemoMode) {
                return connectDemoWallet();
            }
        } else {
            alert('Failed to connect wallet: ' + error.message);
        }
    }
}

async function connectDemoWallet() {
    try {
        const walletAddress = prompt('Enter your Algorand wallet address (or press OK for demo):');
        const demoAddress = walletAddress || 'DEMO' + Math.random().toString(36).substring(7).toUpperCase();

        await handleWalletConnection([demoAddress], true);
    } catch (error) {
        console.error('Demo wallet error:', error);
        alert('Failed to connect demo wallet');
    }
}

async function handleWalletConnection(accounts, isDemoMode = false) {
    try {
        const walletAddress = accounts[0];

        // Register or login user
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wallet_address: walletAddress,
                name: isDemoMode ? 'Demo User' : 'Pera Wallet User',
                email: isDemoMode ? 'demo@example.com' : `${walletAddress.substring(0, 8)}@perawallet.user`
            })
        });

        const data = await response.json();

        if (data.success || response.status === 400) {
            // Login if already registered
            const loginResponse = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wallet_address: walletAddress
                })
            });

            const loginData = await loginResponse.json();
            accessToken = loginData.access_token;
            currentUser = loginData.user;
        } else {
            accessToken = data.access_token;
            currentUser = { wallet_address: walletAddress };
        }

        // Save to localStorage
        saveToken(accessToken);
        localStorage.setItem('walletAddress', walletAddress);
        localStorage.setItem('isDemoMode', isDemoMode);

        // Update UI
        updateWalletUI(isDemoMode);
        alert(`Wallet connected successfully!${isDemoMode ? ' (Demo Mode)' : ''}\n\nAddress: ${walletAddress}`);

    } catch (error) {
        console.error('Wallet connection handling error:', error);
        alert('Failed to complete wallet connection');
    }
}

async function disconnectWallet() {
    try {
        if (peraWallet) {
            await peraWallet.disconnect();
        }

        clearToken();
        localStorage.removeItem('walletAddress');
        localStorage.removeItem('isDemoMode');

        // Update UI
        const connectBtn = document.getElementById('connectWalletBtn');
        if (connectBtn) {
            connectBtn.textContent = 'Connect Wallet';
            connectBtn.classList.remove('connected');
            connectBtn.onclick = connectWallet;
        }

        alert('Wallet disconnected');
    } catch (error) {
        console.error('Disconnect error:', error);
    }
}

function updateWalletUI(isDemoMode = false) {
    const connectBtn = document.getElementById('connectWalletBtn');
    if (connectBtn && currentUser) {
        const address = currentUser.wallet_address || localStorage.getItem('walletAddress');
        const shortAddress = `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
        const modeLabel = isDemoMode || localStorage.getItem('isDemoMode') === 'true' ? ' 🎮' : ' ✓';

        connectBtn.textContent = shortAddress + modeLabel;
        connectBtn.classList.add('connected');
        connectBtn.title = `Connected: ${address}\nClick to disconnect`;
        connectBtn.onclick = disconnectWallet;
    }
}

// ============= API Helper Functions =============

async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const options = {
        method,
        headers
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    return await response.json();
}

async function checkKYCStatus() {
    if (!accessToken) return { status: 'none' };
    try {
        const data = await apiCall('/api/kyc/status');
        return data;
    } catch (error) {
        console.error('Error fetching KYC status:', error);
        return { status: 'error' };
    }
}

// ============= Property Functions =============

async function loadProperties() {
    try {
        const data = await apiCall('/api/properties');
        displayProperties(data.properties);
    } catch (error) {
        console.error('Error loading properties:', error);
    }
}

function displayProperties(properties, containerId = 'propertiesContainer') {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (properties.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 4rem;"><p style="color: var(--text-muted);">No property data found.</p></div>`;
        return;
    }

    container.innerHTML = properties.map(prop => {
        const pricePerToken = prop.total_value / prop.total_tokens;
        const availableTokens = prop.available_tokens !== undefined ? prop.available_tokens : prop.total_tokens;
        const availabilityPct = (availableTokens / prop.total_tokens) * 100;

        return `
        <div class="card property-card animate-in">
            <div class="property-image">
                🏛️
                <div style="position: absolute; top: 1rem; right: 1rem;">
                    <span class="badge ${prop.status === 'verified' ? 'badge-success' : 'badge-warning'}">
                        ${prop.status === 'verified' ? 'Verified' : 'Pending'}
                    </span>
                </div>
            </div>
            <div class="property-info">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <h3 class="property-title">${prop.name}</h3>
                    <span class="badge badge-info">${prop.type}</span>
                </div>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">📍 ${prop.city} | ID: ${prop.property_id}</p>
                
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.4rem; font-weight: 600;">
                        <span>Availability</span>
                        <span>${availableTokens} / ${prop.total_tokens}</span>
                    </div>
                    <div class="progress-container" style="margin: 0;">
                        <div class="progress-bar" style="width: ${availabilityPct}%"></div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--border-light);">
                    <div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Market Value</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: var(--primary);">₹${formatPrice(prop.total_value)}</div>
                    </div>
                    <button class="btn-primary" onclick="viewProperty('${prop.property_id}')" style="padding: 0.5rem 1rem; font-size: 0.9rem;">
                        View Asset
                    </button>
                </div>
            </div>
        </div>
    `}).join('');
}

function formatPrice(price) {
    if (price >= 10000000) {
        return `${(price / 10000000).toFixed(2)} Cr`;
    } else if (price >= 100000) {
        return `${(price / 100000).toFixed(2)} L`;
    }
    return price.toLocaleString('en-IN');
}

async function viewProperty(propertyId) {
    window.location.href = `property-details.html?id=${propertyId}`;
}

// ============= Property Registration =============

async function registerProperty(formData) {
    if (!accessToken) {
        alert('Please connect your wallet first');
        return;
    }

    // Direct KYC enforcement
    const kyc = await checkKYCStatus();
    if (kyc.status !== 'verified') {
        alert('Institutional Registration Blocked: KYC verification is required to tokenize assets.');
        window.location.href = 'kyc-verification.html';
        return;
    }

    try {
        const data = await apiCall('/api/properties/register', 'POST', formData);

        if (data.success) {
            alert('Property registered successfully!');
            return data.property_id;
        } else {
            alert('Error: ' + (data.error || 'Registration failed'));
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Failed to register property');
    }
}

async function uploadDocument(propertyId, file, docType) {
    if (!accessToken) {
        alert('Please connect your wallet first');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/properties/${propertyId}/upload-document`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                },
                body: formData
            }
        );

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

async function verifyProperty(propertyId) {
    try {
        const data = await apiCall(`/api/properties/${propertyId}/verify`, 'POST');
        return data;
    } catch (error) {
        console.error('Verification error:', error);
        throw error;
    }
}

async function tokenizeProperty(propertyId) {
    try {
        const data = await apiCall(`/api/properties/${propertyId}/tokenize`, 'POST');
        return data;
    } catch (error) {
        console.error('Tokenization error:', error);
        throw error;
    }
}

// ============= KYC Functions =============

async function submitKYC(kycData) {
    if (!accessToken) {
        alert('Please connect your wallet first');
        return;
    }

    try {
        const data = await apiCall('/api/kyc/verify', 'POST', kycData);

        if (data.success) {
            alert('KYC verification successful!');
            return true;
        } else {
            alert('KYC verification failed: ' + (data.message || 'Unknown error'));
            return false;
        }
    } catch (error) {
        console.error('KYC error:', error);
        alert('KYC submission failed');
        return false;
    }
}

// ============= Trading Functions =============

async function buyTokens(propertyId, tokenAmount) {
    if (!accessToken) {
        alert('Please connect your wallet first');
        return;
    }

    try {
        // Step 1: Get property price info for payment gateway
        const propertyRes = await apiCall(`/api/properties/${propertyId}`);
        const property = propertyRes.property;
        const pricePerToken = property.total_value / property.total_tokens;
        const totalAmount = pricePerToken * tokenAmount;

        // Step 2: Trigger Payment Gateway (Simulated Razorpay)
        const paymentResult = await PaymentGateway.triggerCheckout({
            amount: totalAmount,
            name: currentUser ? currentUser.name : 'Valued Investor',
            email: currentUser ? currentUser.email : '',
            propertyId: propertyId
        });

        if (!paymentResult.success) {
            alert('Payment cancelled or failed.');
            return;
        }

        // Step 3: Call API to finalize token purchase with payment reference
        const data = await apiCall('/api/trade/buy', 'POST', {
            property_id: propertyId,
            token_amount: tokenAmount,
            payment_ref: paymentResult.payment_ref,
            order_id: paymentResult.order_id
        });

        if (data.success) {
            alert('Payment Confirmed & Tokens Purchased Successfully!');
            return data.transaction;
        } else {
            alert('Purchase failed after payment: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Trading error:', error);
        if (error.success === false) return; // User cancelled
        alert('Failed to buy tokens: ' + error.message);
    }
}

async function sellTokens(propertyId, tokenAmount) {
    if (!accessToken) {
        alert('Please connect your wallet first');
        return;
    }

    try {
        // Step 1: Get property price info for payout
        const propertyRes = await apiCall(`/api/properties/${propertyId}`);
        const property = propertyRes.property;
        const pricePerToken = property.total_value / property.total_tokens;
        const totalPayout = pricePerToken * tokenAmount;

        // Step 2: Trigger Payment Gateway (Simulated Payout Flow)
        const payoutResult = await PaymentGateway.triggerCheckout({
            amount: totalPayout,
            name: currentUser ? currentUser.name : 'Valued Investor',
            email: currentUser ? currentUser.email : '',
            propertyId: propertyId,
            mode: 'sell' // SELL mode for payout
        });

        if (!payoutResult.success) {
            alert('Payout cancelled or failed.');
            return null;
        }

        // Step 3: Call API to finalize token sale with payment reference
        const data = await apiCall('/api/trade/sell', 'POST', {
            property_id: propertyId,
            token_amount: tokenAmount,
            payment_ref: payoutResult.payment_ref,
            order_id: payoutResult.order_id
        });

        if (data.success) {
            alert('Payout Successful! Tokens debited from your account.');
            return data;
        } else {
            alert('Sale failed: ' + (data.error || 'Unknown error'));
            return null;
        }
    } catch (error) {
        console.error('Trading error:', error);
        alert('Failed to sell tokens: ' + error.message);
        return null;
    }
}

// ============= Event Listeners =============

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Pera Wallet
    initializePeraWallet();

    // Connect wallet button
    const connectBtn = document.getElementById('connectWalletBtn');
    if (connectBtn) {
        connectBtn.addEventListener('click', connectWallet);
    }

    // Get started button
    const getStartedBtn = document.getElementById('getStartedBtn');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', () => {
            window.location.href = 'register-property.html';
        });
    }

    // Restore previous session
    const storedToken = localStorage.getItem('accessToken');
    const storedAddress = localStorage.getItem('walletAddress');
    const isDemoMode = localStorage.getItem('isDemoMode') === 'true';

    if (storedToken && storedAddress) {
        accessToken = storedToken;
        currentUser = { wallet_address: storedAddress };
        updateWalletUI(isDemoMode);
    }
});

// Store token in localStorage
function saveToken(token) {
    localStorage.setItem('accessToken', token);
    accessToken = token;
}

function clearToken() {
    localStorage.removeItem('accessToken');
    accessToken = null;
    currentUser = null;
}
