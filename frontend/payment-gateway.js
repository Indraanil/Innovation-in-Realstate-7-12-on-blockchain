/**
 * PaymentGateway - A simulated payment processor for BharatPropChain
 * Mimics the behavior and look of an authentic payment gateway (like Razorpay)
 * Supports both Buy (Payment) and Sell (Payout) modes.
 */
const PaymentGateway = (() => {
    let currentOrder = null;
    let resolveCallback = null;
    let rejectCallback = null;

    const createModal = () => {
        const modalId = 'payment-gateway-modal';
        if (document.getElementById(modalId)) return document.getElementById(modalId);

        const modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        modal.style.cssText = `
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 9999;
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
        `;

        modal.innerHTML = `
            <div style="background: white; width: 90%; max-width: 450px; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.3); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                <div id="pgHeader" style="background: #2b3990; padding: 20px; color: white; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span id="pgIcon" style="font-size: 24px;">🏢</span>
                        <div>
                            <div id="pgTitle" style="font-weight: bold; font-size: 1.1rem;">BharatPropChain Checkout</div>
                            <div style="font-size: 0.8rem; opacity: 0.8;">Order: #<span id="pgOrderRef">ORDER-123</span></div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: bold; font-size: 1.2rem;">₹<span id="pgAmount">0.00</span></div>
                    </div>
                </div>
                
                <div id="pgContent" style="padding: 24px;">
                    <h3 id="pgSubTitle" style="margin-bottom: 20px; font-size: 1rem; color: #444;">Select Payment Method</h3>
                    
                    <div id="pgMethodsList">
                        <!-- Methods dynamic -->
                    </div>

                    <div style="text-align: center; font-size: 0.7rem; color: #aaa;">
                        ⚖️ Secured by BharatPropChain Vault
                    </div>
                </div>

                <div id="pgProcessing" style="display: none; padding: 40px; text-align: center;">
                    <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #2b3990; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <h3 id="pgProcStatus">Processing Payment...</h3>
                    <p id="pgProcDesc" style="color: #666; font-size: 0.9rem;">Please do not close this window</p>
                </div>

                <div id="pgSuccess" style="display: none; padding: 40px; text-align: center;">
                    <div id="pgCheck" style="font-size: 60px; color: #4caf50; margin-bottom: 20px;">✅</div>
                    <h3 id="pgSuccessTitle">Payment Successful!</h3>
                    <p style="color: #2e7d32; font-size: 0.9rem; margin-bottom: 20px;">Transaction ID: <span id="pgTxnId">BHARAT-123456</span></p>
                    <button onclick="PaymentGateway.complete()" style="background: #4caf50; color: white; border: none; padding: 12px 30px; border-radius: 8px; font-weight: bold; cursor: pointer;">Continue to Platform</button>
                </div>
            </div>
            <style>
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                .pg-method { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 12px; cursor: pointer; display: flex; align-items: center; gap: 15px; transition: all 0.2s; }
                .pg-method:hover { background: #f8f9ff; border-color: #2b3990 !important; transform: translateY(-2px); }
            </style>
        `;

        document.body.appendChild(modal);
        return modal;
    };

    return {
        /**
         * Trigger the simulated checkout
         * @param {Object} options { amount, name, email, propertyId, mode: 'buy'|'sell' }
         * @returns {Promise}
         */
        triggerCheckout: (options) => {
            return new Promise((resolve, reject) => {
                const modal = createModal();
                const isSell = options.mode === 'sell';
                const orderRef = (isSell ? 'SELL_' : 'ORDER_') + Math.random().toString(36).substring(7).toUpperCase();

                currentOrder = { ...options, orderRef };
                resolveCallback = resolve;
                rejectCallback = reject;

                // Update UI based on mode
                const header = document.getElementById('pgHeader');
                if (header) header.style.background = isSell ? '#00695c' : '#2b3990';

                const title = document.getElementById('pgTitle');
                if (title) title.textContent = isSell ? 'BharatPropChain Payout' : 'BharatPropChain Checkout';

                const icon = document.getElementById('pgIcon');
                if (icon) icon.textContent = isSell ? '💰' : '🏢';

                const subtitle = document.getElementById('pgSubTitle');
                if (subtitle) subtitle.textContent = isSell ? 'Select Payout Method' : 'Select Payment Method';

                const orderRefEl = document.getElementById('pgOrderRef');
                if (orderRefEl) orderRefEl.textContent = orderRef;

                const amountEl = document.getElementById('pgAmount');
                if (amountEl) amountEl.textContent = options.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 });

                const methodsDiv = document.getElementById('pgMethodsList');
                if (methodsDiv) {
                    if (isSell) {
                        methodsDiv.innerHTML = `
                            <div class="pg-method" onclick="PaymentGateway.process('UPI Payout')">
                                <span style="font-size: 20px;">📱</span>
                                <div style="flex: 1;">
                                    <div style="font-weight: bold; color: #333;">Instant UPI Payout</div>
                                    <div style="font-size: 0.75rem; color: #666;">Transfer to primary UPI ID</div>
                                </div>
                                <span style="color: #999;">></span>
                            </div>
                            <div class="pg-method" onclick="PaymentGateway.process('Bank Transfer')">
                                <span style="font-size: 20px;">🏦</span>
                                <div style="flex: 1;">
                                    <div style="font-weight: bold; color: #333;">Bank Transfer (NEFT/RTGS)</div>
                                    <div style="font-size: 0.75rem; color: #666;">Settlement in 2-4 hours</div>
                                </div>
                                <span style="color: #999;">></span>
                            </div>
                        `;
                    } else {
                        methodsDiv.innerHTML = `
                            <div class="pg-method" onclick="PaymentGateway.process('UPI')">
                                <span style="font-size: 20px;">📱</span>
                                <div style="flex: 1;">
                                    <div style="font-weight: bold; color: #333;">UPI</div>
                                    <div style="font-size: 0.75rem; color: #666;">Google Pay, PhonePe, Paytm</div>
                                </div>
                                <span style="color: #999;">></span>
                            </div>
                            <div class="pg-method" onclick="PaymentGateway.process('Card')">
                                <span style="font-size: 20px;">💳</span>
                                <div style="flex: 1;">
                                    <div style="font-weight: bold; color: #333;">Card</div>
                                    <div style="font-size: 0.75rem; color: #666;">Visa, Mastercard, RuPay</div>
                                </div>
                                <span style="color: #999;">></span>
                            </div>
                        `;
                    }
                }

                // Show modal and reset views
                modal.style.display = 'flex';
                document.getElementById('pgContent').style.display = 'block';
                document.getElementById('pgProcessing').style.display = 'none';
                document.getElementById('pgSuccess').style.display = 'none';
            });
        },

        process: (method) => {
            const isSell = currentOrder.mode === 'sell';
            document.getElementById('pgContent').style.display = 'none';
            document.getElementById('pgProcessing').style.display = 'block';
            document.getElementById('pgProcStatus').textContent = isSell ? 'Initiating Payout...' : 'Processing Payment...';
            document.getElementById('pgProcDesc').textContent = isSell ? 'Verifying bank details' : 'Please do not close this window';

            // Simulate network delay
            setTimeout(() => {
                document.getElementById('pgProcessing').style.display = 'none';
                document.getElementById('pgSuccess').style.display = 'block';
                document.getElementById('pgSuccessTitle').textContent = isSell ? 'Payout Successful!' : 'Payment Successful!';
                const txnId = (isSell ? 'PAYOUT_' : 'TXN_') + Math.random().toString(36).substring(7).toUpperCase();
                document.getElementById('pgTxnId').textContent = txnId;
                currentOrder.txnId = txnId;
            }, 2500);
        },

        complete: () => {
            document.getElementById('payment-gateway-modal').style.display = 'none';
            if (resolveCallback) resolveCallback({
                success: true,
                payment_ref: currentOrder.txnId,
                order_id: currentOrder.orderRef
            });
        },

        cancel: () => {
            document.getElementById('payment-gateway-modal').style.display = 'none';
            if (rejectCallback) rejectCallback({ success: false, error: 'User cancelled' });
        }
    };
})();
