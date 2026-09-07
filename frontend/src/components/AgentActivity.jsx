import React, { useEffect, useState } from 'react';
import { Terminal, CheckCircle2, Clock, Activity, Cpu } from 'lucide-react';
import { fetchAgentEvents } from '../api';

export default function AgentActivity({ sessionId, isCompleted }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (!sessionId) return;

    const loadEvents = async () => {
      try {
        const res = await fetchAgentEvents(sessionId);
        if (res.events) {
          setEvents(res.events);
        }
      } catch (err) {
        console.error('Failed to fetch events', err);
      }
    };

    loadEvents();
    const interval = setInterval(loadEvents, 1500);
    return () => clearInterval(interval);
  }, [sessionId]);

  const agentsList = [
    { name: 'Orchestrator', key: 'Orchestrator' },
    { name: 'Profile Analysis Agent', key: 'Profile Analysis Agent' },
    { name: 'Resume Parser Tool', key: 'Resume Parser Tool' },
    { name: 'Company Research Tool', key: 'Company Research Tool' },
    { name: 'Roadmap Agent', key: 'Roadmap Agent' },
    { name: 'Mock Test Agent', key: 'Mock Test Agent' },
    { name: 'Performance Analysis Agent', key: 'Performance Analysis Agent' },
  ];

  const isAgentFinished = (agentKey) => {
    return events.some(
      (e) => e.agent_name.toLowerCase().includes(agentKey.toLowerCase()) && e.status === 'COMPLETED'
    );
  };

  const isAgentActive = (agentKey) => {
    return events.some(
      (e) => e.agent_name.toLowerCase().includes(agentKey.toLowerCase()) && e.status === 'STARTED'
    );
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '1.5rem' }}>
      {/* Left Column: Agent Status Checklist */}
      <div className="card">
        <div className="card-title">
          <Cpu size={20} color="var(--accent-cyan)" /> Workflow Progress
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {agentsList.map((agent) => {
            const finished = isAgentFinished(agent.key);
            const active = isAgentActive(agent.key) && !finished;

            return (
              <div
                key={agent.key}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  background: active ? 'rgba(0, 242, 254, 0.08)' : 'rgba(0,0,0,0.2)',
                  border: `1px solid ${active ? 'var(--border-active)' : 'var(--border-color)'}`,
                  borderRadius: '10px',
                }}
              >
                <span style={{ fontSize: '0.9rem', fontWeight: 500, color: finished ? 'var(--text-main)' : 'var(--text-muted)' }}>
                  {agent.name}
                </span>
                {finished ? (
                  <span style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                    <CheckCircle2 size={16} /> Completed
                  </span>
                ) : active ? (
                  <span style={{ color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                    <Activity size={16} className="spin" /> Executing
                  </span>
                ) : (
                  <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                    <Clock size={14} /> Pending
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Terminal Logs */}
      <div className="card">
        <div className="card-title">
          <Terminal size={20} color="var(--accent-purple)" /> Terminal Execution Logs
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          Live high-level backend events emitted by multi-agent state graph transitions.
        </p>

        <div className="terminal-box">
          {events.length === 0 ? (
            <div style={{ color: '#64748b', fontStyle: 'italic' }}>
              Waiting for backend execution events...
            </div>
          ) : (
            events.map((evt, idx) => (
              <div key={idx} className="terminal-line">
                <span className="ts">[{evt.timestamp}]</span>
                <span className="agent">[{evt.agent_name.toUpperCase()}]</span>
                <span className={`status-${evt.status.toLowerCase()}`}>
                  ({evt.status})
                </span>{' '}
                {evt.message}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
