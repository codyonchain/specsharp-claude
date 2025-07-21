import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import './Login.css';

interface LoginProps {
  setIsAuthenticated: (value: boolean) => void;
}

function Login({ setIsAuthenticated }: LoginProps) {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isRegister) {
        await authService.register(formData);
        await authService.login({
          username: formData.email,
          password: formData.password,
        });
      } else {
        await authService.login({
          username: formData.email,
          password: formData.password,
        });
      }
      setIsAuthenticated(true);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      if (err.response) {
        setError(err.response.data?.detail || `Error: ${err.response.status}`);
      } else if (err.request) {
        setError('No response from server. Please check your connection.');
      } else {
        setError(err.message || 'An error occurred');
      }
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>SpecSharp</h1>
        <h2>{isRegister ? 'Create Account' : 'Sign In'}</h2>
        
        <form onSubmit={handleSubmit}>
          {isRegister && (
            <input
              type="text"
              placeholder="Full Name"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              required
            />
          )}
          
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
          
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />
          
          {error && <div className="error">{error}</div>}
          
          <button type="submit">
            {isRegister ? 'Register' : 'Login'}
          </button>
        </form>
        
        <p>
          {isRegister ? 'Already have an account?' : "Don't have an account?"}
          <button 
            className="link-button"
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? 'Sign In' : 'Register'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;