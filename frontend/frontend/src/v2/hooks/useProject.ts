import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Project, APIError } from '../types';

export function useProject(id?: string) {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<APIError | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }

    const fetchProject = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProject(id);
        setProject(data);
      } catch (err) {
        setError(err as APIError);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [id]);

  const deleteProject = async () => {
    if (!id) return;
    await api.deleteProject(id);
  };

  return {
    project,
    loading,
    error,
    deleteProject
  };
}
