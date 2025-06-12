export interface MemoryPoint {
  id: string;
  summary: string;
  timestamp: string;
  gravity_score: number;
  stage: 'interpret' | 'reflect';
  layer: 'raw' | 'truth';
  meta?: {
    tags?: string[];
    [key: string]: any;
  };
}
