import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <div className="footer-brand">
            <h3 className="footer-logo">SpecSharp</h3>
            <p className="footer-tagline">Professional construction estimates in 60 seconds</p>
            <p className="footer-copyright">© {currentYear} SpecSharp. All rights reserved.</p>
          </div>
        </div>

        <div className="footer-section">
          <h4>Legal</h4>
          <ul className="footer-links">
            <li><Link to="/terms">Terms of Service</Link></li>
            <li><Link to="/privacy">Privacy Policy</Link></li>
            <li><Link to="/cookies">Cookie Policy</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Product</h4>
          <ul className="footer-links">
            <li><a href="/#how-it-works">How It Works</a></li>
            <li><Link to="/pricing">Pricing</Link></li>
            <li><a href="/#roi-calculator">ROI Calculator</a></li>
            <li><Link to="/demo">Demo</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Support</h4>
          <ul className="footer-links">
            <li><Link to="/faq">FAQ</Link></li>
            <li><a href="mailto:support@specsharp.ai">Contact Us</a></li>
            <li><a href="mailto:support@specsharp.ai">support@specsharp.ai</a></li>
          </ul>
        </div>
      </div>
    </footer>
  );
};