import React, { useState } from 'react';
import { User, Building2, Briefcase, Calendar, Clock, Code, Upload, Sparkles } from 'lucide-react';

export default function StudentForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    name: 'Alex Johnson',
    target_company: 'Google',
    target_role: 'Full Stack Software Engineer',
    prep_days: 7,
    daily_hours: 4.0,
    current_skills: 'JavaScript, Python, React, Data Structures, SQL',
  });
  const [resumeFile, setResumeFile] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append('name', formData.name);
    data.append('target_company', formData.target_company);
    data.append('target_role', formData.target_role);
    data.append('prep_days', formData.prep_days);
    data.append('daily_hours', formData.daily_hours);
    data.append('current_skills', formData.current_skills);
    if (resumeFile) {
      data.append('resume', resumeFile);
    }
    onSubmit(data);
  };

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: '800', marginBottom: '0.5rem' }}>
          Personalized Placement Strategy & Dynamic Mock Test
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          An agentic AI system that analyzes your profile, resume, target company, and preparation window to build an adaptive placement strategy.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label><User size={16} style={{ display: 'inline', marginRight: '4px' }} /> Candidate Full Name</label>
            <input
              type="text"
              name="name"
              className="form-input"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label><Building2 size={16} style={{ display: 'inline', marginRight: '4px' }} /> Target Company</label>
            <input
              type="text"
              name="target_company"
              className="form-input"
              value={formData.target_company}
              onChange={handleChange}
              placeholder="e.g. Amazon, Microsoft, Google, TCS"
              required
            />
          </div>

          <div className="form-group">
            <label><Briefcase size={16} style={{ display: 'inline', marginRight: '4px' }} /> Target Role</label>
            <input
              type="text"
              name="target_role"
              className="form-input"
              value={formData.target_role}
              onChange={handleChange}
              placeholder="e.g. Frontend Engineer, SDE-1, Data Analyst"
              required
            />
          </div>

          <div className="form-group">
            <label><Calendar size={16} style={{ display: 'inline', marginRight: '4px' }} /> Preparation Days Available</label>
            <input
              type="number"
              name="prep_days"
              className="form-input"
              min="1"
              max="90"
              value={formData.prep_days}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label><Clock size={16} style={{ display: 'inline', marginRight: '4px' }} /> Daily Study Hours</label>
            <input
              type="number"
              step="0.5"
              name="daily_hours"
              className="form-input"
              min="1"
              max="16"
              value={formData.daily_hours}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label><Code size={16} style={{ display: 'inline', marginRight: '4px' }} /> Current Technical Skills</label>
            <input
              type="text"
              name="current_skills"
              className="form-input"
              value={formData.current_skills}
              onChange={handleChange}
              placeholder="e.g. C++, Java, Node.js, SQL"
            />
          </div>
        </div>

        <div className="form-group" style={{ marginTop: '1.25rem' }}>
          <label><Upload size={16} style={{ display: 'inline', marginRight: '4px' }} /> Upload Resume (Optional: PDF / DOCX)</label>
          <input
            type="file"
            accept=".pdf,.docx,.doc"
            className="form-input"
            onChange={handleFileChange}
            style={{ padding: '0.5rem' }}
          />
          {resumeFile && (
            <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', marginTop: '4px' }}>
              Uploaded: {resumeFile.name}
            </span>
          )}
        </div>

        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <button type="submit" className="btn-primary" disabled={isLoading} style={{ width: '100%', padding: '1rem' }}>
            <Sparkles size={20} />
            {isLoading ? 'Orchestrator Executing Pipeline...' : 'Generate My Personalized Preparation Plan'}
          </button>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
            🔒 Privacy Note: Your resume is processed exclusively in-memory for generating your personalized strategy.
          </p>
        </div>
      </form>
    </div>
  );
}
