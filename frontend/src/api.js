import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const preparePlacement = async (formData) => {
  const response = await axios.post(`${API_BASE}/prepare`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const fetchSessionStatus = async (sessionId) => {
  const response = await axios.get(`${API_BASE}/session-status`, {
    params: { session_id: sessionId },
  });
  return response.data;
};

export const fetchMockTest = async (sessionId) => {
  const response = await axios.get(`${API_BASE}/mock-test`, {
    params: { session_id: sessionId },
  });
  return response.data;
};

export const submitTestAnswers = async (submissionPayload) => {
  const response = await axios.post(`${API_BASE}/submit-test`, submissionPayload);
  return response.data;
};

export const fetchAgentEvents = async (sessionId) => {
  const response = await axios.get(`${API_BASE}/agent-events`, {
    params: { session_id: sessionId },
  });
  return response.data;
};
