import React, { useState } from 'react';
import { HelpCircle, ChevronLeft, ChevronRight, Send, CheckCircle, AlertCircle } from 'lucide-react';

export default function MockTest({ mockTest, onSubmitTest, isSubmitting }) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});

  if (!mockTest || !mockTest.questions || mockTest.questions.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>No dynamic mock test available. Please generate your preparation plan first.</p>
      </div>
    );
  }

  const questions = mockTest.questions;
  const currentQ = questions[currentIdx];

  const handleSelectOption = (opt) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentIdx]: opt,
    }));
  };

  const answeredCount = Object.keys(selectedAnswers).length;
  const progressPercent = Math.round((answeredCount / questions.length) * 100);

  const handleSubmit = () => {
    if (answeredCount < questions.length) {
      const confirmSubmit = window.confirm(
        `You have answered ${answeredCount} out of ${questions.length} questions. Are you sure you want to submit?`
      );
      if (!confirmSubmit) return;
    }

    const payloadAnswers = Object.entries(selectedAnswers).map(([idxStr, opt]) => ({
      question_index: parseInt(idxStr, 10),
      selected_option: opt,
    }));

    onSubmitTest({
      session_id: mockTest.session_id,
      answers: payloadAnswers,
    });
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Test Header & Progress Bar */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>
              Dynamic Placement Assessment
            </h2>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Tailored assessment ({questions.length} dynamic MCQs)
            </span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
              {answeredCount} / {questions.length} Answered
            </span>
          </div>
        </div>

        <div className="progress-container">
          <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
        </div>

        {/* Question Quick-Jump Palette */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '1rem' }}>
          {questions.map((_, idx) => {
            const isAnswered = selectedAnswers[idx] !== undefined;
            const isCurrent = idx === currentIdx;

            return (
              <button
                key={idx}
                onClick={() => setCurrentIdx(idx)}
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  border: isCurrent ? '2px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                  background: isAnswered ? 'rgba(16, 185, 129, 0.25)' : 'rgba(0,0,0,0.3)',
                  color: isAnswered ? '#34d399' : 'var(--text-muted)',
                  fontSize: '0.78rem',
                  fontWeight: isCurrent ? '700' : '500',
                  cursor: 'pointer',
                }}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Current Question Card */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
            Question {currentIdx + 1} of {questions.length}
          </span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <span className="badge badge-info">{currentQ.topic || 'General'}</span>
            <span className={`badge badge-${currentQ.difficulty === 'hard' ? 'high' : currentQ.difficulty === 'medium' ? 'medium' : 'low'}`}>
              {currentQ.difficulty || 'medium'}
            </span>
          </div>
        </div>

        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, lineHeight: '1.5', marginBottom: '1.5rem' }}>
          {currentQ.question}
        </h3>

        {/* Options List */}
        <div>
          {currentQ.options.map((opt, optIdx) => {
            const optionLabels = ['A', 'B', 'C', 'D'];
            const isSelected = selectedAnswers[currentIdx] === opt;

            return (
              <div
                key={optIdx}
                className={`option-card ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSelectOption(opt)}
              >
                <div className="option-indicator">{optionLabels[optIdx] || optIdx + 1}</div>
                <div style={{ fontSize: '0.95rem', color: 'var(--text-main)' }}>{opt}</div>
              </div>
            );
          })}
        </div>

        {/* Navigation & Submit Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <button
            className="tab-btn"
            onClick={() => setCurrentIdx((prev) => Math.max(0, prev - 1))}
            disabled={currentIdx === 0}
            style={{ opacity: currentIdx === 0 ? 0.5 : 1 }}
          >
            <ChevronLeft size={18} /> Previous
          </button>

          {currentIdx < questions.length - 1 ? (
            <button
              className="btn-primary"
              onClick={() => setCurrentIdx((prev) => Math.min(questions.length - 1, prev + 1))}
            >
              Next <ChevronRight size={18} />
            </button>
          ) : (
            <button
              className="btn-primary"
              onClick={handleSubmit}
              disabled={isSubmitting}
              style={{ background: 'linear-gradient(135deg, var(--accent-green), #059669)' }}
            >
              <Send size={18} /> {isSubmitting ? 'Evaluating Test...' : 'Submit Assessment'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
