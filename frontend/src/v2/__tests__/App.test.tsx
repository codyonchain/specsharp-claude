import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import { isAuthenticatedSession } from '../auth/session';

vi.mock('../auth/session', () => ({
  isAuthenticatedSession: vi.fn(),
}));

vi.mock('../components/common/LoadingSpinner', () => ({
  LoadingSpinner: ({ message }: { message?: string }) => <div>{message || 'Loading'}</div>,
}));

vi.mock('../pages/Dashboard/Dashboard', () => ({
  Dashboard: () => <div>Dashboard Page</div>,
}));

vi.mock('../pages/NewProject/NewProject', () => ({
  NewProject: () => <div>New Project Page</div>,
}));

vi.mock('../pages/ProjectView/ProjectView', () => ({
  ProjectView: () => <div>Project View Page</div>,
}));

vi.mock('../pages/AuthCallback', () => ({
  AuthCallback: () => <div>Auth Callback Page</div>,
}));

vi.mock('../../pages/HomePage', () => ({
  HomePage: () => <div>Home Page</div>,
}));

vi.mock('../../pages/CoveragePage', () => ({
  CoveragePage: () => <div>Coverage Page</div>,
}));

vi.mock('../../pages/FAQPage', () => ({
  FAQPage: () => <div>FAQ Page</div>,
}));

vi.mock('../../pages/TermsOfService', () => ({
  TermsOfService: () => <div>Terms Page</div>,
}));

vi.mock('../../pages/PrivacyPolicy', () => ({
  PrivacyPolicy: () => <div>Privacy Page</div>,
}));

vi.mock('../../pages/CookiePolicy', () => ({
  CookiePolicy: () => <div>Cookie Page</div>,
}));

vi.mock('../../pages/SecurityTrust', () => ({
  SecurityTrust: () => <div>Security Page</div>,
}));

vi.mock('../../pages/DataProcessingAddendum', () => ({
  DataProcessingAddendum: () => <div>DPA Page</div>,
}));

vi.mock('../../pages/SubprocessorList', () => ({
  SubprocessorList: () => <div>Subprocessors Page</div>,
}));

vi.mock('../../components/Login', () => ({
  default: () => <div>Login Page</div>,
}));

describe('App routing', () => {
  beforeEach(() => {
    vi.mocked(isAuthenticatedSession).mockReturnValue(false);
    window.history.replaceState({}, '', '/');
  });

  it('redirects authenticated diagnostics requests to the dashboard because diagnostics is not mounted', async () => {
    vi.mocked(isAuthenticatedSession).mockReturnValue(true);
    window.history.pushState({}, '', '/diagnostics');

    render(<App />);

    expect(await screen.findByText('Dashboard Page')).toBeInTheDocument();
    expect(screen.queryByText(/System Diagnostics/i)).not.toBeInTheDocument();

    await waitFor(() => {
      expect(window.location.pathname).toBe('/dashboard');
    });
  });
});
