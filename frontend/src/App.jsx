import React, { useState, useEffect } from 'react';
import { Bot, User, Activity, Calendar, FileText, CheckSquare, Award, Globe, AlertCircle, LogIn, UserCheck } from 'lucide-react';

import AgentActivity from './components/AgentActivity';
import Roadmap from './components/Roadmap';
import ResumeGap from './components/ResumeGap';
import MockTest from './components/MockTest';
import Results from './components/Results';
import Sources from './components/Sources';
import AuthModal from './components/AuthModal';

import { preparePlacement, fetchSessionStatus, fetchMockTest, submitTestAnswers } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('activity'); // activity, roadmap, gaps, test, results, sources
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);

  const [sessionId, setSessionId] = useState('');
  const [profile, setProfile] = useState(null);
  const [companyResearch, setCompanyResearch] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [mockTest, setMockTest] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [adaptiveAdjustment, setAdaptiveAdjustment] = useState(null);

  // Poll for background agent workflow completion
  useEffect(() => {
    if (!sessionId || roadmap) return;

    const checkStatus = async () => {
      try {
        const res = await fetchSessionStatus(sessionId);
        if (res.is_complete) {
          setProfile(res.profile);
          setCompanyResearch(res.company_research);
          setRoadmap(res.roadmap);

          // Fetch questions
          try {
            const testRes = await fetchMockTest(sessionId);
            if (testRes.status === 'success') {
              setMockTest(testRes.mock_test);
            }
          } catch (tErr) {
            console.error('Error fetching mock test', tErr);
          }

          setIsLoading(false);
          // Transition to roadmap view smoothly
          setTimeout(() => {
            setActiveTab('roadmap');
          }, 1000);
        }
      } catch (err) {
        console.error('Status check error', err);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 1500);
    return () => clearInterval(interval);
  }, [sessionId, roadmap]);

  const handleAuthSuccess = (user, history, newSessionId) => {
    setCurrentUser(user);
    if (newSessionId) {
      setSessionId(newSessionId);
      setIsLoading(true);
      setActiveTab('activity');
    } else if (history && history.length > 0) {
      // Load history
      const lastSession = history[history.length - 1];
      if (lastSession && lastSession.session_id) {
        setSessionId(lastSession.session_id);
      }
    }
  };

  const handleSubmitTest = async (submissionPayload) => {
    setIsSubmitting(true);
    setErrorMessage('');

    try {
      const res = await submitTestAnswers(submissionPayload);
      if (res.status === 'success') {
        setPerformance(res.performance);
        setAdaptiveAdjustment(res.adaptive_adjustment);
        if (res.adaptive_adjustment && res.adaptive_adjustment.updated_roadmap_days && roadmap) {
          setRoadmap((prev) => ({
            ...prev,
            days: res.adaptive_adjustment.updated_roadmap_days,
          }));
        }
        setActiveTab('results');
      }
    } catch (err) {
      console.error(err);
      setErrorMessage(err.response?.data?.detail || 'Error submitting quiz answers.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation Header */}
      <header className="app-header">
        <div className="logo-area">
          <div className="logo-icon">
            <Bot size={22} />
          </div>
          <div className="logo-text">
            <h1>AI Placement Agent</h1>
            <p>Adaptive Placement Preparation & Resume ATS Scoring</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <nav className="nav-tabs">
            <button
              className={`tab-btn ${activeTab === 'activity' ? 'active' : ''}`}
              onClick={() => setActiveTab('activity')}
            >
              <Activity size={15} /> Agent Execution {isLoading && '⚡'}
            </button>
            <button
              className={`tab-btn ${activeTab === 'roadmap' ? 'active' : ''}`}
              onClick={() => setActiveTab('roadmap')}
              disabled={!roadmap}
            >
              <Calendar size={15} /> Roadmap Schedule
            </button>
            <button
              className={`tab-btn ${activeTab === 'gaps' ? 'active' : ''}`}
              onClick={() => setActiveTab('gaps')}
              disabled={!profile}
            >
              <FileText size={15} /> ATS Resume Score & Fixes
            </button>
            <button
              className={`tab-btn ${activeTab === 'test' ? 'active' : ''}`}
              onClick={() => setActiveTab('test')}
              disabled={!mockTest}
            >
              <CheckSquare size={15} /> Mock Test
            </button>
            <button
              className={`tab-btn ${activeTab === 'results' ? 'active' : ''}`}
              onClick={() => setActiveTab('results')}
              disabled={!performance}
            >
              <Award size={15} /> Performance
            </button>
            <button
              className={`tab-btn ${activeTab === 'sources' ? 'active' : ''}`}
              onClick={() => setActiveTab('sources')}
              disabled={!companyResearch}
            >
              <Globe size={15} /> Sources & Apply
            </button>
          </nav>

          {/* User Auth Controls */}
          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(0,242,254,0.1)', padding: '0.4rem 0.85rem', borderRadius: '8px', border: '1px solid var(--accent-cyan)', fontSize: '0.85rem' }}>
              <UserCheck size={16} color="var(--accent-cyan)" />
              <span style={{ fontWeight: 600 }}>{currentUser.name}</span>
            </div>
          ) : (
            <button
              onClick={() => setIsAuthModalOpen(true)}
              className="btn btn-primary"
              style={{ padding: '0.45rem 0.9rem', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <LogIn size={15} /> Login / Register
            </button>
          )}
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Main App Workspace */}
      <main className="main-content">
        {errorMessage && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '1rem',
              borderRadius: '12px',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
            }}
          >
            <AlertCircle size={20} />
            <span>{errorMessage}</span>
          </div>
        )}

        {!currentUser && !sessionId && (
          <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem', background: 'linear-gradient(135deg, #0f172a, #1e293b)', border: '1px solid var(--accent-cyan)' }}>
            <Bot size={48} color="var(--accent-cyan)" style={{ marginBottom: '1rem' }} />
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.5rem' }}>Welcome to AI Placement Agent</h2>
            <p style={{ color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto 1.5rem auto', fontSize: '0.95rem' }}>
              Please register or log in to validate your resume, calculate your ATS Compatibility Score, and generate a 100% personalized preparation roadmap.
            </p>
            <button onClick={() => setIsAuthModalOpen(true)} className="btn btn-primary" style={{ padding: '0.75rem 1.8rem', fontSize: '1rem' }}>
              <LogIn size={18} style={{ display: 'inline', marginRight: '6px' }} /> Register or Sign In Now
            </button>
          </div>
        )}

        {activeTab === 'activity' && (sessionId || currentUser) && (
          <AgentActivity sessionId={sessionId} isCompleted={Boolean(roadmap)} />
        )}

        {activeTab === 'roadmap' && (
          <Roadmap roadmap={roadmap} profile={profile} sessionId={sessionId} />
        )}

        {activeTab === 'gaps' && (
          <ResumeGap profile={profile} companyResearch={companyResearch} />
        )}

        {activeTab === 'test' && (
          <MockTest mockTest={mockTest} onSubmitTest={handleSubmitTest} isSubmitting={isSubmitting} />
        )}

        {activeTab === 'results' && (
          <Results performance={performance} adjustment={adaptiveAdjustment} />
        )}

        {activeTab === 'sources' && (
          <Sources companyResearch={companyResearch} />
        )}
      </main>

      <footer className="app-footer">
        AI Placement Agent &bull; Multi-Agent System Powered by Gemini API &bull; 100% Dynamic Assessment Strategy
      </footer>
    </div>
  );
}

