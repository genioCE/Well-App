export async function fetchSpiral(wellId: string) {
  const res = await fetch('/spiral', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target: 'well_id', value: wellId, stage: 'reflect' }),
  });
  return res.json();
}

export async function queryWell(wellId: string, query: string) {
  const res = await fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ well_id: wellId, query }),
  });
  return res.json();
}

export async function searchDocs(wellId: string, query: string, mode: 'literal' | 'semantic') {
  const res = await fetch('/docs/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ well_id: wellId, query, mode }),
  });
  return res.json();
}

export async function fetchOverview(wellId: string) {
  const res = await fetch(`/well/overview?well_id=${wellId}`);
  return res.json();
}
