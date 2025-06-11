import { useState } from 'react';
import { searchDocs } from '../lib/api';

interface Props {
  wellId: string;
}

export default function DocumentSearch({ wellId }: Props) {
  const [mode, setMode] = useState<'literal' | 'semantic'>('literal');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);

  const search = async () => {
    const res = await searchDocs(wellId, query, mode);
    setResults(res.results || []);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Document Search</h2>
      <div className="flex gap-2 mb-2">
        <input
          className="flex-1 border rounded px-2"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search documents"
        />
        <select
          className="border rounded"
          value={mode}
          onChange={(e) => setMode(e.target.value as 'literal' | 'semantic')}
        >
          <option value="literal">Literal</option>
          <option value="semantic">Semantic</option>
        </select>
        <button className="px-3 py-1 bg-blue-500 text-white rounded" onClick={search}>
          Search
        </button>
      </div>
      <ul className="space-y-1 text-sm max-h-40 overflow-auto">
        {results.map((r, idx) => (
          <li key={idx} className="border-b pb-1">
            <p>{r.snippet}</p>
            <p className="text-xs text-gray-500">{r.date}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
