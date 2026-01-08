import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../hooks/useProject';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { ProjectHeader } from './ProjectHeader';
import { ExecutiveView } from './ExecutiveView';
import { ConstructionView } from './ConstructionView';

export const ProjectView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { project, loading, error, deleteProject } = useProject(id);
  const [activeView, setActiveView] = useState<'executive' | 'construction'>('executive');

  if (loading) return <LoadingSpinner size="large" message="Loading project..." />;
  if (error) return <ErrorMessage error={error} />;
  if (!project) return <div className="text-center py-8">Project not found</div>;

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await deleteProject();
        navigate('/dashboard');
      } catch (err) {
        console.error('Failed to delete project:', err);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <ProjectHeader 
        project={project} 
        onDelete={handleDelete}
        activeView={activeView}
        onViewChange={setActiveView}
      />
      
      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeView === 'executive' ? (
          <ExecutiveView project={project} />
        ) : (
          <ConstructionView project={project} />
        )}
      </div>
    </div>
  );
};
