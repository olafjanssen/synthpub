import React from 'react';
import { useQuery, useMutation } from 'react-query';
import { topicsApi, articlesApi, Topic } from '../services/api';

const TopicsList: React.FC = () => {
  const { data: topics, isLoading, error } = useQuery<Topic[]>('topics', 
    async () => {
      const response = await topicsApi.getAll();
      return response.data;
    }
  );

  const updateArticleMutation = useMutation((topicId: number) => articlesApi.updateByTopic(topicId), {
    onSuccess: () => {
      alert('Article updated successfully!');
    },
    onError: () => {
      alert('Failed to update article.');
    }
  });

  if (isLoading) return <div className="spinner-border" role="status" />;
  if (error) return <div className="alert alert-danger">Error loading topics</div>;

  return (
    <div className="row">
      <div className="col-12">
        <h2>Topics</h2>
        <div className="list-group">
          {topics?.map((topic) => (
            <div key={topic.id} className="list-group-item d-flex justify-content-between align-items-start">
              <div className="ms-2 me-auto">
                <div className="fw-bold">{topic.name}</div>
                <p className="mb-1">{topic.description}</p>
                <small className="text-muted">
                  Created: {new Date(topic.created_at).toLocaleDateString()}
                </small>
              </div>
              <button 
                className="btn btn-outline-primary btn-sm"
                onClick={() => updateArticleMutation.mutate(topic.id)}
                disabled={updateArticleMutation.isLoading}
              >
                {updateArticleMutation.isLoading ? 'Updating...' : 'Update Article'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TopicsList; 