import { useState, useEffect } from 'react';
import { markupService } from '../services/api';
import { Settings, Save, X } from 'lucide-react';
import './MarkupSettings.css';

interface MarkupSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSave?: () => void;
}

interface UserMarkupSettings {
  global_overhead_percent: number;
  global_profit_percent: number;
  self_perform_markup_percent: number;
  subcontractor_markup_percent: number;
  trade_specific_markups: { [key: string]: { overhead: number; profit: number } };
  show_markups_in_pdf: boolean;
  show_markup_breakdown: boolean;
}

function MarkupSettings({ isOpen, onClose, onSave }: MarkupSettingsProps) {
  const [settings, setSettings] = useState<UserMarkupSettings>({
    global_overhead_percent: 10,
    global_profit_percent: 10,
    self_perform_markup_percent: 15,
    subcontractor_markup_percent: 20,
    trade_specific_markups: {},
    show_markups_in_pdf: true,
    show_markup_breakdown: false,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [availableTrades, setAvailableTrades] = useState<string[]>([]);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
      loadTrades();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await markupService.getUserSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load markup settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTrades = async () => {
    try {
      const data = await markupService.getAvailableTrades();
      setAvailableTrades(data.trades);
    } catch (error) {
      console.error('Failed to load trades:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await markupService.updateUserSettings(settings);
      if (onSave) onSave();
      onClose();
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const updateGlobalSetting = (field: keyof UserMarkupSettings, value: any) => {
    setSettings({ ...settings, [field]: value });
  };

  const updateTradeSetting = (trade: string, field: 'overhead' | 'profit', value: number) => {
    const tradeMarkups = { ...settings.trade_specific_markups };
    if (!tradeMarkups[trade]) {
      tradeMarkups[trade] = { overhead: settings.global_overhead_percent, profit: settings.global_profit_percent };
    }
    tradeMarkups[trade][field] = value;
    setSettings({ ...settings, trade_specific_markups: tradeMarkups });
  };

  const removeTradeSetting = (trade: string) => {
    const tradeMarkups = { ...settings.trade_specific_markups };
    delete tradeMarkups[trade];
    setSettings({ ...settings, trade_specific_markups: tradeMarkups });
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content markup-settings" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <Settings size={24} />
            Markup & Margin Settings
          </h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading settings...</div>
        ) : (
          <>
            <div className="settings-section">
              <h3>Global Markups</h3>
              <div className="setting-group">
                <label>
                  Overhead %
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.5"
                    value={settings.global_overhead_percent}
                    onChange={(e) => updateGlobalSetting('global_overhead_percent', parseFloat(e.target.value))}
                  />
                </label>
                <label>
                  Profit %
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.5"
                    value={settings.global_profit_percent}
                    onChange={(e) => updateGlobalSetting('global_profit_percent', parseFloat(e.target.value))}
                  />
                </label>
              </div>
            </div>

            <div className="settings-section">
              <h3>Performance Type Markups</h3>
              <div className="setting-group">
                <label>
                  Self-Perform Markup %
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.5"
                    value={settings.self_perform_markup_percent}
                    onChange={(e) => updateGlobalSetting('self_perform_markup_percent', parseFloat(e.target.value))}
                  />
                  <span className="help-text">Applied when you perform work in-house</span>
                </label>
                <label>
                  Subcontractor Markup %
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.5"
                    value={settings.subcontractor_markup_percent}
                    onChange={(e) => updateGlobalSetting('subcontractor_markup_percent', parseFloat(e.target.value))}
                  />
                  <span className="help-text">Applied when subcontracting work</span>
                </label>
              </div>
            </div>

            <div className="settings-section">
              <h3>Trade-Specific Overrides</h3>
              <p className="section-description">
                Set custom overhead and profit percentages for specific trades
              </p>
              
              {Object.entries(settings.trade_specific_markups).map(([trade, markups]) => (
                <div key={trade} className="trade-override">
                  <h4>{trade.charAt(0).toUpperCase() + trade.slice(1)}</h4>
                  <div className="setting-group">
                    <label>
                      Overhead %
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.5"
                        value={markups.overhead}
                        onChange={(e) => updateTradeSetting(trade, 'overhead', parseFloat(e.target.value))}
                      />
                    </label>
                    <label>
                      Profit %
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.5"
                        value={markups.profit}
                        onChange={(e) => updateTradeSetting(trade, 'profit', parseFloat(e.target.value))}
                      />
                    </label>
                    <button
                      className="remove-btn"
                      onClick={() => removeTradeSetting(trade)}
                      title="Remove override"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              ))}

              <div className="add-trade-override">
                <select
                  onChange={(e) => {
                    if (e.target.value) {
                      updateTradeSetting(e.target.value, 'overhead', settings.global_overhead_percent);
                      e.target.value = '';
                    }
                  }}
                >
                  <option value="">Add trade override...</option>
                  {availableTrades
                    .filter(trade => !settings.trade_specific_markups[trade])
                    .map(trade => (
                      <option key={trade} value={trade}>
                        {trade.charAt(0).toUpperCase() + trade.slice(1)}
                      </option>
                    ))
                  }
                </select>
              </div>
            </div>

            <div className="settings-section">
              <h3>Display Options</h3>
              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.show_markups_in_pdf}
                    onChange={(e) => updateGlobalSetting('show_markups_in_pdf', e.target.checked)}
                  />
                  Show markups in PDF exports
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={settings.show_markup_breakdown}
                    onChange={(e) => updateGlobalSetting('show_markup_breakdown', e.target.checked)}
                  />
                  Show overhead/profit breakdown separately
                </label>
              </div>
            </div>

            <div className="modal-actions">
              <button className="secondary-btn" onClick={onClose}>
                Cancel
              </button>
              <button className="primary-btn" onClick={handleSave} disabled={saving}>
                <Save size={16} />
                {saving ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default MarkupSettings;