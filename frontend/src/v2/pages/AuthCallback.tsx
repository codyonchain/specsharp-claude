import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { handleAuthCallback } from '../auth/session';

export function AuthCallback() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    handleAuthCallback()
      .then((result) => {
        if (!mounted) return;
        if (result.ok) {
          window.location.replace('/dashboard');
          return;
        }
        setError(result.error);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err?.message || 'Authentication callback failed');
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (!error) {
    return (
      <div style={{ padding: 24 }}>
        Completing sign-in...
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Sign-in failed</h2>
      <p>{error}</p>
      <Link to="/login">Back to login</Link>
    </div>
  );
}
