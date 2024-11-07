import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { articlesApi, Article, Topic, topicsApi } from '../services/api';

const ArticlesList: React.FC = () => {
  const { data: articles, isLoading: articlesLoading, error: articlesError } = 
    useQuery<Article[]>('articles', async () => {
      const response = await articlesApi.getAll();
      return response.data;
    });

  const { data: topics } = useQuery<Topic[]>('topics', async () => {
    const response = await topicsApi.getAll();
    return response.data;
  });

  const getTopicName = (topicId: number) => {
    return topics?.find(t => t.id === topicId)?.name || 'Unknown Topic';
  };

  if (articlesLoading) {
    return (
      <div className="d-flex justify-content-center mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (articlesError) {
    return (
      <div className="alert alert-danger" role="alert">
        Error loading articles. Please try again later.
      </div>
    );
  }

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Articles</h2>
          <Link to="/create-article" className="btn btn-primary">
            Create New Article
          </Link>
        </div>
        <div className="row row-cols-1 row-cols-md-2 g-4">
          {articles?.map((article) => (
            <div key={article.id} className="col">
              <div className="card h-100">
                <div className="card-body">
                  <h5 className="card-title">{article.title}</h5>
                  <h6 className="card-subtitle mb-2 text-muted">
                    {getTopicName(article.topic_id)}
                  </h6>
                  <p className="card-text">
                    {article.content.substring(0, 150)}...
                  </p>
                  <div className="d-flex justify-content-between align-items-center">
                    <Link 
                      to={`/articles/${article.id}`} 
                      className="btn btn-outline-primary"
                    >
                      Read More
                    </Link>
                    <small className="text-muted">
                      Version {article.version}
                    </small>
                  </div>
                </div>
                <div className="card-footer text-muted">
                  <small>
                    Last updated: {new Date(article.updated_at).toLocaleDateString()}
                  </small>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ArticlesList; 