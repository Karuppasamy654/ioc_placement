import React, { useState } from 'react';
import { User, Lock, Mail, Building, Briefcase, Calendar, Clock, Upload, AlertCircle, CheckCircle, LogIn, UserPlus, X } from 'lucide-react';
import { registerUser, loginUser } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Form states
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [targetCompany, setTargetCompany] = useState('Google');
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [prepDays, setPrepDays] = useState(14);
  const [dailyHours, setDailyHours] = useState(4);
  const [currentSkills, setCurrentSkills] = useState('Python, Algorithms, SQL');
  const [resumeFile, setResumeFile] = useState(null);

  if (!isOpen) return null;

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');
    setLoading(true);

    try {
      const res = await loginUser({ username, password });
      if (res.status === 'success') {
        setSuccessMsg(`Welcome back, ${res.user.name}!`);
        setTimeout(() => {
          onAuthSuccess(res.user, res.history, res.session_id, false);
          onClose();
        }, 1000);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('email', email);
      formData.append('password', password);
      formData.append('name', name);
      formData.append('target_company', targetCompany);
      formData.append('target_role', targetRole);
      formData.append('prep_days', prepDays);
      formData.append('daily_hours', dailyHours);
      formData.append('current_skills', currentSkills);

      if (resumeFile) {
        formData.append('resume', resumeFile);
      }

      const res = await registerUser(formData);
      if (res.status === 'success') {
        setSuccessMsg('Account created & resume validated! View your ATS Resume Score & Fixes in the top menu.');
        setTimeout(() => {
          onAuthSuccess(res.user, null, res.session_id, true);
          onClose();
        }, 1200);
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please check your resume and form inputs.';
      setErrorMsg(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(8px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem'
    }}>
      <div className="card" style={{
        maxWidth: '540px', width: '100%', maxHeight: '90vh', overflowY: 'auto',
        background: '#0d131f', border: '1px solid var(--accent-cyan)', position: 'relative'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute', top: '1rem', right: '1rem', background: 'transparent',
            border: 'none', color: 'var(--text-muted)', cursor: 'pointer'
          }}
        >
          <X size={20} />
        </button>

        {/* Tab Toggle */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
          <button
            onClick={() => { setMode('login'); setErrorMsg(''); setSuccessMsg(''); }}
            style={{
              flex: 1, padding: '0.85rem', background: 'transparent', border: 'none',
              color: mode === 'login' ? 'var(--accent-cyan)' : 'var(--text-muted)',
              borderBottom: mode === 'login' ? '2px solid var(--accent-cyan)' : 'none',
              fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px'
            }}
          >
            <LogIn size={16} /> Candidate Login
          </button>
          <button
            onClick={() => { setMode('register'); setErrorMsg(''); setSuccessMsg(''); }}
            style={{
              flex: 1, padding: '0.85rem', background: 'transparent', border: 'none',
              color: mode === 'register' ? 'var(--accent-cyan)' : 'var(--text-muted)',
              borderBottom: mode === 'register' ? '2px solid var(--accent-cyan)' : 'none',
              fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px'
            }}
          >
            <UserPlus size={16} /> Register & Validate Resume
          </button>
        </div>

        {/* Error Alert Box */}
        {errorMsg && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '10px', padding: '0.85rem 1rem', marginBottom: '1.25rem',
            color: '#f87171', fontSize: '0.85rem', display: 'flex', alignItems: 'flex-start', gap: '8px'
          }}>
            <AlertCircle size={18} style={{ shrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Validation Alert:</strong> {errorMsg}
            </div>
          </div>
        )}

        {/* Success Alert Box */}
        {successMsg && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.4)',
            borderRadius: '10px', padding: '0.85rem 1rem', marginBottom: '1.25rem',
            color: '#34d399', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px'
          }}>
            <CheckCircle size={18} /> {successMsg}
          </div>
        )}

        {/* LOGIN FORM */}
        {mode === 'login' ? (
          <form onSubmit={handleLoginSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label><User size={14} style={{ display: 'inline', marginRight: '4px' }} /> Registered Username</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. john_doe"
                className="input-field"
              />
            </div>

            <div className="form-group">
              <label><Lock size={14} style={{ display: 'inline', marginRight: '4px' }} /> Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-field"
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem', padding: '0.8rem' }}>
              {loading ? 'Authenticating...' : 'Sign In to Dashboard'}
            </button>
          </form>
        ) : (
          /* REGISTER FORM */
          <form onSubmit={handleRegisterSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="john_doe"
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="john@example.com"
                  className="input-field"
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div className="form-group">
                <label>Candidate Full Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input-field"
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div className="form-group">
                <label>Target Company</label>
                <input
                  type="text"
                  required
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
                  placeholder="Google"
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label>Target Role</label>
                <input
                  type="text"
                  required
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="Software Engineer"
                  className="input-field"
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.85rem' }}>
              <div className="form-group">
                <label>Prep Timeframe (Days)</label>
                <input
                  type="number"
                  min="1"
                  max="90"
                  required
                  value={prepDays}
                  onChange={(e) => setPrepDays(Number(e.target.value))}
                  className="input-field"
                />
              </div>

              <div className="form-group">
                <label>Daily Study Hours</label>
                <input
                  type="number"
                  min="1"
                  max="16"
                  step="0.5"
                  required
                  value={dailyHours}
                  onChange={(e) => setDailyHours(Number(e.target.value))}
                  className="input-field"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Current Skills (Comma Separated)</label>
              <input
                type="text"
                value={currentSkills}
                onChange={(e) => setCurrentSkills(e.target.value)}
                placeholder="Python, Algorithms, System Design"
                className="input-field"
              />
            </div>

            {/* Resume Upload Box */}
            <div className="form-group">
              <label><Upload size={14} style={{ display: 'inline', marginRight: '4px' }} /> Candidate Resume (PDF / DOCX)</label>
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={(e) => setResumeFile(e.target.files[0])}
                className="input-field"
                style={{ padding: '0.5rem' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                * Your name in the form must match your name inside the uploaded resume.
              </span>
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem', padding: '0.8rem' }}>
              {loading ? 'Validating Resume & Registering...' : 'Complete Registration'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
