import React, { useState } from 'react';
import { Calendar, Clock, Target, CheckSquare, Layers, Award, Sparkles } from 'lucide-react';

export default function Roadmap({ roadmap, profile }) {
  const [completedDays, setCompletedDays] = useState({});

  if (!roadmap || !roadmap.days || roadmap.days.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No roadmap data available. Please generate your plan first.</p>
      </div>
    );
  }

  const toggleDayCompletion = (dayNum) => {
    setCompletedDays((prev) => ({ ...prev, [dayNum]: !prev[dayNum] }));
  };

  const completedCount = Object.values(completedDays).filter(Boolean).length;
  const progressPercent = Math.round((completedCount / roadmap.days.length) * 100);

  return (
    <div>
      {/* Strategy Overview Card */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #182030, #131b2a)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.25rem' }}>
              Personalized {roadmap.total_days}-Day Placement Strategy
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Tailored specifically for <strong style={{ color: 'var(--accent-cyan)' }}>{profile?.target_role}</strong> at{' '}
              <strong style={{ color: 'var(--accent-blue)' }}>{profile?.target_company}</strong>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem 1rem', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Daily Hours</span>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{roadmap.daily_hours} hrs</div>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem 1rem', borderRadius: '10px', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Progress</span>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-green)' }}>{progressPercent}%</div>
            </div>
          </div>
        </div>

        {roadmap.overview && (
          <div style={{ marginTop: '1rem', padding: '0.85rem', background: 'rgba(0, 242, 254, 0.05)', borderRadius: '10px', borderLeft: '4px solid var(--accent-cyan)', fontSize: '0.9rem' }}>
            <strong>Strategy Focus:</strong> {roadmap.overview}
          </div>
        )}

        <div className="progress-container" style={{ marginTop: '1.25rem' }}>
          <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
        </div>
      </div>

      {/* Day by Day Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {roadmap.days.map((day) => {
          const isDone = Boolean(completedDays[day.day_number]);

          return (
            <div
              key={day.day_number}
              className="card"
              style={{
                borderColor: isDone ? 'var(--accent-green)' : 'var(--border-color)',
                opacity: isDone ? 0.85 : 1,
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <button
                    onClick={() => toggleDayCompletion(day.day_number)}
                    style={{
                      background: isDone ? 'var(--accent-green)' : 'transparent',
                      border: `2px solid ${isDone ? 'var(--accent-green)' : 'var(--text-muted)'}`,
                      borderRadius: '6px',
                      color: '#000',
                      cursor: 'pointer',
                      padding: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <CheckSquare size={16} color={isDone ? '#000' : 'var(--text-muted)'} />
                  </button>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 600, textDecoration: isDone ? 'line-through' : 'none' }}>
                    {day.day_title}
                  </h3>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  <Clock size={15} /> Total Duration: <strong>{day.total_hours} hrs</strong>
                </div>
              </div>

              {/* Tasks List */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                {day.tasks.map((task, tIdx) => (
                  <div
                    key={tIdx}
                    style={{
                      background: 'rgba(0, 0, 0, 0.25)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '12px',
                      padding: '1rem',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>{task.topic}</h4>
                      <span className={`badge badge-${task.priority.toLowerCase()}`}>{task.priority}</span>
                    </div>

                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                      <Layers size={13} style={{ display: 'inline', marginRight: '4px' }} />
                      <strong>Subtopics:</strong> {task.subtopics.join(', ') || 'Core concepts'}
                    </div>

                    <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.65rem', borderRadius: '8px', fontSize: '0.82rem', marginBottom: '0.5rem' }}>
                      <Target size={13} style={{ display: 'inline', marginRight: '4px', color: 'var(--accent-amber)' }} />
                      <strong>Practice Task:</strong> {task.practice_task}
                    </div>

                    <div style={{ fontSize: '0.8rem', color: '#a7f3d0' }}>
                      <Award size={13} style={{ display: 'inline', marginRight: '4px' }} />
                      <strong>Expected Outcome:</strong> {task.expected_outcome}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
