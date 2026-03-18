import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import { FAQPage } from '../FAQPage';
import { SecurityTrust } from '../SecurityTrust';

describe('public security trust copy', () => {
  it('removes the row-level security overclaim from the security page', () => {
    render(
      <MemoryRouter>
        <SecurityTrust />
      </MemoryRouter>
    );

    expect(
      screen.getByText(/backend-enforced organization scoping for project access and generated outputs/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/decision packets and exports are served through authenticated, scoped backend routes/i)
    ).toBeInTheDocument();
    expect(screen.queryByText(/row-level security/i)).not.toBeInTheDocument();
  });

  it('keeps the FAQ security answer aligned to repo-proven access controls', () => {
    render(
      <MemoryRouter>
        <FAQPage />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: /How is data secured\?/i }));

    expect(
      screen.getByText(
        /backend-enforced access controls, and organization-scoped authorization for project access and generated documents/i
      )
    ).toBeInTheDocument();
    expect(screen.queryByText(/row-level security/i)).not.toBeInTheDocument();
  });
});
