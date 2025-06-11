import { fetchSpiral, queryWell, searchDocs, fetchOverview } from '../lib/api';

beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ json: () => Promise.resolve({ ok: true }) })
  ) as jest.Mock;
});

describe('api helpers', () => {
  it('fetchSpiral posts to /spiral', async () => {
    await fetchSpiral('WELL-001');
    expect(fetch).toHaveBeenCalledWith('/spiral', expect.any(Object));
  });

  it('queryWell posts to /query', async () => {
    await queryWell('WELL-001', 'hi');
    expect(fetch).toHaveBeenCalledWith('/query', expect.any(Object));
  });

  it('searchDocs posts to /docs/search', async () => {
    await searchDocs('WELL-001', 'test', 'literal');
    expect(fetch).toHaveBeenCalledWith('/docs/search', expect.any(Object));
  });

  it('fetchOverview fetches /well/overview', async () => {
    await fetchOverview('WELL-001');
    expect(fetch).toHaveBeenCalledWith('/well/overview?well_id=WELL-001');
  });
});
