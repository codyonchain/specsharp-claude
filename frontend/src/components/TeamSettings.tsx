import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Mail, 
  Crown, 
  Plus, 
  Settings, 
  X,
  CreditCard,
  UserPlus,
  Info
} from 'lucide-react';
import { authService } from '../services/api';
import './TeamSettings.css';

interface CurrentUser {
  email: string;
  full_name: string;
  picture?: string;
}

interface TeamSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const TeamSettings: React.FC<TeamSettingsProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'members' | 'billing'>('members');
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadUserData();
    }
  }, [isOpen]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const user = await authService.getCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      console.error('Failed to load user data:', error);
      // Silently continue without showing error - teams aren't fully integrated yet
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleManageBilling = () => {
    // This would open the Stripe customer portal
    window.open('https://billing.stripe.com/p/login/test_placeholder', '_blank');
  };

  if (!isOpen) return null;

  return (
    <div className="team-settings-overlay" onClick={onClose}>
      <div className="team-settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="team-settings-header">
          <h2>Team Settings</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {loading ? (
          <div className="loading-state">Loading user information...</div>
        ) : (
          <>
            {/* Team Summary */}
            <div className="team-summary">
              <h3>Your Team</h3>
              <div className="seat-usage">
                <Users size={18} />
                <span>You're using 1 of 3 included seats</span>
              </div>
            </div>

            {/* Tabs */}
            <div className="team-tabs">
              <button 
                className={`tab ${activeTab === 'members' ? 'active' : ''}`}
                onClick={() => setActiveTab('members')}
              >
                Team Members
              </button>
              <button 
                className={`tab ${activeTab === 'billing' ? 'active' : ''}`}
                onClick={() => setActiveTab('billing')}
              >
                Billing & Seats
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                {error}
                <button onClick={() => setError('')}>×</button>
              </div>
            )}

            {/* Tab Content */}
            {activeTab === 'members' && (
              <div className="members-tab">
                {/* Current User */}
                <div className="members-list">
                  <h4>Current Members</h4>
                  <div className="member-item">
                    <div className="member-info">
                      <div className="member-name">
                        {currentUser?.full_name || 'You'}
                        <Crown size={16} className="owner-icon" title="Admin" />
                      </div>
                      <div className="member-email">{currentUser?.email || 'Your account'}</div>
                    </div>
                    <div className="member-actions">
                      <span className="role-badge admin">Admin</span>
                    </div>
                  </div>
                </div>

                {/* Coming Soon Section */}
                <div className="coming-soon-section">
                  <div className="coming-soon-header">
                    <UserPlus size={24} />
                    <h4>Invite Team Members</h4>
                  </div>
                  <div className="coming-soon-content">
                    <div className="info-box">
                      <Info size={20} className="info-icon" />
                      <div>
                        <p><strong>Team collaboration features coming soon!</strong></p>
                        <p>Need to add team members to your account right now? Email <a href="mailto:support@specsharp.ai">support@specsharp.ai</a> and we'll help you get set up.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'billing' && (
              <div className="billing-tab">
                <h4>Subscription Details</h4>
                <div className="subscription-info">
                  <div className="subscription-item">
                    <label>Base Plan</label>
                    <span>$799/month (includes 3 seats)</span>
                  </div>
                  <div className="subscription-item">
                    <label>Seats Used</label>
                    <span>1 of 3 included seats</span>
                  </div>
                  <div className="subscription-item total">
                    <label>Total Monthly</label>
                    <span>$799/month</span>
                  </div>
                </div>

                <div className="billing-note">
                  <p>Need to update payment method or cancel subscription?</p>
                  <button className="portal-link" onClick={handleManageBilling}>
                    <CreditCard size={16} />
                    Manage Billing →
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TeamSettings;