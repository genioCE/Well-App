import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import SpiralFilters from '../components/SpiralFilters';
import SpiralView from '../components/SpiralView';
import type { MemoryPoint } from '../types';
import { fetchSpiral } from '../lib/api';

jest.mock('../lib/api', () => ({
  fetchSpiral: jest.fn(),
}));

const mockPoints: MemoryPoint[] = [
  {
    id: '1',
    summary: 'A',
    timestamp: '2020-01-01T00:00:00Z',
    gravity_score: 5,
    stage: 'interpret',
    layer: 'raw',
    meta: { tags: ['alpha'] },
  },
  {
    id: '2',
    summary: 'B',
    timestamp: '2020-01-02T00:00:00Z',
    gravity_score: 3,
    stage: 'reflect',
    layer: 'truth',
    meta: { tags: ['beta'] },
  },
];

beforeEach(() => {
  (fetchSpiral as jest.Mock).mockResolvedValue({ points: mockPoints });
});

test('SpiralFilters calls onChange', () => {
  const onChange = jest.fn();
  const { getByLabelText } = render(
    <SpiralFilters
      filters={{ stage: 'both', layer: 'both', tag: '' }}
      onChange={onChange}
    />
  );
  fireEvent.change(getByLabelText('stage'), { target: { value: 'interpret' } });
  expect(onChange).toHaveBeenCalledWith(
    expect.objectContaining({ stage: 'interpret' })
  );
});

test('SpiralView selects point on click', async () => {
  const onSelect = jest.fn();
  const { getByTestId } = render(<SpiralView wellId="W1" onSelect={onSelect} />);
  await waitFor(() => getByTestId('point-1'));
  fireEvent.click(getByTestId('point-1'));
  expect(onSelect).toHaveBeenCalledWith('1');
});
