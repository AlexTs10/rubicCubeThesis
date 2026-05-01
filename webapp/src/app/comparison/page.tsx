'use client';

import { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Card, MetricCard } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { Slider, Input } from '@/components/ui/Controls';
import { Progress } from '@/components/ui/Controls';
import CubeNet from '@/components/cube/CubeNet';
import { Play, Download, Trophy, Clock, Hash, HardDrive, Check, X, RotateCcw } from 'lucide-react';
import { CubeState, Move, Algorithm, SolveResult } from '@/types/cube';
import { ALGORITHMS, SOLVED_STATE } from '@/lib/constants';
import { generateScramble, applyMoves, formatMoves } from '@/lib/cube';
import { compareAlgorithms, formatTime, formatMemory, analyzeResults } from '@/lib/solver';

const RubiksCube3D = dynamic(() => import('@/components/cube/RubiksCube3D'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[300px] bg-slate-800/50 rounded-xl flex items-center justify-center">
      <div className="text-slate-400">Loading 3D Cube...</div>
    </div>
  ),
});

export default function ComparisonPage() {
  // Settings
  const [scrambleDepth, setScrambleDepth] = useState(15);
  const [seed, setSeed] = useState(42);
  const [timeouts, setTimeouts] = useState({
    thistlethwaite: 10,
    kociemba: 30,
    korf: 60,
  });

  // State
  const [scrambleMoves, setScrambleMoves] = useState<Move[]>([]);
  const [cubeState, setCubeState] = useState<CubeState>(SOLVED_STATE);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<SolveResult[]>([]);

  // Run comparison
  const handleRunComparison = useCallback(async () => {
    setRunning(true);
    setProgress(0);
    setResults([]);

    // Generate scramble
    const moves = generateScramble(scrambleDepth, seed);
    setScrambleMoves(moves);
    const newState = applyMoves({ ...SOLVED_STATE }, moves);
    setCubeState(newState);

    setProgress(10);

    try {
      // Run comparison
      const compareResults = await compareAlgorithms(moves, {
        thistlethwaite: timeouts.thistlethwaite * 1000,
        kociemba: timeouts.kociemba * 1000,
        korf: timeouts.korf * 1000,
      });

      setProgress(100);
      setResults(compareResults);
    } catch (error) {
      console.error('Comparison error:', error);
    } finally {
      setRunning(false);
    }
  }, [scrambleDepth, seed, timeouts]);

  // Reset
  const handleReset = useCallback(() => {
    setCubeState({ ...SOLVED_STATE });
    setScrambleMoves([]);
    setResults([]);
    setProgress(0);
  }, []);

  // Export results
  const handleExport = useCallback((format: 'json' | 'csv') => {
    if (results.length === 0) return;

    let content: string;
    let filename: string;
    let mimeType: string;

    if (format === 'json') {
      content = JSON.stringify({
        source: 'synthetic-preview',
        demoOnly: true,
        scramble: scrambleMoves,
        results: results.map(r => ({
          algorithm: r.algorithm,
          solved: r.solved,
          solutionLength: r.solutionLength,
          timeMs: r.timeMs,
          memoryMb: r.memoryMb,
          demoOnly: r.demoOnly ?? true,
          solution: r.solution,
          backend: r.backend,
          optimality: r.optimality,
          notes: r.notes,
        })),
        timestamp: new Date().toISOString(),
      }, null, 2);
      filename = 'comparison_preview_results.json';
      mimeType = 'application/json';
    } else {
      const headers = ['Algorithm', 'Solved', 'Moves', 'Time (ms)', 'Memory (MB)', 'Nodes', 'Demo Only'];
      const rows = results.map(r => [
        r.algorithm,
        r.solved ? 'Yes' : 'No',
        r.solutionLength,
        r.timeMs.toFixed(2),
        r.memoryMb.toFixed(2),
        r.nodesExplored || 'N/A',
        r.demoOnly ? 'Yes' : 'No',
      ]);
      content = [headers, ...rows].map(row => row.join(',')).join('\n');
      filename = 'comparison_preview_results.csv';
      mimeType = 'text/csv';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }, [results, scrambleMoves]);

  const winners = results.length > 0 ? analyzeResults(results) : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">Algorithm Comparison</span>
        </h1>
        <p className="text-slate-400">Preview all three benchmark profiles side-by-side on the same scramble</p>
        <p className="text-sm text-slate-500 mt-2">
          Demo data follows the corrected benchmark profile, but this page does not run the repository solvers. The outputs are synthetic previews.
        </p>
        <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-100">
          This web comparison view uses synthetic preview data. Each move sequence is the inverse
          scramble rather than a live solver result, so the page should not be cited as benchmark
          evidence. The authoritative thesis benchmark is produced by the Python evaluation
          pipeline under <code>results/benchmarks/thesis/</code>.
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-8">
        {/* Settings Panel */}
        <div className="space-y-6">
          <Card>
            <h2 className="text-lg font-bold mb-4">Configuration</h2>

            <Slider
              label="Scramble Depth"
              value={scrambleDepth}
              onChange={setScrambleDepth}
              min={5}
              max={20}
              className="mb-4"
            />

            <Input
              label="Random Seed"
              type="number"
              value={seed.toString()}
              onChange={(v) => setSeed(parseInt(v) || 0)}
              className="mb-6"
            />

            <h3 className="text-sm font-medium text-slate-400 mb-3">Timeouts (seconds)</h3>
            <div className="space-y-3">
              {(Object.keys(ALGORITHMS) as Algorithm[]).map((algo) => (
                <div key={algo} className="flex items-center gap-2">
                  <span className="text-sm w-24">{ALGORITHMS[algo].emoji} {ALGORITHMS[algo].name}</span>
                  <Input
                    type="number"
                    value={timeouts[algo].toString()}
                    onChange={(v) => setTimeouts({ ...timeouts, [algo]: parseInt(v) || 10 })}
                    className="flex-1"
                  />
                </div>
              ))}
            </div>
          </Card>

          <Button
            onClick={handleRunComparison}
            loading={running}
            disabled={running}
            className="w-full"
            size="lg"
            icon={<Play className="w-5 h-5" />}
          >
            {running ? 'Generating...' : 'Run Preview Comparison'}
          </Button>

          <Button
            onClick={handleReset}
            variant="secondary"
            className="w-full"
            icon={<RotateCcw className="w-4 h-4" />}
          >
            Reset
          </Button>

          {results.length > 0 && (
            <div className="flex gap-2">
              <Button
                onClick={() => handleExport('json')}
                variant="ghost"
                size="sm"
                className="flex-1"
                icon={<Download className="w-4 h-4" />}
              >
                JSON
              </Button>
              <Button
                onClick={() => handleExport('csv')}
                variant="ghost"
                size="sm"
                className="flex-1"
                icon={<Download className="w-4 h-4" />}
              >
                CSV
              </Button>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Cube Preview */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Scrambled Cube</h2>
              {running && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-400">Processing...</span>
                  <Progress value={progress} className="w-32" />
                </div>
              )}
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <RubiksCube3D state={cubeState} className="h-[300px]" />
              <div className="flex flex-col justify-center">
                <CubeNet state={cubeState} size="md" className="mx-auto" />
                {scrambleMoves.length > 0 && (
                  <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
                    <div className="text-sm text-slate-400 mb-1">Scramble ({scrambleMoves.length} moves):</div>
                    <code className="text-xs text-blue-400 font-mono break-all">{formatMoves(scrambleMoves)}</code>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Results */}
          {results.length > 0 && (
            <>
              {/* Result Cards */}
              <div className="grid md:grid-cols-3 gap-4">
                {results.map((result) => {
                  const algo = ALGORITHMS[result.algorithm];

                  return (
                    <Card
                      key={result.algorithm}
                      className={`relative ${!result.solved ? 'opacity-60' : ''}`}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{algo.emoji}</span>
                          <span className="font-bold">{algo.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {result.demoOnly && (
                            <span className="px-2 py-0.5 text-xs bg-amber-500/20 text-amber-300 rounded-full">
                              Demo only
                            </span>
                          )}
                          {result.solved ? (
                            <Check className="w-5 h-5 text-green-400" />
                          ) : (
                            <X className="w-5 h-5 text-red-400" />
                          )}
                        </div>
                      </div>

                      {result.solved ? (
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-slate-400 flex items-center gap-1">
                              <Hash className="w-3 h-3" /> Moves
                            </span>
                            <span className="font-mono">{result.solutionLength}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400 flex items-center gap-1">
                              <Clock className="w-3 h-3" /> Time
                            </span>
                            <span className="font-mono">{formatTime(result.timeMs)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400 flex items-center gap-1">
                              <HardDrive className="w-3 h-3" /> Memory
                            </span>
                            <span className="font-mono">{formatMemory(result.memoryMb)}</span>
                          </div>
                          {(result.backend || result.optimality) && (
                            <div className="pt-2 border-t border-slate-700/50 text-xs text-slate-400">
                              <div>Backend: {result.backend || '-'}</div>
                              <div>Optimality: {result.optimality || '-'}</div>
                              {result.demoOnly && <div>Source: synthetic scramble-inverse preview</div>}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-center text-red-400 py-4">
                          {result.error || 'Failed'}
                        </div>
                      )}

                      {/* Winner badges */}
                      <div className="flex gap-1 mt-4 flex-wrap">
                        {winners?.fastest === result.algorithm && (
                          <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded-full">
                            ⚡ Fastest
                          </span>
                        )}
                        {winners?.fewestMoves === result.algorithm && (
                          <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-400 rounded-full">
                            🎯 Fewest Moves
                          </span>
                        )}
                        {winners?.leastMemory === result.algorithm && (
                          <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-400 rounded-full">
                            💾 Least Memory
                          </span>
                        )}
                      </div>
                    </Card>
                  );
                })}
              </div>

              {/* Detailed Results Table */}
              <Card>
                <h2 className="text-lg font-bold mb-4">Detailed Results</h2>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4 text-slate-400 font-medium">Algorithm</th>
                        <th className="text-center py-3 px-4 text-slate-400 font-medium">Solved</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-medium">Moves</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-medium">Time</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-medium">Memory</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-medium">Nodes</th>
                        <th className="text-left py-3 px-4 text-slate-400 font-medium">Backend</th>
                        <th className="text-left py-3 px-4 text-slate-400 font-medium">Optimality</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((result) => (
                        <tr key={result.algorithm} className="border-b border-slate-700/50">
                          <td className="py-3 px-4">
                            {ALGORITHMS[result.algorithm].emoji} {ALGORITHMS[result.algorithm].name}
                          </td>
                          <td className="text-center py-3 px-4">
                            {result.solved ? (
                              <span className="text-green-400">✓</span>
                            ) : (
                              <span className="text-red-400">✗</span>
                            )}
                          </td>
                          <td className="text-right py-3 px-4 font-mono">
                            {result.solved ? result.solutionLength : '-'}
                          </td>
                          <td className="text-right py-3 px-4 font-mono">
                            {formatTime(result.timeMs)}
                          </td>
                          <td className="text-right py-3 px-4 font-mono">
                            {formatMemory(result.memoryMb)}
                          </td>
                          <td className="text-right py-3 px-4 font-mono text-slate-400">
                            {result.nodesExplored?.toLocaleString() || '-'}
                          </td>
                          <td className="py-3 px-4 text-sm text-slate-300">
                            {result.backend || '-'}
                          </td>
                          <td className="py-3 px-4 text-sm text-slate-300">
                            {result.optimality || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Winner Analysis */}
              {winners && (
                <Card>
                  <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-yellow-400" />
                    Winner Analysis
                  </h2>
                  <div className="grid md:grid-cols-3 gap-4">
                    {winners.fastest && (
                      <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                        <div className="text-sm text-blue-400 mb-1">⚡ Fastest</div>
                        <div className="font-bold">{ALGORITHMS[winners.fastest].name}</div>
                      </div>
                    )}
                    {winners.fewestMoves && (
                      <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                        <div className="text-sm text-green-400 mb-1">🎯 Fewest Moves</div>
                        <div className="font-bold">{ALGORITHMS[winners.fewestMoves].name}</div>
                      </div>
                    )}
                    {winners.leastMemory && (
                      <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                        <div className="text-sm text-purple-400 mb-1">💾 Least Memory</div>
                        <div className="font-bold">{ALGORITHMS[winners.leastMemory].name}</div>
                      </div>
                    )}
                  </div>
                </Card>
              )}

              {/* Solutions */}
              <Card>
                <h2 className="text-lg font-bold mb-4">Preview Sequences</h2>
                <p className="mb-4 text-sm text-slate-400">
                  The sequences below are synthetic preview outputs derived by inverting the scramble. Use the thesis benchmark artifacts for citation or comparison.
                </p>
                <div className="space-y-4">
                  {results.filter(r => r.solved).map((result) => (
                    <details key={result.algorithm} className="group">
                      <summary className="cursor-pointer flex items-center gap-2 p-3 bg-slate-700/30 rounded-lg hover:bg-slate-700/50">
                        <span>{ALGORITHMS[result.algorithm].emoji}</span>
                        <span className="font-medium">{ALGORITHMS[result.algorithm].name}</span>
                        <span className="text-slate-400 ml-auto">{result.solutionLength} moves</span>
                      </summary>
                      <div className="mt-2 p-3 bg-slate-800/50 rounded-lg">
                        <code className="text-sm text-green-400 font-mono break-all">
                          {formatMoves(result.solution)}
                        </code>
                      </div>
                    </details>
                  ))}
                </div>
              </Card>
            </>
          )}

          {/* Empty State */}
          {results.length === 0 && !running && (
            <Card className="text-center py-12">
              <div className="text-4xl mb-4">🧩</div>
              <h3 className="text-xl font-bold mb-2">Ready to Compare Previews</h3>
              <p className="text-slate-400">
                Configure your settings and click "Run Preview Comparison" to inspect all three benchmark profiles
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
