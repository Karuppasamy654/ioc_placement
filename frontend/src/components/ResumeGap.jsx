import React from 'react';
import { ShieldCheck, AlertTriangle, Lightbulb, CheckCircle, FileText, Code2, BookOpen } from 'lucide-react';

export default function ResumeGap({ profile, companyResearch }) {
  if (!profile) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No profile data available. Please generate your plan first.</p>
      </div>
    );
  }

  const hasResume = profile.resume_data && profile.resume_data.extracted_text;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
      {/* Column 1: Proven Strengths & Extracted Skills */}
      <div className="card">
        <div className="card-title" style={{ color: 'var(--accent-green)' }}>
          <ShieldCheck size={20} /> Candidate Evidenced Strengths
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Extracted from your profile inputs and parsed resume evidence.
        </p>

        {profile.strong_areas && profile.strong_areas.length > 0 ? (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
            {profile.strong_areas.map((skill, idx) => (
              <span key={idx} className="badge badge-low" style={{ textTransform: 'none', fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                <CheckCircle size={14} style={{ marginRight: '4px' }} /> {skill}
              </span>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Not enough evidence available to establish strong areas.</p>
        )}

        <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginTop: '1.25rem', marginBottom: '0.5rem' }}>
          <Code2 size={16} style={{ display: 'inline', marginRight: '6px', color: 'var(--accent-cyan)' }} />
          Detected Technical Skills
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
          {profile.user_skills && profile.user_skills.length > 0 ? (
            profile.user_skills.map((s, idx) => (
              <span key={idx} style={{ background: 'rgba(255,255,255,0.06)', padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.8rem' }}>
                {s}
              </span>
            ))
          ) : (
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No technical skills parsed.</span>
          )}
        </div>

        {hasResume && profile.resume_data && (
          <div style={{ marginTop: '1.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.85rem', borderRadius: '10px', fontSize: '0.82rem' }}>
            <FileText size={15} style={{ display: 'inline', marginRight: '6px', color: 'var(--accent-blue)' }} />
            <strong>Resume Excerpt:</strong>
            <p style={{ color: 'var(--text-muted)', marginTop: '4px' }}>
              Education: {profile.resume_data.education.join(', ') || 'N/A'}<br/>
              Languages: {profile.resume_data.programming_languages.join(', ') || 'N/A'}
            </p>
          </div>
        )}
      </div>

      {/* Column 2: Identified Gaps vs Target Role */}
      <div className="card">
        <div className="card-title" style={{ color: '#f87171' }}>
          <AlertTriangle size={20} /> Target Role Skill Gaps
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          Key technical requirements for <strong>{profile.target_role}</strong> at <strong>{profile.target_company}</strong> requiring reinforcement.
        </p>

        {profile.resume_gaps && profile.resume_gaps.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {profile.resume_gaps.map((gap, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: '10px',
                  padding: '0.85rem',
                  fontSize: '0.9rem',
                }}
              >
                <strong style={{ color: '#f87171' }}>Gap #{idx + 1}:</strong> {gap}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Not enough information available to detect gaps.</p>
        )}

        {companyResearch && companyResearch.key_skills && companyResearch.key_skills.length > 0 && (
          <div style={{ marginTop: '1.25rem' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-muted)' }}>
              <BookOpen size={15} style={{ display: 'inline', marginRight: '4px' }} /> Research Identified Role Skills
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {companyResearch.key_skills.map((ks, idx) => (
                <span key={idx} className="badge badge-info" style={{ textTransform: 'none' }}>
                  {ks}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Column 3: AI Recommendations */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-title" style={{ color: 'var(--accent-cyan)' }}>
          <Lightbulb size={20} /> Actionable AI Recommendations
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {profile.recommendations && profile.recommendations.length > 0 ? (
            profile.recommendations.map((rec, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(0, 242, 254, 0.05)',
                  border: '1px solid rgba(0, 242, 254, 0.15)',
                  borderRadius: '12px',
                  padding: '1rem',
                  fontSize: '0.9rem',
                }}
              >
                <div style={{ fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '0.35rem' }}>Recommendation #{idx + 1}</div>
                {rec}
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>Not enough information available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
