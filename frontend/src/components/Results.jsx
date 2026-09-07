import React from 'react';
import { Award, CheckCircle2, XCircle, TrendingUp, AlertTriangle, RefreshCw, BookOpen, Sparkles } from 'lucide-react';

export default function Results({ performance, adjustment, onRetakeTest }) {
  if (!performance) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No test performance data available yet. Complete a mock test to view your analysis.</p>
      </div>
    );
  }

  const isPass = performance.score_percentage >= 60;

  return (
    <div style={{ maxWidth: '1050px', margin: '0 auto' }}>
      {/* Overview Metric Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #182030, #0f172a)', textAlign: 'center', padding: '2.5rem' }}>
        <Award size={48} color={isPass ? 'var(--accent-green)' : 'var(--accent-amber)'} style={{ margin: '0 auto 1rem auto' }} />
        <h2 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.25rem' }}>
          {performance.score_percentage}% Score
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
          {performance.correct_count} Correct out of {performance.total_questions} Questions ({performance.answered_questions} Answered)
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', flexWrap: 'wrap' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.75rem 1.5rem', borderRadius: '12px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Correct Answers</span>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-green)' }}>
              <CheckCircle2 size={18} style={{ display: 'inline', marginRight: '4px' }} />
              {performance.correct_count}
            </div>
          </div>

          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.75rem 1.5rem', borderRadius: '12px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Incorrect Answers</span>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f87171' }}>
              <XCircle size={18} style={{ display: 'inline', marginRight: '4px' }} />
              {performance.incorrect_count}
            </div>
          </div>

          <div style={{ background: 'rgba(0, 242, 254, 0.1)', border: '1px solid rgba(0, 242, 254, 0.3)', padding: '0.75rem 1.5rem', borderRadius: '12px' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Accuracy Rating</span>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
              <TrendingUp size={18} style={{ display: 'inline', marginRight: '4px' }} />
              {performance.score_percentage}%
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Topic-wise Performance & Difficulty Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Topic-wise Breakdown */}
        <div className="card">
          <div className="card-title">
            <BookOpen size={20} color="var(--accent-cyan)" /> Topic-wise Accuracy
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {Object.entries(performance.topic_accuracy).map(([topic, acc], idx) => (
              <div key={idx}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                  <span>{topic}</span>
                  <strong style={{ color: acc >= 70 ? 'var(--accent-green)' : acc <= 50 ? '#f87171' : '#fbbf24' }}>
                    {acc}%
                  </strong>
                </div>
                <div className="progress-container" style={{ margin: 0 }}>
                  <div
                    className="progress-fill"
                    style={{
                      width: `${acc}%`,
                      background: acc >= 70 ? 'var(--accent-green)' : acc <= 50 ? '#ef4444' : '#f59e0b',
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strong & Weak Areas */}
        <div className="card">
          <div className="card-title">
            <AlertTriangle size={20} color="var(--accent-amber)" /> Adaptive Diagnostic
          </div>

          <h4 style={{ fontSize: '0.9rem', color: 'var(--accent-green)', marginBottom: '0.5rem' }}>
            Strong Topics (&ge; 70%)
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1.25rem' }}>
            {performance.strong_topics.length > 0 ? (
              performance.strong_topics.map((st, idx) => (
                <span key={idx} className="badge badge-low" style={{ textTransform: 'none' }}>
                  {st}
                </span>
              ))
            ) : (
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>None identified yet</span>
            )}
          </div>

          <h4 style={{ fontSize: '0.9rem', color: '#f87171', marginBottom: '0.5rem' }}>
            Weak Topics Needing Reinforcement
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {performance.weak_topics.length > 0 ? (
              performance.weak_topics.map((wt, idx) => (
                <span key={idx} className="badge badge-high" style={{ textTransform: 'none' }}>
                  {wt}
                </span>
              ))
            ) : (
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>None identified</span>
            )}
          </div>
        </div>
      </div>

      {/* Adaptive Schedule Adjustments */}
      {adjustment && (
        <div className="card" style={{ borderLeft: '4px solid var(--accent-purple)' }}>
          <div className="card-title" style={{ color: 'var(--accent-purple)' }}>
            <Sparkles size={20} /> Adaptive Next-Day Schedule Changes
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            The Performance Analysis Agent has dynamically updated your upcoming roadmap to address identified weak topics.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '10px' }}>
              <h5 style={{ fontSize: '0.88rem', color: 'var(--accent-cyan)', marginBottom: '0.5rem' }}>Concepts to Revise Immediately</h5>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                {adjustment.concepts_to_revise.map((c, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{c}</li>
                ))}
              </ul>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '10px' }}>
              <h5 style={{ fontSize: '0.88rem', color: 'var(--accent-green)', marginBottom: '0.5rem' }}>Recommended Practice Exercises</h5>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                {adjustment.recommended_practice.map((p, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{p}</li>
                ))}
              </ul>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '10px' }}>
              <h5 style={{ fontSize: '0.88rem', color: '#fbbf24', marginBottom: '0.5rem' }}>Next-Day Schedule Modifications</h5>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                {adjustment.next_day_schedule_changes.map((sc, i) => (
                  <li key={i} style={{ marginBottom: '4px' }}>{sc}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
