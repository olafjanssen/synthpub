import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { topicsApi } from '../services/api';

const CreateTopic: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const createTopicMutation = useMutation(
    (data: { name: string; description: string }) => topicsApi.create(data),
    {
      onSuccess: () => {
        navigate('/topics');
      },
    }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    createTopicMutation.mutate({ name, description });
  };

  return (
    <div className="row">
      <div className="col-12">
        <h2>Create New Topic</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Topic Name</label>
            <input
              type="text"
              className="form-control"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Description</label>
            <textarea
              className="form-control"
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={createTopicMutation.isLoading}
          >
            {createTopicMutation.isLoading ? 'Creating...' : 'Create Topic'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateTopic; 