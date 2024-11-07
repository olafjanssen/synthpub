import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { topicsApi, articlesApi, Topic } from '../services/api';

const CreateArticle: React.FC = () => {
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [selectedTopic, setSelectedTopic] = useState<number>(0);

  const { data: topics } = useQuery<Topic[]>('topics', 
    async () => {
      const response = await topicsApi.getAll();
      return response.data;
    }
  );

  const synthesizeMutation = useMutation(
    (data: { content: string; topic: string; topic_id: number }) =>
      articlesApi.synthesize(data),
    {
      onSuccess: () => {
        navigate('/articles');
      },
    }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const topic = topics?.find(t => t.id === selectedTopic);
    if (!topic) return;

    synthesizeMutation.mutate({
      content,
      topic: topic.name,
      topic_id: topic.id
    });
  };

  return (
    <div className="row">
      <div className="col-12">
        <h2>Create New Article</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Topic</label>
            <select
              className="form-select"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(Number(e.target.value))}
              required
            >
              <option value="">Select a topic</option>
              {topics?.map((topic) => (
                <option key={topic.id} value={topic.id}>
                  {topic.name}
                </option>
              ))}
            </select>
          </div>
          <div className="mb-3">
            <label className="form-label">Content</label>
            <textarea
              className="form-control"
              rows={10}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
            />
          </div>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={synthesizeMutation.isLoading}
          >
            {synthesizeMutation.isLoading ? 'Processing...' : 'Synthesize Article'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateArticle; 