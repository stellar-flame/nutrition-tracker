import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/app/auth/AuthContext';
import styles from './Auth.module.css';

export default function ConfirmEmail() {
  const { confirmSignUp } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState<string>(
    (location.state as { email?: string })?.email ?? ''
  );
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await confirmSignUp(email, code);
      navigate('/login');
    } catch (err: any) {
      setError(err.message ?? 'Confirmation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Confirm your email</h1>
      {email
        ? <p className={styles.info}>We sent a 6-digit code to <strong>{email}</strong></p>
        : <p className={styles.info}>Enter the email you registered with to confirm it.</p>
      }
      <form onSubmit={handleSubmit}>
        {!email && (
          <div className={styles.field}>
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
        )}
        <div className={styles.field}>
          <label>Verification code</label>
          <input type="text" value={code} onChange={e => setCode(e.target.value)} required />
        </div>
        {error && <div role="alert" className={styles.error}>{error}</div>}
        <button type="submit" disabled={loading} className={styles.submit}>
          {loading ? 'Confirming...' : 'Confirm'}
        </button>
      </form>
    </div>
  );
}
