import React from 'react';
import { ExternalLink, Search, Globe, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function Sources({ companyResearch }) {
  if (!companyResearch) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No research data available yet. Generate your plan to inspect sources.</p>
      </div>
    );
  }

  const isAvailable = companyResearch.research_available;

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div className="card-title" style={{ margin: 0 }}>
            <Globe size={20} color="var(--accent-cyan)" /> Live Research Transparency & Sources
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

        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Target Company: <strong style={{ color: 'var(--text-main)' }}>{companyResearch.company_name}</strong> | Target Role: <strong style={{ color: 'var(--text-main)' }}>{companyResearch.role_name}</strong>
        </p>

        {isAvailable ? (
          <div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              The following live public sources were retrieved via external search to inform your company-specific roadmap and interview preparation:
            </p>

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
                    justifyConstraint: 'space-between',
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
                      style={{ color: 'var(--accent-blue)', border: '1px solid var(--border-color)' }}
                    >
                      Inspect Source <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              ))}
            </div>
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
