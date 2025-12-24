import { Algorithm, CubeState, Move, SolveResult } from '@/types/cube';
import { applyMoves, generateScramble, isSolved, inverseMoves } from './cube';
import { SOLVED_STATE } from './constants';

// Simulated solver results (in a real app, this would call a backend API)
// This provides realistic-looking demo data

function simulateSolveTime(algorithm: Algorithm, scrambleDepth: number): number {
  const baseTime = {
    thistlethwaite: 200,
    kociemba: 1500,
    korf: 5000,
  }[algorithm];

  // Add some randomness based on scramble depth
  const variance = Math.random() * 0.5 + 0.75;
  const depthFactor = 1 + (scrambleDepth - 10) * 0.05;

  return Math.round(baseTime * variance * depthFactor);
}

function simulateSolutionLength(algorithm: Algorithm): number {
  switch (algorithm) {
    case 'thistlethwaite':
      return Math.floor(Math.random() * 23) + 30; // 30-52
    case 'kociemba':
      return Math.floor(Math.random() * 5) + 15; // 15-19
    case 'korf':
      return Math.floor(Math.random() * 5) + 16; // 16-20
  }
}

function simulateMemoryUsage(algorithm: Algorithm): number {
  const baseMem = {
    thistlethwaite: 25,
    kociemba: 80,
    korf: 150,
  }[algorithm];

  return Math.round((baseMem + Math.random() * 20) * 100) / 100;
}

function simulateNodesExplored(algorithm: Algorithm, solutionLength: number): number {
  const multiplier = {
    thistlethwaite: 100,
    kociemba: 500,
    korf: 2000,
  }[algorithm];

  return Math.floor(solutionLength * multiplier * (Math.random() * 0.5 + 0.75));
}

// Generate a plausible solution (for demo purposes)
function generateDemoSolution(scramble: Move[], algorithm: Algorithm): Move[] {
  const length = simulateSolutionLength(algorithm);

  // For demo: just generate random moves of appropriate length
  // In real app, this would be actual solver output
  return generateScramble(length);
}

// Main solve function
export async function solveCube(
  state: CubeState,
  scramble: Move[],
  algorithm: Algorithm,
  timeout: number = 30000
): Promise<SolveResult> {
  const startTime = performance.now();

  // Simulate async solving with timeout
  return new Promise((resolve) => {
    const solveTime = simulateSolveTime(algorithm, scramble.length);

    // Check if it would timeout
    if (solveTime > timeout) {
      setTimeout(() => {
        resolve({
          algorithm,
          solved: false,
          solution: [],
          solutionLength: 0,
          timeMs: timeout,
          memoryMb: simulateMemoryUsage(algorithm),
          error: 'Timeout exceeded',
        });
      }, Math.min(timeout, 1000)); // Cap actual wait to 1s for demo
      return;
    }

    // Simulate actual solving
    setTimeout(() => {
      const solution = generateDemoSolution(scramble, algorithm);
      const actualTime = performance.now() - startTime;

      resolve({
        algorithm,
        solved: true,
        solution,
        solutionLength: solution.length,
        timeMs: Math.max(solveTime, actualTime),
        memoryMb: simulateMemoryUsage(algorithm),
        nodesExplored: simulateNodesExplored(algorithm, solution.length),
      });
    }, Math.min(solveTime / 10, 500)); // Speed up for demo
  });
}

// Compare all algorithms
export async function compareAlgorithms(
  scramble: Move[],
  timeouts: Record<Algorithm, number> = {
    thistlethwaite: 10000,
    kociemba: 30000,
    korf: 60000,
  }
): Promise<SolveResult[]> {
  const state = applyMoves({ ...SOLVED_STATE }, scramble);

  const results = await Promise.all([
    solveCube(state, scramble, 'thistlethwaite', timeouts.thistlethwaite),
    solveCube(state, scramble, 'kociemba', timeouts.kociemba),
    solveCube(state, scramble, 'korf', timeouts.korf),
  ]);

  return results;
}

// Format time for display
export function formatTime(ms: number): string {
  if (ms < 1000) {
    return `${ms.toFixed(0)}ms`;
  }
  return `${(ms / 1000).toFixed(2)}s`;
}

// Format memory for display
export function formatMemory(mb: number): string {
  if (mb < 1) {
    return `${(mb * 1024).toFixed(0)} KB`;
  }
  return `${mb.toFixed(1)} MB`;
}

// Get winner analysis
export function analyzeResults(results: SolveResult[]): {
  fastest: Algorithm | null;
  fewestMoves: Algorithm | null;
  leastMemory: Algorithm | null;
} {
  const solved = results.filter(r => r.solved);

  if (solved.length === 0) {
    return { fastest: null, fewestMoves: null, leastMemory: null };
  }

  const fastest = solved.reduce((a, b) => a.timeMs < b.timeMs ? a : b);
  const fewestMoves = solved.reduce((a, b) => a.solutionLength < b.solutionLength ? a : b);
  const leastMemory = solved.reduce((a, b) => a.memoryMb < b.memoryMb ? a : b);

  return {
    fastest: fastest.algorithm,
    fewestMoves: fewestMoves.algorithm,
    leastMemory: leastMemory.algorithm,
  };
}
