'use client';

import { CubeState, Face, FaceColor } from '@/types/cube';
import { COLOR_MAP, SOLVED_STATE } from '@/lib/constants';

interface CubeNetProps {
  state?: CubeState;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
};

function FaceGrid({ colors, size }: { colors: FaceColor[]; size: 'sm' | 'md' | 'lg' }) {
  return (
    <div className="grid grid-cols-3 gap-0.5">
      {colors.map((color, idx) => (
        <div
          key={idx}
          className={`${sizeClasses[size]} rounded-sm border border-slate-600/50`}
          style={{ backgroundColor: COLOR_MAP[color] }}
        />
      ))}
    </div>
  );
}

export default function CubeNet({
  state = SOLVED_STATE,
  size = 'md',
  className = '',
}: CubeNetProps) {
  // Net layout:
  //       [U]
  //  [L] [F] [R] [B]
  //       [D]

  const faceSize = {
    sm: 'w-[54px]',
    md: 'w-[78px]',
    lg: 'w-[102px]',
  }[size];

  return (
    <div className={`inline-block ${className}`}>
      {/* Top row - Up face */}
      <div className="flex justify-center mb-0.5">
        <div className={faceSize}>
          <FaceGrid colors={state.U} size={size} />
        </div>
      </div>

      {/* Middle row - L, F, R, B */}
      <div className="flex gap-0.5 mb-0.5">
        <FaceGrid colors={state.L} size={size} />
        <FaceGrid colors={state.F} size={size} />
        <FaceGrid colors={state.R} size={size} />
        <FaceGrid colors={state.B} size={size} />
      </div>

      {/* Bottom row - Down face */}
      <div className="flex justify-center">
        <div className={faceSize}>
          <FaceGrid colors={state.D} size={size} />
        </div>
      </div>
    </div>
  );
}
