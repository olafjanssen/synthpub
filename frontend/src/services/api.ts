import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Topic {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export interface Article {
  id: number;
  title: string;
  content: string;
  topic_id: number;
  created_at: string;
  updated_at: string;
  version: number;
}

export const topicsApi = {
  getAll: () => api.get<Topic[]>('/topics'),
  getById: (id: number) => api.get<Topic>(`/topics/${id}`),
  create: (data: Partial<Topic>) => api.post<Topic>('/topics/', data),
  update: (id: number, data: Partial<Topic>) => api.put<Topic>(`/topics/${id}`, data),
};

export const articlesApi = {
  getAll: () => api.get<Article[]>('/articles'),
  getById: (id: number) => api.get<Article>(`/articles/${id}`),
  create: (data: Partial<Article>) => api.post<Article>('/articles', data),
  synthesize: (data: { content: string; topic: string; topic_id: number }) => 
    api.post('/curator/process', data),
  updateByTopic: (topicId: number) => api.post(`/articles/update-by-topic/${topicId}`),
};

export default api; 