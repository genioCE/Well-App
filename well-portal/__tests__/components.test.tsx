import React from "react";
import { render } from '@testing-library/react';
import Home from '../pages/index';

describe('Home page', () => {
  it('renders title', () => {
    const { getByText } = render(<Home />);
    expect(getByText('Show Me the Well')).toBeInTheDocument();
  });
});
