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

// ============= Property Functions =============

async function loadProperties() {
    try {
        const data = await apiCall('/api/properties');
        displayProperties(data.properties);
    } catch (error) {
        console.error('Error loading properties:', error);
    }
}

function displayProperties(properties) {
    const container = document.getElementById('propertiesContainer');
    if (!container) return;

    if (properties.length === 0) {
        container.innerHTML = '<p class="text-center">No properties available yet</p>';
        return;
    }

    container.innerHTML = properties.map(prop => `
        <div class="property-card">
            <div class="property-image">🏢</div>
            <div class="property-info">
                <h3 class="property-title">${prop.name}</h3>
                <div class="property-meta">
                    <span>📍 ${prop.city}</span>
                    <span>📐 ${prop.area_sqft} sq ft</span>
                </div>
                <div class="property-price">₹${formatPrice(prop.total_value)}</div>
                <div class="property-meta">
                    <span>🪙 ${prop.total_tokens} tokens</span>
                    <span class="badge badge-success">${prop.status}</span>
                </div>
                ${prop.risk_score ? `
                    <div class="property-meta">
                        <span>Risk: ${prop.risk_score.risk_category}</span>
                        <span>Score: ${prop.risk_score.overall_score}/100</span>
                    </div>
                ` : ''}
                <button class="btn-primary" onclick="viewProperty('${prop.property_id}')">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
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
        const data = await apiCall('/api/trade/buy', 'POST', {
            property_id: propertyId,
            token_amount: tokenAmount
        });

        if (data.success) {
            alert('Tokens purchased successfully!');
            return data.transaction;
        } else {
            alert('Purchase failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Trading error:', error);
        alert('Failed to buy tokens');
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
