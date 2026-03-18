import { V2APIClient } from '../client';

vi.mock('../../auth/session', () => ({
  getValidAccessToken: vi.fn().mockResolvedValue(null),
}));

const jsonResponse = (body: unknown, init: ResponseInit = {}) =>
  new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    statusText: init.statusText,
    headers: {
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  });

describe('V2APIClient authenticated reads', () => {
  const fetchMock = vi.mocked(global.fetch);

  beforeEach(() => {
    fetchMock.mockReset();
    sessionStorage.clear();
    localStorage.clear();
  });

  it('does not revive cached dashboard projects when the backend rejects the read', async () => {
    localStorage.setItem(
      'specsharp_projects',
      JSON.stringify([{ id: 'cached-project', name: 'Stale Project' }])
    );
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        { detail: 'Forbidden' },
        { status: 403, statusText: 'Forbidden' }
      )
    );

    const client = new V2APIClient();

    await expect(client.getProjects()).rejects.toMatchObject({
      name: 'APIError',
      status: 403,
    });
  });

  it('does not revive a cached project on success=false denial envelopes', async () => {
    localStorage.setItem(
      'specsharp_projects',
      JSON.stringify([{ id: 'cached-project', name: 'Stale Project' }])
    );
    fetchMock.mockResolvedValueOnce(
      jsonResponse({
        success: false,
        data: null,
        errors: ['Access denied'],
      })
    );

    const client = new V2APIClient();

    await expect(client.getProject('cached-project')).rejects.toThrow('Access denied');
  });

  it('bounds raw backend analyze failures before they reach the UI', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({
        success: false,
        data: {},
        errors: ['Traceback: confidential deal memo exploded in parser'],
      })
    );

    const client = new V2APIClient();

    await expect(client.analyzeProject('Confidential deal memo')).rejects.toMatchObject({
      name: 'APIError',
      message: "We couldn't analyze this project. Please review the description and inputs and try again.",
    });
  });
});

describe('V2APIClient deleteProject', () => {
  const fetchMock = vi.mocked(global.fetch);

  beforeEach(() => {
    fetchMock.mockReset();
    sessionStorage.clear();
    localStorage.clear();
  });

  it('calls the mounted V2 delete endpoint and removes cached state only after backend success', async () => {
    localStorage.setItem(
      'specsharp_projects',
      JSON.stringify([
        { id: 'proj_delete_me', name: 'Delete Me' },
        { id: 'proj_keep', name: 'Keep Me' },
      ])
    );
    fetchMock.mockResolvedValueOnce(
      jsonResponse({
        success: true,
        data: { message: 'Project deleted' },
      })
    );

    const client = new V2APIClient();

    await expect(client.deleteProject('proj_delete_me')).resolves.toBeUndefined();

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v2\/scope\/projects\/proj_delete_me$/),
      expect.objectContaining({
        method: 'DELETE',
      })
    );
    expect(JSON.parse(localStorage.getItem('specsharp_projects') || '[]')).toEqual([
      { id: 'proj_keep', name: 'Keep Me' },
    ]);
  });

  it('keeps cached state intact and rejects when backend delete fails', async () => {
    const cachedProjects = [
      { id: 'proj_delete_me', name: 'Delete Me' },
      { id: 'proj_keep', name: 'Keep Me' },
    ];
    localStorage.setItem('specsharp_projects', JSON.stringify(cachedProjects));
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        { detail: 'Delete failed' },
        { status: 500, statusText: 'Internal Server Error' }
      )
    );

    const client = new V2APIClient();

    await expect(client.deleteProject('proj_delete_me')).rejects.toMatchObject({
      name: 'APIError',
      status: 500,
    });
    expect(JSON.parse(localStorage.getItem('specsharp_projects') || '[]')).toEqual(
      cachedProjects
    );
  });

  it('preserves the safe run-limit contract for decision-packet generation', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse(
        {
          detail: {
            code: 'run_limit_reached',
            message: 'Run limit reached. Contact support for more runs.',
            remaining_runs: 0,
          },
        },
        { status: 403, statusText: 'Forbidden' }
      )
    );

    const client = new V2APIClient();

    await expect(
      client.createProject({
        description: 'Hotel in Nashville, TN',
      })
    ).rejects.toMatchObject({
      name: 'APIError',
      status: 403,
      code: 'run_limit_reached',
      message: 'Run limit reached. Contact support for more runs.',
    });
  });
});
