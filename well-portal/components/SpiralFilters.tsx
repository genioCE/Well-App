import React from 'react';

export interface SpiralFilterState {
  stage: 'interpret' | 'reflect' | 'both';
  layer: 'raw' | 'truth' | 'both';
  tag: string;
}

interface Props {
  filters: SpiralFilterState;
  onChange: (filters: SpiralFilterState) => void;
}

export default function SpiralFilters({ filters, onChange }: Props) {
  const update = (partial: Partial<SpiralFilterState>) =>
    onChange({ ...filters, ...partial });

  return (
    <div className="flex gap-2 items-end mb-4">
      <label className="text-sm">
        Stage
        <select
          aria-label="stage"
          className="border rounded ml-1 px-1 py-0.5"
          value={filters.stage}
          onChange={(e) => update({ stage: e.target.value as SpiralFilterState['stage'] })}
        >
          <option value="both">Both</option>
          <option value="interpret">Interpret</option>
          <option value="reflect">Reflect</option>
        </select>
      </label>
      <label className="text-sm">
        Layer
        <select
          aria-label="layer"
          className="border rounded ml-1 px-1 py-0.5"
          value={filters.layer}
          onChange={(e) => update({ layer: e.target.value as SpiralFilterState['layer'] })}
        >
          <option value="both">Both</option>
          <option value="raw">Raw</option>
          <option value="truth">Truth</option>
        </select>
      </label>
      <label className="text-sm flex-1">
        Tags
        <input
          aria-label="tag search"
          className="border rounded w-full px-1 py-0.5 ml-1"
          value={filters.tag}
          onChange={(e) => update({ tag: e.target.value })}
          placeholder="filter tags"
        />
      </label>
    </div>
  );
}
