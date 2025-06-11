import { useEffect, useState } from 'react';
import { fetchOverview } from '../lib/api';

interface Props {
  wellId: string;
}

interface OverviewData {
  production: number[];
  uptime: number;
  downtime: number;
  operator: string;
  district: string;
  field: string;
  tags: string[];
  reflection: string;
}

export default function WellOverview({ wellId }: Props) {
  const [data, setData] = useState<OverviewData | null>(null);

  useEffect(() => {
    fetchOverview(wellId).then(setData);
  }, [wellId]);

  if (!data) return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">Loading...</div>
  );

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="font-semibold mb-2">Well Overview</h2>
      <div className="mb-2">
        <p className="text-sm">Operator: {data.operator}</p>
        <p className="text-sm">District: {data.district}</p>
        <p className="text-sm">Field: {data.field}</p>
      </div>
      <div className="mb-2">
        <p className="text-sm">Uptime: {data.uptime}%</p>
        <p className="text-sm">Downtime: {data.downtime}%</p>
      </div>
      <div className="mb-2">
        <p className="text-sm font-semibold">Top Tags</p>
        <ul className="list-disc pl-5 text-sm">
          {data.tags.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
      <div>
        <p className="text-sm font-semibold">Most Recent Reflection</p>
        <p className="text-sm">{data.reflection}</p>
      </div>
    </div>
  );
}
