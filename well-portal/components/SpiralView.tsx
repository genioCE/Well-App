import { useEffect, useRef } from 'react';
import { fetchSpiral } from '../lib/api';

type Point = {
  timestamp: string;
  gravity_score: number;
};

interface Props {
  wellId: string;
}

export default function SpiralView({ wellId }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    async function draw() {
      const data = await fetchSpiral(wellId);
      const ctx = canvasRef.current?.getContext('2d');
      if (!ctx) return;
      ctx.clearRect(0, 0, 300, 300);
      // placeholder spiral rendering
      (data.points as Point[]).forEach((p, i) => {
        const angle = i * 0.3;
        const radius = i * 2;
        const x = 150 + radius * Math.cos(angle);
        const y = 150 + radius * Math.sin(angle);
        ctx.beginPath();
        ctx.arc(x, y, p.gravity_score, 0, Math.PI * 2);
        ctx.fillStyle = '#3b82f6';
        ctx.fill();
      });
    }
    draw();
  }, [wellId]);

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
      <h2 className="font-semibold mb-2">SCADA Spiral View</h2>
      <canvas ref={canvasRef} width={300} height={300} />
    </div>
  );
}
