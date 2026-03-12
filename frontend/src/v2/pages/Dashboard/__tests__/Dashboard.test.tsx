import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import authService from '../../../../services/authService';
import { Dashboard } from '../Dashboard';

const mockNavigate = vi.fn();
const mockUseProjects = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../../../hooks/useProjects', () => ({
  useProjects: () => mockUseProjects(),
}));

vi.mock('../../../../services/authService', () => ({
  default: {
    logout: vi.fn(),
  },
}));

describe('Dashboard', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    mockUseProjects.mockReturnValue({
      projects: [],
      loading: false,
      error: null,
      deleteProject: vi.fn(),
    });
    vi.mocked(authService.logout).mockReset();
  });

  it('renders one dashboard-only Logout control beside New Project and calls the shared logout helper', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    const newProjectButton = screen.getByRole('button', { name: /New Project/i });
    const logoutButton = screen.getByRole('button', { name: /Logout/i });

    expect(screen.getAllByRole('button', { name: /Logout/i })).toHaveLength(1);
    expect(
      newProjectButton.compareDocumentPosition(logoutButton) & Node.DOCUMENT_POSITION_FOLLOWING
    ).toBeTruthy();

    fireEvent.click(logoutButton);

    expect(authService.logout).toHaveBeenCalledTimes(1);
  });
});
