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
    { name: 'Orchestrator Node', key: 'Orchestrator' },
    { name: 'Profile Analysis Agent', key: 'Profile Analysis Agent' },
    { name: 'Resume Parser Tool', key: 'Resume Parser' },
    { name: 'Company Research Tool', key: 'Company Research' },
    { name: 'Roadmap Agent', key: 'Roadmap Agent' },
    { name: 'Mock Test Agent', key: 'Mock Test Agent' },
    { name: 'Question Generator Tool', key: 'Question Generator' },
    { name: 'Performance Analysis Agent', key: 'Performance' },
    { name: 'Performance Analyzer Tool', key: 'Performance Analyzer' },
    { name: 'Job Discovery & Scraping Tool', key: 'Job Discovery' },
    { name: 'Learning Resource Tool', key: 'Learning Resource' },
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
      {/* Left Column: Agent & Tool Status Checklist */}
      <div className="card">
        <div className="card-title">
          <Cpu size={20} color="var(--accent-cyan)" /> Workflow & Tool Execution Progress
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '520px', overflowY: 'auto' }}>
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
                  padding: '0.65rem 0.9rem',
                  background: active ? 'rgba(0, 242, 254, 0.08)' : 'rgba(0,0,0,0.2)',
                  border: `1px solid ${active ? 'var(--border-active)' : 'var(--border-color)'}`,
                  borderRadius: '8px',
                }}
              >
                <span style={{ fontSize: '0.85rem', fontWeight: 500, color: finished ? 'var(--text-main)' : 'var(--text-muted)' }}>
                  {agent.name.includes('Tool') ? '🔧 ' : '🤖 '}{agent.name}
                </span>
                {finished ? (
                  <span style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem' }}>
                    <CheckCircle2 size={15} /> Completed
                  </span>
                ) : active ? (
                  <span style={{ color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem' }}>
                    <Activity size={15} className="spin" /> Executing
                  </span>
                ) : (
                  <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem' }}>
                    <Clock size={13} /> Pending
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Terminal Logs with Tool Output Visibility */}
      <div className="card">
        <div className="card-title">
          <Terminal size={20} color="var(--accent-purple)" /> Real-Time Terminal Execution Logs & Tool Outputs
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          Live streaming of state graph transitions, agent decisions, tool execution inputs, and tool output results.
        </p>

        <div className="terminal-box" style={{ maxHeight: '480px', overflowY: 'auto' }}>
          {events.length === 0 ? (
            <div style={{ color: '#64748b', fontStyle: 'italic' }}>
              Waiting for agent and tool execution events...
            </div>
          ) : (
            events.map((evt, idx) => {
              const isTool = evt.agent_name.toLowerCase().includes('tool') || evt.message.toLowerCase().includes('input:') || evt.message.toLowerCase().includes('completed in');
              const isMemory = evt.agent_name.toLowerCase().includes('memory');
              const isGemini = evt.agent_name.toLowerCase().includes('gemini');

              return (
                <div key={idx} className="terminal-line" style={{ margin: '3px 0' }}>
                  <span className="ts">[{evt.timestamp}]</span>
                  <span className="agent" style={{
                    color: isTool ? '#38bdf8' : isMemory ? '#a855f7' : isGemini ? '#f59e0b' : '#34d399',
                    fontWeight: isTool ? 'bold' : 'normal'
                  }}>
                    [{evt.agent_name.toUpperCase()}]
                  </span>
                  <span className={`status-${evt.status.toLowerCase()}`}>
                    ({evt.status})
                  </span>{' '}
                  <span style={{ color: isTool ? '#e2e8f0' : 'inherit' }}>
                    {evt.message}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
