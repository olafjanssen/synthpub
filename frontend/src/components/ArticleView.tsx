import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { articlesApi, Article, Topic, topicsApi } from '../services/api';

const ArticleView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: article, isLoading: articleLoading, error: articleError } = 
    useQuery<Article>(['article', id], async () => {
      const response = await articlesApi.getById(Number(id));
      return response.data;
    });

  const { data: topics } = useQuery<Topic[]>('topics', async () => {
    const response = await topicsApi.getAll();
    return response.data;
  });

  const getTopicName = (topicId: number) => {
    return topics?.find(t => t.id === topicId)?.name || 'Unknown Topic';
  };

  if (articleLoading) {
    return (
      <div className="d-flex justify-content-center mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (articleError || !article) {
    return (
      <div className="alert alert-danger" role="alert">
        Error loading article. Please try again later.
      </div>
    );
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="card">
          <div className="card-body">
            <div className="d-flex justify-content-between align-items-start mb-4">
              <div>
                <h1 className="card-title mb-2">{article.title}</h1>
                <h6 className="card-subtitle text-muted">
                  {getTopicName(article.topic_id)}
                </h6>
              </div>
              <button 
                className="btn btn-outline-secondary"
                onClick={() => navigate('/articles')}
              >
                Back to Articles
              </button>
            </div>
            
            <div className="article-metadata mb-4">
              <span className="badge bg-primary me-2">Version {article.version}</span>
              <small className="text-muted">
                Created: {new Date(article.created_at).toLocaleDateString()}
              </small>
              <small className="text-muted ms-3">
                Last updated: {new Date(article.updated_at).toLocaleDateString()}
              </small>
            </div>

            <div className="article-content">
              {article.content.split('\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleView; 