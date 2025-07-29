import React, { useState } from 'react';
import { Clock, CreditCard, Check, Shield, Zap, TrendingUp } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import './PaymentWall.css';

// Initialize Stripe (you'll need to add your publishable key to env)
const stripeKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
const stripePromise = stripeKey ? loadStripe(stripeKey) : null;

interface PaymentWallProps {
  totalTimeSaved: number;
  estimatesCreated: number;
  onPaymentSuccess: () => void;
}

const CheckoutForm: React.FC<{ onSuccess: () => void }> = ({ onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setError(null);

    const cardElement = elements.getElement(CardElement);
    if (!cardElement) return;

    try {
      // Create subscription on backend
      const response = await fetch('http://localhost:8001/api/v1/subscription/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          priceId: 'price_specsharp_monthly' // You'll create this in Stripe
        })
      });

      const { clientSecret } = await response.json();

      // Confirm payment
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
        }
      });

      if (result.error) {
        setError(result.error.message || 'Payment failed');
      } else {
        // Payment successful
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <div className="card-element-container">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
              invalid: {
                color: '#9e2146',
              },
            },
          }}
        />
      </div>
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      <button
        type="submit"
        disabled={!stripe || isProcessing}
        className="subscribe-btn"
      >
        {isProcessing ? (
          <>
            <div className="spinner" />
            Processing...
          </>
        ) : (
          <>
            <CreditCard size={20} />
            Subscribe for $799/month
          </>
        )}
      </button>
      
      <div className="security-note">
        <Shield size={16} />
        <span>Secure payment powered by Stripe</span>
      </div>
    </form>
  );
};

const PaymentWall: React.FC<PaymentWallProps> = ({ 
  totalTimeSaved, 
  estimatesCreated,
  onPaymentSuccess 
}) => {
  const dollarsSaved = totalTimeSaved * 75; // $75/hour rate

  return (
    <div className="payment-wall-overlay">
      <div className="payment-wall-container">
        <div className="payment-wall-content">
          {/* Success Summary */}
          <div className="success-summary">
            <div className="congrats-header">
              <Zap size={48} className="success-icon" />
              <h1>Incredible! You've Saved {totalTimeSaved} Hours!</h1>
              <p className="subtitle">
                That's ${dollarsSaved} worth of time in just 2 minutes
              </p>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <Clock size={24} />
                <div className="stat-value">{totalTimeSaved}h</div>
                <div className="stat-label">Time Saved</div>
              </div>
              <div className="stat-card">
                <TrendingUp size={24} />
                <div className="stat-value">${dollarsSaved}</div>
                <div className="stat-label">Value Created</div>
              </div>
              <div className="stat-card">
                <Zap size={24} />
                <div className="stat-value">{estimatesCreated}</div>
                <div className="stat-label">Estimates Made</div>
              </div>
            </div>
          </div>

          {/* Payment Section */}
          <div className="payment-section">
            <div className="pricing-header">
              <h2>Ready to Save Hours Every Day?</h2>
              <p>Join thousands of contractors using SpecSharp</p>
            </div>

            <div className="pricing-card">
              <div className="price-tag">
                <span className="currency">$</span>
                <span className="amount">799</span>
                <span className="period">/month</span>
              </div>
              
              <div className="features-list">
                <div className="feature">
                  <Check size={20} className="check-icon" />
                  <span>Unlimited estimates</span>
                </div>
                <div className="feature">
                  <Check size={20} className="check-icon" />
                  <span>Professional PDF & Excel exports</span>
                </div>
                <div className="feature">
                  <Check size={20} className="check-icon" />
                  <span>Location-based comparisons</span>
                </div>
                <div className="feature">
                  <Check size={20} className="check-icon" />
                  <span>Trade package generation</span>
                </div>
                <div className="feature">
                  <Check size={20} className="check-icon" />
                  <span>Priority support</span>
                </div>
              </div>
              
              {stripePromise ? (
                <Elements stripe={stripePromise}>
                  <CheckoutForm onSuccess={onPaymentSuccess} />
                </Elements>
              ) : (
                <div className="stripe-not-configured">
                  <p>Payment processing is not configured.</p>
                  <p>Please contact support to enable payments.</p>
                </div>
              )}
            </div>

            <div className="money-back-guarantee">
              <Shield size={20} />
              <span>30-day money-back guarantee</span>
            </div>
          </div>

          {/* Trial Info */}
          <div className="trial-info">
            <p>You've used {estimatesCreated} of 3 free estimates</p>
            <p className="upgrade-prompt">Add payment to continue creating estimates</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentWall;