'use client';

import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  gradient?: boolean;
}

export function Card({ children, className = '', hover = false, gradient = false }: CardProps) {
  return (
    <div
      className={`
        bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6
        ${hover ? 'transition-all duration-300 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10' : ''}
        ${gradient ? 'bg-gradient-to-br from-slate-800/50 to-slate-900/50' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  color?: 'blue' | 'green' | 'yellow' | 'purple' | 'red';
  subtext?: string;
}

const colorClasses = {
  blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
  green: 'from-green-500/20 to-green-600/10 border-green-500/30',
  yellow: 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30',
  purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
  red: 'from-red-500/20 to-red-600/10 border-red-500/30',
};

const textColors = {
  blue: 'text-blue-400',
  green: 'text-green-400',
  yellow: 'text-yellow-400',
  purple: 'text-purple-400',
  red: 'text-red-400',
};

export function MetricCard({ label, value, icon, color = 'blue', subtext }: MetricCardProps) {
  return (
    <div
      className={`
        bg-gradient-to-br ${colorClasses[color]}
        rounded-xl border p-4
      `}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-slate-400">{label}</span>
        {icon && <span className={textColors[color]}>{icon}</span>}
      </div>
      <div className={`text-2xl font-bold ${textColors[color]}`}>{value}</div>
      {subtext && <div className="text-xs text-slate-500 mt-1">{subtext}</div>}
    </div>
  );
}

interface AlgorithmCardProps {
  name: string;
  emoji: string;
  speed: string;
  moves: string;
  description: string;
  color: 'yellow' | 'blue' | 'purple';
  isSelected?: boolean;
  onClick?: () => void;
}

export function AlgorithmCard({
  name,
  emoji,
  speed,
  moves,
  description,
  color,
  isSelected = false,
  onClick,
}: AlgorithmCardProps) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left p-4 rounded-xl border transition-all duration-200
        ${isSelected
          ? `bg-gradient-to-br ${colorClasses[color]} border-2`
          : 'bg-slate-800/50 border-slate-700/50 hover:border-slate-600'
        }
      `}
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl">{emoji}</span>
        <span className={`font-bold ${isSelected ? textColors[color] : 'text-white'}`}>
          {name}
        </span>
      </div>
      <p className="text-sm text-slate-400 mb-3">{description}</p>
      <div className="flex gap-4 text-xs">
        <span className="text-slate-500">
          Speed: <span className={textColors[color]}>{speed}</span>
        </span>
        <span className="text-slate-500">
          Moves: <span className={textColors[color]}>{moves}</span>
        </span>
      </div>
    </button>
  );
}
