import React from 'react';
import { ShieldCheck, AlertTriangle, Lightbulb, CheckCircle, FileText, Code2, BookOpen, Award, FileEdit, Check, X } from 'lucide-react';

export default function ResumeGap({ profile, companyResearch }) {
  if (!profile) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No profile data available. Please generate your plan first.</p>
      </div>
    );
  }

  const hasResume = profile.resume_data && profile.resume_data.extracted_text;
  const atsScore = profile.ats_resume_score || 75.0;
  const scoreDetails = profile.resume_score_details;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner: ATS Compatibility Score & Resume Match */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #182030, #131b2a)', border: '1px solid var(--accent-cyan)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <span className="badge badge-info" style={{ marginBottom: '0.5rem' }}>ATS Resume Match Engine</span>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0.25rem 0' }}>
              Target Role Compatibility Analysis
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Evaluating your resume against ATS screening benchmarks for <strong style={{ color: 'var(--accent-cyan)' }}>{profile.target_role}</strong> at <strong style={{ color: 'var(--accent-blue)' }}>{profile.target_company}</strong>
            </p>
          </div>

          {/* Score Gauge Ring */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', background: 'rgba(0,0,0,0.3)', padding: '1rem 1.5rem', borderRadius: '14px' }}>
            <div style={{ position: 'relative', width: '90px', height: '90px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="90" height="90" viewBox="0 0 36 36">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="3.8"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke={atsScore >= 80 ? 'var(--accent-green)' : atsScore >= 60 ? 'var(--accent-amber)' : '#f87171'}
                  strokeWidth="3.8"
                  strokeDasharray={`${atsScore}, 100`}
                />
              </svg>
              <div style={{ position: 'absolute', textAlign: 'center' }}>
                <span style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)' }}>{Math.round(atsScore)}%</span>
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>ATS Match Rating</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: atsScore >= 80 ? 'var(--accent-green)' : atsScore >= 60 ? 'var(--accent-amber)' : '#f87171' }}>
                {atsScore >= 80 ? 'Strong Match' : atsScore >= 60 ? 'Moderate Match' : 'Needs Formatting'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* WHAT TO CHANGE IN RESUME (Actionable Improvements Section) */}
      <div className="card" style={{ borderColor: 'var(--accent-amber)', background: 'rgba(245, 158, 11, 0.03)' }}>
        <div className="card-title" style={{ color: 'var(--accent-amber)' }}>
          <FileEdit size={22} /> Recommended Resume Changes & ATS Fixes
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Specific modifications to make to your resume to pass company ATS filters and boost interview shortlist probability.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {scoreDetails?.actionable_improvements && scoreDetails.actionable_improvements.length > 0 ? (
            scoreDetails.actionable_improvements.map((imp, idx) => (
              <div key={idx} style={{ background: 'rgba(0,0,0,0.3)', borderLeft: '4px solid var(--accent-amber)', padding: '0.85rem 1rem', borderRadius: '8px', fontSize: '0.88rem' }}>
                <strong style={{ color: 'var(--accent-amber)' }}>Fix #{idx + 1}:</strong> {imp}
              </div>
            ))
          ) : (
            <div style={{ background: 'rgba(0,0,0,0.3)', borderLeft: '4px solid var(--accent-amber)', padding: '0.85rem 1rem', borderRadius: '8px', fontSize: '0.88rem' }}>
              Add quantified metrics and explicitly mention keywords for {profile.target_role}.
            </div>
          )}

          {scoreDetails?.formatting_feedback && scoreDetails.formatting_feedback.map((fmt, idx) => (
            <div key={`fmt-${idx}`} style={{ background: 'rgba(0,0,0,0.3)', borderLeft: '4px solid var(--accent-cyan)', padding: '0.85rem 1rem', borderRadius: '8px', fontSize: '0.88rem' }}>
              <strong style={{ color: 'var(--accent-cyan)' }}>Layout Suggestion:</strong> {fmt}
            </div>
          ))}
        </div>
      </div>

      {/* Grid: Strengths vs Gaps */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Column 1: Proven Strengths & Extracted Skills */}
        <div className="card">
          <div className="card-title" style={{ color: 'var(--accent-green)' }}>
            <ShieldCheck size={20} /> Matched Technical Competencies
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Skills confirmed on your profile and resume matching target role requirements.
          </p>

          {scoreDetails?.matched_skills && scoreDetails.matched_skills.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {scoreDetails.matched_skills.map((skill, idx) => (
                <span key={idx} className="badge badge-low" style={{ textTransform: 'none', fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}>
                  <Check size={14} style={{ marginRight: '4px' }} /> {skill}
                </span>
              ))}
            </div>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {profile.strong_areas.map((s, idx) => (
                <span key={idx} className="badge badge-low" style={{ textTransform: 'none', fontSize: '0.85rem' }}>
                  <Check size={14} style={{ marginRight: '4px' }} /> {s}
                </span>
              ))}
            </div>
          )}

          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginTop: '1.25rem', marginBottom: '0.5rem' }}>
            <Code2 size={16} style={{ display: 'inline', marginRight: '6px', color: 'var(--accent-cyan)' }} />
            Parsed Resume Skills
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
        </div>

        {/* Column 2: Identified Gaps vs Target Role */}
        <div className="card">
          <div className="card-title" style={{ color: '#f87171' }}>
            <AlertTriangle size={20} /> Missing Skills & Role Gaps
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Key technical requirements for <strong>{profile.target_role}</strong> at <strong>{profile.target_company}</strong> missing from your current resume.
          </p>

          {scoreDetails?.missing_skills && scoreDetails.missing_skills.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {scoreDetails.missing_skills.map((gap, idx) => (
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
                  <strong style={{ color: '#f87171' }}>Missing Skill #{idx + 1}:</strong> {gap}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {profile.resume_gaps.map((gap, idx) => (
                <div key={idx} style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '10px', padding: '0.85rem', fontSize: '0.9rem' }}>
                  <strong style={{ color: '#f87171' }}>Gap #{idx + 1}:</strong> {gap}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

