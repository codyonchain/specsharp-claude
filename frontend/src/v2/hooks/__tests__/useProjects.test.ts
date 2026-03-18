import { act, renderHook, waitFor } from '@testing-library/react';
import { useProjects } from '../useProjects';
import { api } from '../../api/client';

vi.mock('../../api/client', () => ({
  api: {
    getProjects: vi.fn(),
    deleteProject: vi.fn(),
  },
}));

describe('useProjects delete behavior', () => {
  beforeEach(() => {
    vi.mocked(api.getProjects).mockReset();
    vi.mocked(api.deleteProject).mockReset();
  });

  it('keeps the project visible when backend delete fails', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([
      { id: 'proj_delete_me', name: 'Delete Me' } as any,
      { id: 'proj_keep', name: 'Keep Me' } as any,
    ]);
    vi.mocked(api.deleteProject).mockRejectedValue(new Error('Delete failed'));

    const { result } = renderHook(() => useProjects());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await expect(result.current.deleteProject('proj_delete_me')).rejects.toThrow('Delete failed');
    });

    expect(result.current.projects.map((project) => project.id)).toEqual([
      'proj_delete_me',
      'proj_keep',
    ]);
  });

  it('removes the project from UI state after backend delete success', async () => {
    vi.mocked(api.getProjects).mockResolvedValue([
      { id: 'proj_delete_me', name: 'Delete Me' } as any,
      { id: 'proj_keep', name: 'Keep Me' } as any,
    ]);
    vi.mocked(api.deleteProject).mockResolvedValue(undefined);

    const { result } = renderHook(() => useProjects());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.deleteProject('proj_delete_me');
    });

    expect(result.current.projects.map((project) => project.id)).toEqual(['proj_keep']);
  });
});
