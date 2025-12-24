'use client';

import { ReactNode, InputHTMLAttributes, SelectHTMLAttributes } from 'react';

interface SliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  className?: string;
}

export function Slider({ label, value, onChange, min, max, step = 1, className = '' }: SliderProps) {
  return (
    <div className={className}>
      <div className="flex justify-between mb-2">
        <label className="text-sm text-slate-400">{label}</label>
        <span className="text-sm font-mono text-blue-400">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer
          [&::-webkit-slider-thumb]:appearance-none
          [&::-webkit-slider-thumb]:w-4
          [&::-webkit-slider-thumb]:h-4
          [&::-webkit-slider-thumb]:bg-blue-500
          [&::-webkit-slider-thumb]:rounded-full
          [&::-webkit-slider-thumb]:cursor-pointer
          [&::-webkit-slider-thumb]:transition-all
          [&::-webkit-slider-thumb]:hover:bg-blue-400"
      />
    </div>
  );
}

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label?: string;
  onChange?: (value: string) => void;
}

export function Input({ label, onChange, className = '', ...props }: InputProps) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm text-slate-400 mb-2">{label}</label>
      )}
      <input
        onChange={(e) => onChange?.(e.target.value)}
        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg
          text-white placeholder-slate-500
          focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500
          transition-colors"
        {...props}
      />
    </div>
  );
}

interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'onChange'> {
  label?: string;
  options: { value: string; label: string }[];
  onChange?: (value: string) => void;
}

export function Select({ label, options, onChange, className = '', value, ...props }: SelectProps) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm text-slate-400 mb-2">{label}</label>
      )}
      <select
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg
          text-white
          focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500
          transition-colors cursor-pointer"
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface TabsProps {
  tabs: { id: string; label: string; icon?: ReactNode }[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className = '' }: TabsProps) {
  return (
    <div className={`flex gap-1 p-1 bg-slate-800/50 rounded-lg ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-md transition-colors
            ${activeTab === tab.id
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white hover:bg-slate-700'
            }
          `}
        >
          {tab.icon}
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  );
}

interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
}

export function Progress({ value, max = 100, className = '', showLabel = false }: ProgressProps) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className={className}>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="text-xs text-slate-400 mt-1 text-right">{Math.round(percentage)}%</div>
      )}
    </div>
  );
}
