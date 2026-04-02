import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/apiClient';
import styles from './Auth.module.css';

export default function CompleteProfile() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: '', last_name: '',
    height_in: '', weight_lb: '',
    date_of_birth: '', gender: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.post('/users/create', {
        ...form,
        height_in: parseFloat(form.height_in),
        weight_lb: parseFloat(form.weight_lb),
      });
      navigate('/');
    } catch (err: any) {
      setError(err.userMessage ?? 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Complete your profile</h1>
      <form onSubmit={handleSubmit}>
        <div className={styles.field}><label>First name</label><input name="first_name" value={form.first_name} onChange={handleChange} required /></div>
        <div className={styles.field}><label>Last name</label><input name="last_name" value={form.last_name} onChange={handleChange} required /></div>
        <div className={styles.field}><label>Height (in)</label><input name="height_in" type="number" value={form.height_in} onChange={handleChange} required /></div>
        <div className={styles.field}><label>Weight (lb)</label><input name="weight_lb" type="number" value={form.weight_lb} onChange={handleChange} required /></div>
        <div className={styles.field}><label>Date of birth</label><input name="date_of_birth" type="date" value={form.date_of_birth} onChange={handleChange} required /></div>
        <div className={styles.field}>
          <label>Gender</label>
          <select name="gender" value={form.gender} onChange={handleChange} required>
            <option value="">Select...</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        {error && <div role="alert" className={styles.error}>{error}</div>}
        <button type="submit" disabled={loading} className={styles.submit}>
          {loading ? 'Saving...' : 'Save profile'}
        </button>
      </form>
    </div>
  );
}
