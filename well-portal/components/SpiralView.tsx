import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import SpiralFilters, { SpiralFilterState } from './SpiralFilters';
import { fetchSpiral } from '../lib/api';
import type { MemoryPoint } from '../types';

interface Props {
  wellId: string;
  onSelect?: (id: string) => void;
}

export default function SpiralView({ wellId, onSelect }: Props) {
  const [points, setPoints] = useState<MemoryPoint[]>([]);
  const [filters, setFilters] = useState<SpiralFilterState>({
    stage: 'reflect',
    layer: 'both',
    tag: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSpiral(wellId);
        console.log('Spiral response', data);
        if (!ignore) setPoints(data.points || []);
      } catch (err) {
        console.error('Error fetching spiral', err);
        if (!ignore) setError('Failed to load spiral');
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    load();
    return () => {
      ignore = true;
    };
  }, [wellId]);

  const filtered = useMemo(() => {
    return points.filter((p) => {
      const stageOk =
        filters.stage === 'both' || p.stage === filters.stage;
      const layerOk =
        filters.layer === 'both' || p.layer === filters.layer;
      const tagOk =
        !filters.tag || p.meta?.tags?.some((t) => t.includes(filters.tag));
      return stageOk && layerOk && tagOk;
    });
  }, [points, filters]);

  const sorted = useMemo(
    () =>
      [...filtered].sort(
        (a, b) =>
          new Date(a.timestamp).getTime() -
          new Date(b.timestamp).getTime()
      ),
    [filtered]
  );

  const size = 300;
  const center = size / 2;
  const step = 20;

  const handleSelect = (id: string) => {
    setSelected(id);
    onSelect?.(id);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="font-semibold mb-2">SCADA Spiral View</h2>
      <SpiralFilters filters={filters} onChange={setFilters} />
      {loading && (
        <div className="text-center py-8" data-testid="loading">
          Loading spiral...
        </div>
      )}
      {error && !loading && (
        <div className="text-center text-red-500" data-testid="error">
          {error}
        </div>
      )}
      {!loading && !error && (
        <svg width={size} height={size} className="mx-auto block">
          <AnimatePresence>
            {sorted.map((p, i) => {
              const angle = i * 0.5;
              const radius = step * i + (60 - p.gravity_score * 10);
              const x = center + radius * Math.cos(angle);
              const y = center + radius * Math.sin(angle);
              const color = p.stage === 'interpret' ? '#93c5fd' : '#facc15';
            return (
              <motion.g
                key={p.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 120 }}
              >
                <motion.circle
                  data-testid={`point-${p.id}`}
                  cx={x}
                  cy={y}
                  r={selected === p.id ? 8 : 6}
                  fill={color}
                  className="cursor-pointer"
                  whileHover={{ scale: 1.2 }}
                  onClick={() => handleSelect(p.id)}
                >
                  <title>{`${p.summary}\n${p.timestamp}\n${p.meta?.tags?.join(', ') || ''}`}</title>
                </motion.circle>
                {p.layer === 'truth' && (
                  <motion.circle
                    cx={x}
                    cy={y}
                    r={12}
                    fill="none"
                    stroke={color}
                    className="pointer-events-none"
                    animate={{ opacity: [0.6, 0], scale: [1, 1.5] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  />
                )}
              </motion.g>
            );
          })}
          </AnimatePresence>
        </svg>
      )}
    </div>
  );
}
