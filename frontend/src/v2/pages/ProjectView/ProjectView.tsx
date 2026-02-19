import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProject } from '../../hooks/useProject';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { ProjectHeader } from './ProjectHeader';
import { ExecutiveViewComplete } from './ExecutiveViewComplete';
import { ConstructionView } from './ConstructionView';
import { DealShieldView } from './DealShieldView';
import { api } from '../../api/client';
import { DealShieldViewModel } from '../../types';

export const ProjectView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { project, loading, error, deleteProject } = useProject(id);
  const [activeView, setActiveView] = useState<'dealshield' | 'executive' | 'construction'>('executive');
  const [dealShieldState, setDealShieldState] = useState<{
    data: DealShieldViewModel | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });
  const hasUserSelectedViewRef = useRef(false);

  useEffect(() => {
    hasUserSelectedViewRef.current = false;
    setActiveView('executive');
    setDealShieldState({ data: null, loading: false, error: null });
  }, [id]);

  useEffect(() => {
    if (!id) return;
    let isActive = true;
    setDealShieldState((prev) => ({ ...prev, loading: true, error: null }));
    api.fetchDealShield(id)
      .then((response) => {
        if (!isActive) return;
        setDealShieldState({ data: response, loading: false, error: null });
        if (!hasUserSelectedViewRef.current) {
          setActiveView('dealshield');
        }
      })
      .catch((err: Error) => {
        if (!isActive) return;
        setDealShieldState({ data: null, loading: false, error: err });
      });
    return () => {
      isActive = false;
    };
  }, [id]);

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

  const handleViewChange = (view: 'dealshield' | 'executive' | 'construction') => {
    hasUserSelectedViewRef.current = true;
    setActiveView(view);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <ProjectHeader 
        project={project} 
        onDelete={handleDelete}
        activeView={activeView}
        onViewChange={handleViewChange}
      />
      
      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeView === 'dealshield' ? (
          <DealShieldView
            projectId={id || project.id}
            data={dealShieldState.data}
            loading={dealShieldState.loading}
            error={dealShieldState.error}
          />
        ) : activeView === 'executive' ? (
          <ExecutiveViewComplete
            project={project}
            dealShieldData={dealShieldState.data}
          />
        ) : (
          <ConstructionView project={project} />
        )}
      </div>
    </div>
  );
};
