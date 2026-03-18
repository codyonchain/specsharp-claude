import { act, renderHook, waitFor } from '@testing-library/react';
import { useProject } from '../useProject';
import { api } from '../../api/client';

vi.mock('../../api/client', () => ({
  api: {
    getProject: vi.fn(),
    deleteProject: vi.fn(),
  },
}));

describe('useProject delete behavior', () => {
  beforeEach(() => {
    vi.mocked(api.getProject).mockReset();
    vi.mocked(api.deleteProject).mockReset();
  });

  it('keeps the project visible when backend delete fails', async () => {
    vi.mocked(api.getProject).mockResolvedValue({
      id: 'proj_delete_me',
      name: 'Delete Me',
    } as any);
    vi.mocked(api.deleteProject).mockRejectedValue(new Error('Delete failed'));

    const { result } = renderHook(() => useProject('proj_delete_me'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await expect(result.current.deleteProject()).rejects.toThrow('Delete failed');
    });

    expect(result.current.project?.id).toBe('proj_delete_me');
  });

  it('clears the project from UI state after backend delete success', async () => {
    vi.mocked(api.getProject).mockResolvedValue({
      id: 'proj_delete_me',
      name: 'Delete Me',
    } as any);
    vi.mocked(api.deleteProject).mockResolvedValue(undefined);

    const { result } = renderHook(() => useProject('proj_delete_me'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.deleteProject();
    });

    expect(result.current.project).toBeNull();
  });
});
