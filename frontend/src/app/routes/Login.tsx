import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/app/auth/AuthContext';
import styles from './Auth.module.css';
import { api } from '@/lib/apiClient';
import axios from 'axios';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError(null);
  setLoading(true);
  try {
    await login(email, password);
    // Check if user has completed profile in DB
    try {
      await api.get('/users/me');
      navigate('/');
    } catch (profileErr) {
      if (axios.isAxiosError(profileErr) && profileErr.response?.status === 404) {
        navigate('/complete-profile');
      } else {
        throw profileErr;
      }
    }
  } catch (err: any) {
    setError(err.message ?? 'Login failed');
  } finally {
    setLoading(false);
  }
};

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Login</h1>
      <form onSubmit={handleSubmit}>
        <div className={styles.field}>
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
        </div>
        <div className={styles.field}>
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
        </div>
        {error && <div role="alert" className={styles.error}>{error}</div>}
        <button type="submit" disabled={loading} className={styles.submit}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p className={styles.footer}>No account? <Link to="/register">Register</Link></p>
    </div>
  );
}
