import React, { useState } from 'react';
import { Calendar, Clock, Target, CheckSquare, Layers, Award, Download, Grid, List, ChevronDown, ChevronUp, Check } from 'lucide-react';
import { getICSCalendarUrl } from '../api';

export default function Roadmap({ roadmap, profile, sessionId }) {
  const [completedDays, setCompletedDays] = useState({});
  const [expandedDays, setExpandedDays] = useState({ 1: true }); // Day 1 open by default
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar' or 'timeline'

  if (!roadmap || !roadmap.days || roadmap.days.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No roadmap data available. Please generate your plan first.</p>
      </div>
    );
  }

  const toggleDayCompletion = (dayNum, e) => {
    if (e) e.stopPropagation();
    setCompletedDays((prev) => ({ ...prev, [dayNum]: !prev[dayNum] }));
  };

  const toggleDayExpansion = (dayNum) => {
    setExpandedDays((prev) => ({ ...prev, [dayNum]: !prev[dayNum] }));
  };

  const expandAllDays = () => {
    const all = {};
    roadmap.days.forEach((d) => (all[d.day_number] = true));
    setExpandedDays(all);
  };

  const collapseAllDays = () => {
    setExpandedDays({ 1: true });
  };

  const completedCount = Object.values(completedDays).filter(Boolean).length;
  const progressPercent = Math.round((completedCount / roadmap.days.length) * 100);

  // Helper to format date starting from today
  const getCalendarDateString = (dayIndex) => {
    const d = new Date();
    d.setDate(d.getDate() + dayIndex);
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
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
          
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
            {/* View Mode Toggle */}
            <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '10px', padding: '4px', display: 'flex', gap: '4px' }}>
              <button
                onClick={() => setViewMode('calendar')}
                className={`btn ${viewMode === 'calendar' ? 'btn-primary' : ''}`}
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <Grid size={14} /> Calendar Grid View
              </button>
              <button
                onClick={() => setViewMode('timeline')}
                className={`btn ${viewMode === 'timeline' ? 'btn-primary' : ''}`}
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <List size={14} /> Timeline View
              </button>
            </div>

            {/* Expand / Collapse All Controls */}
            <div style={{ display: 'flex', gap: '4px' }}>
              <button onClick={expandAllDays} className="btn btn-secondary" style={{ padding: '0.4rem 0.7rem', fontSize: '0.75rem' }}>
                Expand All
              </button>
              <button onClick={collapseAllDays} className="btn btn-secondary" style={{ padding: '0.4rem 0.7rem', fontSize: '0.75rem' }}>
                Collapse All
              </button>
            </div>

            {/* iCal Download Button */}
            {sessionId && (
              <a
                href={getICSCalendarUrl(sessionId)}
                download
                className="btn btn-secondary"
                style={{ fontSize: '0.8rem', padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
              >
                <Download size={15} /> Download iCal (.ics)
              </a>
            )}

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

      {/* CALENDAR VIEW GRID */}
      {viewMode === 'calendar' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {roadmap.days.map((day, idx) => {
            const isDone = Boolean(completedDays[day.day_number]);
            const isOpen = Boolean(expandedDays[day.day_number]);
            const dateStr = getCalendarDateString(idx);

            return (
              <div
                key={day.day_number}
                className="card"
                onClick={() => toggleDayExpansion(day.day_number)}
                style={{
                  borderColor: isDone ? 'var(--accent-green)' : isOpen ? 'var(--accent-cyan)' : 'var(--border-color)',
                  background: isDone ? 'rgba(16, 185, 129, 0.05)' : isOpen ? 'rgba(0, 242, 254, 0.03)' : 'rgba(255, 255, 255, 0.02)',
                  padding: '1.25rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isOpen ? '0 0 15px rgba(0, 242, 254, 0.15)' : 'none'
                }}
              >
                {/* Header Row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="badge badge-high" style={{ fontSize: '0.75rem' }}>
                      <Calendar size={12} style={{ display: 'inline', marginRight: '4px' }} />
                      {dateStr}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Day {day.day_number}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                      onClick={(e) => toggleDayCompletion(day.day_number, e)}
                      style={{
                        background: isDone ? 'var(--accent-green)' : 'transparent',
                        border: `1.5px solid ${isDone ? 'var(--accent-green)' : 'var(--text-muted)'}`,
                        borderRadius: '6px',
                        color: isDone ? '#000' : 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '3px 8px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      {isDone ? <><Check size={12} /> Done</> : 'Mark Done'}
                    </button>
                    {isOpen ? <ChevronUp size={16} color="var(--accent-cyan)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
                  </div>
                </div>

                {/* Day Title & Duration Summary */}
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: isDone ? 'var(--accent-green)' : 'var(--accent-cyan)', marginBottom: '0.35rem' }}>
                  Day {day.day_number}: {day.day_title}
                </h4>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: isOpen ? '0.75rem' : '0' }}>
                  <span><Clock size={13} style={{ display: 'inline', marginRight: '4px' }} /> {day.total_hours} hrs</span>
                  <span>{day.tasks ? day.tasks.length : 0} Focus Tasks</span>
                </div>

                {/* EXPANDABLE TASKS BODY */}
                {isOpen && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', marginTop: '0.75rem', borderTop: '1px dashed var(--border-color)', paddingTop: '0.75rem' }}>
                    {day.tasks.map((task, tIdx) => (
                      <div key={tIdx} style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem 0.85rem', borderRadius: '8px', fontSize: '0.8rem', borderLeft: `3px solid ${task.priority === 'High' ? 'var(--accent-pink)' : 'var(--accent-cyan)'}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                          <strong style={{ color: 'var(--text-main)' }}>{task.topic}</strong>
                          <span style={{ fontSize: '0.7rem', color: 'var(--accent-amber)', background: 'rgba(245, 158, 11, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                            {task.duration_hours}h
                          </span>
                        </div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '4px' }}>
                          {task.practice_task}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: '#a7f3d0' }}>
                          ✓ {task.expected_outcome}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        /* TIMELINE VIEW CARDS */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {roadmap.days.map((day, idx) => {
            const isDone = Boolean(completedDays[day.day_number]);
            const isOpen = Boolean(expandedDays[day.day_number]);
            const dateStr = getCalendarDateString(idx);

            return (
              <div
                key={day.day_number}
                className="card"
                style={{
                  borderColor: isDone ? 'var(--accent-green)' : isOpen ? 'var(--accent-cyan)' : 'var(--border-color)',
                  opacity: isDone ? 0.85 : 1,
                  transition: 'all 0.2s ease',
                }}
              >
                <div
                  onClick={() => toggleDayExpansion(day.day_number)}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', paddingBottom: isOpen ? '0.75rem' : '0', borderBottom: isOpen ? '1px solid var(--border-color)' : 'none' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <button
                      onClick={(e) => toggleDayCompletion(day.day_number, e)}
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
                    <div>
                      <span className="badge badge-info" style={{ fontSize: '0.7rem', marginRight: '8px' }}>{dateStr}</span>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 600, display: 'inline', textDecoration: isDone ? 'line-through' : 'none' }}>
                        Day {day.day_number}: {day.day_title}
                      </h3>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      <Clock size={15} style={{ display: 'inline', marginRight: '4px' }} /> <strong>{day.total_hours} hrs</strong>
                    </div>
                    {isOpen ? <ChevronUp size={18} color="var(--accent-cyan)" /> : <ChevronDown size={18} color="var(--text-muted)" />}
                  </div>
                </div>

                {/* Tasks List */}
                {isOpen && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
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
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
