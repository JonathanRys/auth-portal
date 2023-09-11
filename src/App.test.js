import { render, screen } from '@testing-library/react';
import App from './App';

test('renders header text', () => {
  render(<App />);
  const linkElement = screen.getByText(/Phys GPT/i);
  expect(linkElement).toBeInTheDocument();
});
