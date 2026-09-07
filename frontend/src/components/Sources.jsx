import React from 'react';
import { ExternalLink, Globe, ShieldAlert, CheckCircle2, Briefcase, BookOpen, Sparkles } from 'lucide-react';

export default function Sources({ companyResearch }) {
  if (!companyResearch) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No research data available yet. Generate your plan to inspect sources.</p>
      </div>
    );
  }

  const isAvailable = companyResearch.research_available;
  const officialCareersUrl = companyResearch.official_careers_url;
  const studyLinks = companyResearch.study_links || [];

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Official Careers Portal Card */}
      {officialCareersUrl && (
        <div className="card" style={{ background: 'linear-gradient(135deg, #182030, #131b2a)', border: '1px solid var(--accent-cyan)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span className="badge badge-high" style={{ marginBottom: '0.4rem', textTransform: 'none' }}>
                <Briefcase size={13} style={{ marginRight: '4px' }} /> Verified Hiring Portal
              </span>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0.25rem 0' }}>
                Apply Directly to {companyResearch.company_name}
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Official job application portal for <strong style={{ color: 'var(--text-main)' }}>{companyResearch.role_name}</strong> openings at <strong style={{ color: 'var(--accent-cyan)' }}>{companyResearch.company_name}</strong>.
              </p>
            </div>
            <a
              href={officialCareersUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ fontSize: '0.9rem', padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}
            >
              Apply on Official Site <ExternalLink size={16} />
            </a>
          </div>
        </div>
      )}

      {/* Curated Technical Study Links */}
      <div className="card">
        <div className="card-title" style={{ color: 'var(--accent-cyan)' }}>
          <BookOpen size={20} /> Verified Technical Study Resources
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          High-yield technical learning indices and practice portals recommended for your preparation roadmap.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {studyLinks.map((study, idx) => (
            <div key={idx} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>
                {study.title}
              </h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                Type: {study.source_type}
              </p>
              <a
                href={study.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'var(--accent-blue)', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
              >
                Open Study Resource <ExternalLink size={13} />
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Live Web Research Sources */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="card-title" style={{ margin: 0 }}>
            <Globe size={20} color="var(--accent-cyan)" /> Company Search Results
          </div>
          {isAvailable ? (
            <span className="badge badge-low" style={{ textTransform: 'none' }}>
              <CheckCircle2 size={14} style={{ marginRight: '4px' }} /> Live Sources Verified
            </span>
          ) : (
            <span className="badge badge-high" style={{ textTransform: 'none' }}>
              <ShieldAlert size={14} style={{ marginRight: '4px' }} /> Search Unavailable
            </span>
          )}
        </div>

        {isAvailable ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {companyResearch.sources.map((src, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(0,0,0,0.25)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '1rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '0.2rem' }}>
                    {src.title}
                  </h4>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Category: {src.source_type}
                  </span>
                </div>
                {src.url && (
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="tab-btn"
                    style={{ color: 'var(--accent-blue)', border: '1px solid var(--border-color)', textDecoration: 'none' }}
                  >
                    Inspect Source <ExternalLink size={14} />
                  </a>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
            <ShieldAlert size={32} color="#f87171" style={{ margin: '0 auto 0.5rem auto' }} />
            <h4 style={{ fontSize: '1rem', color: '#f87171', marginBottom: '0.5rem' }}>Company-Specific Research Unavailable</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Live external research could not be retrieved for "{companyResearch.company_name}". The AI system has strictly fallen back to target role-based preparation for "{companyResearch.role_name}" without inventing fake company information.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

