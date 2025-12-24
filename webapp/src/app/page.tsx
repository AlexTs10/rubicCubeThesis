'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { Card, MetricCard, AlgorithmCard } from '@/components/ui/Card';
import { Target, Scale, GraduationCap, Zap, Clock, Brain, ArrowRight } from 'lucide-react';
import { ALGORITHMS } from '@/lib/constants';
import { SOLVED_STATE } from '@/lib/constants';

// Dynamic import to avoid SSR issues with Three.js
const RubiksCube3D = dynamic(() => import('@/components/cube/RubiksCube3D'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] bg-slate-800/50 rounded-xl flex items-center justify-center">
      <div className="text-slate-400">Loading 3D Cube...</div>
    </div>
  ),
});

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl sm:text-5xl font-bold mb-4">
          <span className="gradient-text">Rubik's Cube Solver</span>
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          Master's Thesis Project - University of Patras
        </p>
        <p className="text-slate-500 mt-2">
          Comparing classical cube-solving algorithms: Thistlethwaite, Kociemba, and Korf IDA*
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-2 gap-8 mb-12">
        {/* 3D Cube Preview */}
        <Card className="lg:row-span-2">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            Interactive 3D Cube
          </h2>
          <RubiksCube3D
            state={SOLVED_STATE}
            autoRotate={true}
            className="w-full h-[400px]"
          />
          <p className="text-sm text-slate-400 mt-4 text-center">
            Click and drag to rotate • Scroll to zoom
          </p>
        </Card>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            label="God's Number"
            value="20"
            color="purple"
            subtext="Maximum moves needed"
            icon={<Zap className="w-4 h-4" />}
          />
          <MetricCard
            label="Configurations"
            value="43×10¹⁸"
            color="blue"
            subtext="Possible cube states"
            icon={<Brain className="w-4 h-4" />}
          />
          <MetricCard
            label="Algorithms"
            value="3"
            color="green"
            subtext="Implemented solvers"
            icon={<Target className="w-4 h-4" />}
          />
          <MetricCard
            label="Year Range"
            value="1981-1997"
            color="yellow"
            subtext="Algorithm development"
            icon={<Clock className="w-4 h-4" />}
          />
        </div>

        {/* Quick Actions */}
        <Card>
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="grid gap-3">
            <Link
              href="/solver"
              className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Target className="w-5 h-5 text-blue-400" />
                <div>
                  <div className="font-medium">Single Solver</div>
                  <div className="text-sm text-slate-400">Test individual algorithms</div>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
            </Link>

            <Link
              href="/comparison"
              className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <Scale className="w-5 h-5 text-green-400" />
                <div>
                  <div className="font-medium">Compare Algorithms</div>
                  <div className="text-sm text-slate-400">Side-by-side comparison</div>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
            </Link>

            <Link
              href="/educational"
              className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <GraduationCap className="w-5 h-5 text-purple-400" />
                <div>
                  <div className="font-medium">Learn Algorithms</div>
                  <div className="text-sm text-slate-400">Educational content</div>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
            </Link>
          </div>
        </Card>
      </div>

      {/* Algorithm Overview */}
      <h2 className="text-2xl font-bold mb-6">Algorithms Overview</h2>
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <AlgorithmCard
          name={ALGORITHMS.thistlethwaite.name}
          emoji={ALGORITHMS.thistlethwaite.emoji}
          speed={ALGORITHMS.thistlethwaite.speed}
          moves={ALGORITHMS.thistlethwaite.moves}
          description={ALGORITHMS.thistlethwaite.description}
          color="yellow"
        />
        <AlgorithmCard
          name={ALGORITHMS.kociemba.name}
          emoji={ALGORITHMS.kociemba.emoji}
          speed={ALGORITHMS.kociemba.speed}
          moves={ALGORITHMS.kociemba.moves}
          description={ALGORITHMS.kociemba.description}
          color="blue"
        />
        <AlgorithmCard
          name={ALGORITHMS.korf.name}
          emoji={ALGORITHMS.korf.emoji}
          speed={ALGORITHMS.korf.speed}
          moves={ALGORITHMS.korf.moves}
          description={ALGORITHMS.korf.description}
          color="purple"
        />
      </div>

      {/* Comparison Table */}
      <Card className="mb-12">
        <h2 className="text-xl font-bold mb-4">Algorithm Comparison</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Algorithm</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Year</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Speed</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Moves</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Approach</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4">
                  <span className="text-yellow-400">⚡ Thistlethwaite</span>
                </td>
                <td className="py-3 px-4 text-slate-300">1981</td>
                <td className="py-3 px-4 text-green-400">Fast (0.2-0.5s)</td>
                <td className="py-3 px-4 text-slate-300">30-52</td>
                <td className="py-3 px-4 text-slate-400">4-phase group theory</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4">
                  <span className="text-blue-400">🚀 Kociemba</span>
                </td>
                <td className="py-3 px-4 text-slate-300">1992</td>
                <td className="py-3 px-4 text-yellow-400">Medium (1-3s)</td>
                <td className="py-3 px-4 text-slate-300">&lt;19</td>
                <td className="py-3 px-4 text-slate-400">2-phase IDA*</td>
              </tr>
              <tr>
                <td className="py-3 px-4">
                  <span className="text-purple-400">🐢 Korf IDA*</span>
                </td>
                <td className="py-3 px-4 text-slate-300">1997</td>
                <td className="py-3 px-4 text-red-400">Variable (1-30s)</td>
                <td className="py-3 px-4 text-slate-300">≤20</td>
                <td className="py-3 px-4 text-slate-400">Pattern databases</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Technical Details */}
      <Card>
        <details className="group">
          <summary className="cursor-pointer list-none flex items-center justify-between">
            <h2 className="text-xl font-bold">Technical Details</h2>
            <span className="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
          </summary>
          <div className="mt-4 grid md:grid-cols-2 gap-6 pt-4 border-t border-slate-700">
            <div>
              <h3 className="font-medium text-blue-400 mb-2">About This Project</h3>
              <p className="text-sm text-slate-400">
                This thesis project implements and compares three classical Rubik's Cube solving
                algorithms. The goal is to analyze the trade-offs between solution optimality,
                execution speed, and memory requirements.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-purple-400 mb-2">Key Features</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>• Interactive 3D cube visualization</li>
                <li>• Real-time solving with multiple algorithms</li>
                <li>• Detailed performance metrics</li>
                <li>• Educational content on each algorithm</li>
              </ul>
            </div>
          </div>
        </details>
      </Card>

      {/* Footer */}
      <footer className="mt-12 text-center text-slate-500 text-sm">
        <p>Master's Thesis Project • University of Patras • 2024-2025</p>
      </footer>
    </div>
  );
}
