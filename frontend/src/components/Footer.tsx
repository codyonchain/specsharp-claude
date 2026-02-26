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
            <p className="footer-tagline">Decision Insurance for Development Deals</p>
            <p className="footer-copyright">© {currentYear} SpecSharp. All rights reserved.</p>
          </div>
        </div>

        <div className="footer-section">
          <h4>Legal</h4>
          <ul className="footer-links">
            <li><Link to="/terms">Terms of Service</Link></li>
            <li><Link to="/privacy">Privacy Policy</Link></li>
            <li><Link to="/cookies">Cookie Notice</Link></li>
            <li><a href="mailto:cody@specsharp.ai?subject=Security%20and%20Trust%20Request">Security &amp; Trust</a></li>
            <li><a href="mailto:cody@specsharp.ai?subject=Data%20Processing%20Addendum%20Request">Data Processing Addendum</a></li>
            <li><a href="mailto:cody@specsharp.ai?subject=Subprocessor%20List%20Request">Subprocessor List</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Support</h4>
          <ul className="footer-links">
            <li><Link to="/faq">FAQ</Link></li>
            <li><a href="/coverage">Building Types Supported</a></li>
            <li><a href="mailto:cody@specsharp.ai">Contact Us</a></li>
            <li><a href="mailto:cody@specsharp.ai">cody@specsharp.ai</a></li>
          </ul>
        </div>
      </div>
      <div className="footer-disclaimer">
        SpecSharp supports decision workflows and does not provide legal, tax, accounting, or investment advice. Outputs are scenario-based and not a guarantee of project performance.
      </div>
    </footer>
  );
};
