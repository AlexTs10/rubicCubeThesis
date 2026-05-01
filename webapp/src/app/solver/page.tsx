'use client';

import { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Card, MetricCard, AlgorithmCard } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { Slider, Input, Select } from '@/components/ui/Controls';
import CubeNet from '@/components/cube/CubeNet';
import { Play, RotateCcw, Shuffle, Zap, Clock, HardDrive, Hash, ChevronLeft, ChevronRight, Pause } from 'lucide-react';
import { CubeState, Move, Algorithm, SolveResult } from '@/types/cube';
import { ALGORITHMS, SOLVED_STATE } from '@/lib/constants';
import { generateScramble, applyMoves, applyMove, formatMoves, isSolved, parseMoves } from '@/lib/cube';
import { solveCube, formatTime, formatMemory } from '@/lib/solver';

const RubiksCube3D = dynamic(() => import('@/components/cube/RubiksCube3D'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] bg-slate-800/50 rounded-xl flex items-center justify-center">
      <div className="text-slate-400">Loading 3D Cube...</div>
    </div>
  ),
});

type ScrambleMethod = 'random' | 'custom' | 'seeded';

export default function SolverPage() {
  // Cube state
  const [cubeState, setCubeState] = useState<CubeState>(SOLVED_STATE);
  const [scrambleMoves, setScrambleMoves] = useState<Move[]>([]);

  // Scramble settings
  const [scrambleMethod, setScrambleMethod] = useState<ScrambleMethod>('random');
  const [scrambleDepth, setScrambleDepth] = useState(15);
  const [customMoves, setCustomMoves] = useState('');
  const [seed, setSeed] = useState(42);

  // Algorithm settings
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<Algorithm>('kociemba');
  const [timeout, setTimeout] = useState(30);

  // Solve state
  const [solving, setSolving] = useState(false);
  const [solveResult, setSolveResult] = useState<SolveResult | null>(null);

  // Animation state
  const [animationIndex, setAnimationIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const scrambledState = applyMoves({ ...SOLVED_STATE }, scrambleMoves);

  // Generate scramble
  const handleGenerateScramble = useCallback(() => {
    let moves: Move[] = [];

    switch (scrambleMethod) {
      case 'random':
        moves = generateScramble(scrambleDepth);
        break;
      case 'seeded':
        moves = generateScramble(scrambleDepth, seed);
        break;
      case 'custom':
        moves = parseMoves(customMoves);
        break;
    }

    const newState = applyMoves({ ...SOLVED_STATE }, moves);
    setCubeState(newState);
    setScrambleMoves(moves);
    setSolveResult(null);
    setAnimationIndex(0);
  }, [scrambleMethod, scrambleDepth, seed, customMoves]);

  // Reset cube
  const handleReset = useCallback(() => {
    setCubeState({ ...SOLVED_STATE });
    setScrambleMoves([]);
    setSolveResult(null);
    setAnimationIndex(0);
    setIsPlaying(false);
  }, []);

  // Solve cube
  const handleSolve = useCallback(async () => {
    if (isSolved(cubeState)) return;

    setSolving(true);
    setSolveResult(null);

    try {
      const result = await solveCube(scrambledState, scrambleMoves, selectedAlgorithm, timeout * 1000);
      setSolveResult(result);
      setAnimationIndex(0);
    } catch (error) {
      console.error('Solve error:', error);
    } finally {
      setSolving(false);
    }
  }, [cubeState, scrambleMoves, scrambledState, selectedAlgorithm, timeout]);

  // Animation controls
  const handleAnimationStep = useCallback((direction: 'prev' | 'next') => {
    if (!solveResult?.solution) return;

    if (direction === 'next' && animationIndex < solveResult.solution.length) {
      const partialSolution = solveResult.solution.slice(0, animationIndex + 1);
      setCubeState(applyMoves(scrambledState, partialSolution));
      setAnimationIndex((currentIndex) => currentIndex + 1);
    } else if (direction === 'prev' && animationIndex > 0) {
      const partialSolution = solveResult.solution.slice(0, animationIndex - 1);
      setCubeState(applyMoves(scrambledState, partialSolution));
      setAnimationIndex((currentIndex) => currentIndex - 1);
    }
  }, [solveResult, animationIndex, scrambledState]);

  const handleSliderChange = useCallback((value: number) => {
    if (!solveResult?.solution) return;

    const partialSolution = solveResult.solution.slice(0, value);
    setCubeState(applyMoves(scrambledState, partialSolution));
    setAnimationIndex(value);
  }, [solveResult, scrambledState]);

  const cubeIsSolved = isSolved(cubeState);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">Single Solver</span>
        </h1>
        <p className="text-slate-400">Preview individual algorithm benchmark profiles on scrambled cubes</p>
        <p className="text-sm text-slate-500 mt-2">
          This page mirrors the corrected thesis benchmark profile, but it does not execute the repository solvers. Every result here is synthetic preview data.
        </p>
        <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-100">
          This Next.js page generates a valid preview sequence by inverting the scramble. It is
          useful for UI demos only and should not be cited as benchmark evidence, solver
          telemetry, or an optimality claim. For authoritative live solver execution, use the
          Streamlit UI in <code>ui/</code>.
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column - Controls */}
        <div className="space-y-6">
          {/* Algorithm Selection */}
          <Card>
            <h2 className="text-lg font-bold mb-4">Select Algorithm</h2>
            <div className="space-y-3">
              {(Object.keys(ALGORITHMS) as Algorithm[]).map((algo) => (
                <AlgorithmCard
                  key={algo}
                  name={ALGORITHMS[algo].name}
                  emoji={ALGORITHMS[algo].emoji}
                  speed={ALGORITHMS[algo].speed}
                  moves={ALGORITHMS[algo].moves}
                  description={ALGORITHMS[algo].description}
                  color={algo === 'thistlethwaite' ? 'yellow' : algo === 'kociemba' ? 'blue' : 'purple'}
                  isSelected={selectedAlgorithm === algo}
                  onClick={() => setSelectedAlgorithm(algo)}
                />
              ))}
            </div>
          </Card>

          {/* Scramble Settings */}
          <Card>
            <h2 className="text-lg font-bold mb-4">Scramble Settings</h2>

            <Select
              label="Scramble Method"
              value={scrambleMethod}
              onChange={(value) => setScrambleMethod(value as ScrambleMethod)}
              options={[
                { value: 'random', label: 'Random' },
                { value: 'seeded', label: 'Seeded Random' },
                { value: 'custom', label: 'Custom Moves' },
              ]}
              className="mb-4"
            />

            {scrambleMethod !== 'custom' && (
              <Slider
                label="Scramble Depth"
                value={scrambleDepth}
                onChange={setScrambleDepth}
                min={5}
                max={25}
                className="mb-4"
              />
            )}

            {scrambleMethod === 'seeded' && (
              <Input
                label="Random Seed"
                type="number"
                value={seed.toString()}
                onChange={(v) => setSeed(parseInt(v) || 0)}
                className="mb-4"
              />
            )}

            {scrambleMethod === 'custom' && (
              <Input
                label="Move Sequence"
                placeholder="e.g., R U R' U' F2"
                value={customMoves}
                onChange={setCustomMoves}
                className="mb-4"
              />
            )}

            <Slider
              label="Timeout (seconds)"
              value={timeout}
              onChange={setTimeout}
              min={5}
              max={120}
              className="mb-4"
            />

            <div className="flex gap-2">
              <Button
                onClick={handleGenerateScramble}
                variant="secondary"
                className="flex-1"
                icon={<Shuffle className="w-4 h-4" />}
              >
                Scramble
              </Button>
              <Button
                onClick={handleReset}
                variant="ghost"
                icon={<RotateCcw className="w-4 h-4" />}
              >
                Reset
              </Button>
            </div>
          </Card>
        </div>

        {/* Middle Column - 3D Cube */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="relative">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Cube State</h2>
              <span className={`px-3 py-1 rounded-full text-sm ${cubeIsSolved ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                {cubeIsSolved ? '✓ Solved' : 'Scrambled'}
              </span>
            </div>

            <RubiksCube3D
              state={cubeState}
              className="w-full h-[400px]"
            />

            {/* Scramble Display */}
            {scrambleMoves.length > 0 && (
              <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
                <div className="text-sm text-slate-400 mb-1">Scramble ({scrambleMoves.length} moves):</div>
                <code className="text-sm text-blue-400 font-mono">{formatMoves(scrambleMoves)}</code>
              </div>
            )}

            {/* Solve Button */}
            <Button
              onClick={handleSolve}
              loading={solving}
              disabled={cubeIsSolved || solving}
              className="w-full mt-4"
              size="lg"
              icon={<Play className="w-5 h-5" />}
            >
              {solving ? 'Generating preview...' : `Preview ${ALGORITHMS[selectedAlgorithm].name}`}
            </Button>
          </Card>

          {/* Solution Results */}
          {solveResult && (
            <Card>
              <h2 className="text-lg font-bold mb-4">Preview Results</h2>

              {solveResult.demoOnly && (
                <div className="mb-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-100">
                  Synthetic preview only. The sequence below is the inverse scramble used to exercise the UI and is not thesis evidence.
                </div>
              )}

              {solveResult.solved ? (
                <>
                  {/* Metrics */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                    <MetricCard
                      label="Algorithm"
                      value={ALGORITHMS[solveResult.algorithm].name}
                      color={solveResult.algorithm === 'thistlethwaite' ? 'yellow' : solveResult.algorithm === 'kociemba' ? 'blue' : 'purple'}
                      icon={<Zap className="w-4 h-4" />}
                    />
                    <MetricCard
                      label="Moves"
                      value={solveResult.solutionLength}
                      color="green"
                      icon={<Hash className="w-4 h-4" />}
                    />
                    <MetricCard
                      label="Time"
                      value={formatTime(solveResult.timeMs)}
                      color="blue"
                      icon={<Clock className="w-4 h-4" />}
                    />
                    <MetricCard
                      label="Memory"
                      value={formatMemory(solveResult.memoryMb)}
                      color="purple"
                      icon={<HardDrive className="w-4 h-4" />}
                    />
                  </div>

                  {(solveResult.backend || solveResult.optimality || solveResult.notes) && (
                    <div className="mb-6 p-4 bg-slate-700/30 rounded-lg text-sm text-slate-300 space-y-1">
                      <div><span className="text-slate-400">Backend:</span> {solveResult.backend || '-'}</div>
                      <div><span className="text-slate-400">Optimality:</span> {solveResult.optimality || '-'}</div>
                      {solveResult.notes && (
                        <div><span className="text-slate-400">Notes:</span> {solveResult.notes}</div>
                      )}
                    </div>
                  )}

                  {/* Solution Animation */}
                  <div className="p-4 bg-slate-700/30 rounded-lg mb-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm text-slate-400">Solution Animation</span>
                      <span className="text-sm font-mono text-blue-400">
                        {animationIndex} / {solveResult.solution.length}
                      </span>
                    </div>

                    <Slider
                      label=""
                      value={animationIndex}
                      onChange={handleSliderChange}
                      min={0}
                      max={solveResult.solution.length}
                    />

                    <div className="flex justify-center gap-2 mt-3">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleSliderChange(0)}
                        disabled={animationIndex === 0}
                      >
                        ⏮ Start
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleAnimationStep('prev')}
                        disabled={animationIndex === 0}
                        icon={<ChevronLeft className="w-4 h-4" />}
                      >
                        Prev
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleAnimationStep('next')}
                        disabled={animationIndex === solveResult.solution.length}
                        icon={<ChevronRight className="w-4 h-4" />}
                      >
                        Next
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleSliderChange(solveResult.solution.length)}
                        disabled={animationIndex === solveResult.solution.length}
                      >
                        End ⏭
                      </Button>
                    </div>

                    {animationIndex < solveResult.solution.length && (
                      <div className="text-center mt-3 text-sm">
                        Next move: <span className="font-mono text-yellow-400 px-2 py-1 bg-slate-700 rounded">
                          {solveResult.solution[animationIndex]}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Full Solution */}
                  <details className="group">
                    <summary className="cursor-pointer text-sm text-slate-400 hover:text-white">
                      View full solution
                    </summary>
                    <div className="mt-2 p-3 bg-slate-700/50 rounded-lg">
                      <code className="text-sm text-green-400 font-mono break-all">
                        {formatMoves(solveResult.solution)}
                      </code>
                    </div>
                  </details>
                </>
              ) : (
                <div className="text-center py-8">
                  <div className="text-red-400 text-lg mb-2">❌ Preview Failed</div>
                  <p className="text-slate-400">{solveResult.error || 'Unknown error'}</p>
                </div>
              )}
            </Card>
          )}

          {/* 2D Net View */}
          <Card>
            <h2 className="text-lg font-bold mb-4">2D Net View</h2>
            <div className="flex justify-center">
              <CubeNet state={cubeState} size="lg" />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
