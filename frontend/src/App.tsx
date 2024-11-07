import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import ErrorBoundary from './utils/ErrorBoundary';
import Navbar from './components/Navbar';
import TopicsList from './components/TopicsList';
import ArticlesList from './components/ArticlesList';
import ArticleView from './components/ArticleView';
import CreateTopic from './components/CreateTopic';
import 'bootstrap/dist/css/bootstrap.min.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <Router>
          <div className="App">
            <Navbar />
            <div className="container mt-4">
              <Routes>
                <Route path="/" element={<TopicsList />} />
                <Route path="/topics" element={<TopicsList />} />
                <Route path="/articles" element={<ArticlesList />} />
                <Route path="/articles/:id" element={<ArticleView />} />
                <Route path="/create-topic" element={<CreateTopic />} />
              </Routes>
            </div>
          </div>
        </Router>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}

export default App; 