/**
 * Hook for single project management
 */

import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Project, APIError } from '../types';

export function useProject(id: string | undefined) {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<APIError | null>(null);

  useEffect(() => {
    if (!id) {
      setLoading(false);
      return;
    }

    async function fetchProject() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProject(id);
        setProject(data);
      } catch (err) {
        setError(err as APIError);
        setProject(null);
      } finally {
        setLoading(false);
      }
    }

    fetchProject();
  }, [id]);

  const deleteProject = async () => {
    if (!id) return;
    
    try {
      await api.deleteProject(id);
      setProject(null);
    } catch (err) {
      setError(err as APIError);
      throw err;
    }
  };

  const refreshProject = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const data = await api.getProject(id);
      setProject(data);
    } catch (err) {
      setError(err as APIError);
    } finally {
      setLoading(false);
    }
  };

  return {
    project,
    loading,
    error,
    deleteProject,
    refreshProject
  };
}