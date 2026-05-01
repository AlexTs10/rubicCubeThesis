import { Algorithm, CubeState, Move, SolveResult } from '@/types/cube';
import { applyMoves, isSolved, inverseMoves } from './cube';
import { SOLVED_STATE } from './constants';

// Synthetic demo results. The Next.js frontend is intentionally decoupled from
// the authoritative thesis benchmark pipeline.

function hashString(input: string): number {
  let hash = 2166136261;

  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }

  return hash >>> 0;
}

function createDeterministicRng(...parts: string[]): () => number {
  let state = hashString(parts.join('|')) || 0x6d2b79f5;

  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let value = state;
    value ^= value >>> 15;
    value = Math.imul(value, value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function sampleInRange(rng: () => number, min: number, max: number): number {
  return min + rng() * (max - min);
}

function scrambleSignature(scramble: Move[]): string {
  return scramble.join(' ');
}

function backendInfo(algorithm: Algorithm): Pick<SolveResult, 'backend' | 'optimality' | 'notes'> {
  switch (algorithm) {
    case 'thistlethwaite':
      return {
        backend: 'synthetic scramble-inverse preview',
        optimality: 'not evaluated in preview',
        notes: 'Preview uses the inverse scramble to exercise the UI. It mirrors the pure Thistlethwaite benchmark profile but is not live solver telemetry.',
      };
    case 'kociemba':
      return {
        backend: 'synthetic scramble-inverse preview',
        optimality: 'not evaluated in preview',
        notes: 'Preview uses the inverse scramble to exercise the UI. It mirrors the Kociemba benchmark profile but is not actual two-phase solver output.',
      };
    case 'korf':
      return {
        backend: 'synthetic scramble-inverse preview',
        optimality: 'not evaluated in preview',
        notes: 'Preview uses the inverse scramble to exercise the UI. It mirrors the external exact-backend benchmark profile but does not compute an optimal solution.',
      };
  }
}

function simulateSolveTime(
  algorithm: Algorithm,
  scrambleDepth: number,
  rng: () => number
): number {
  if (algorithm === 'thistlethwaite') {
    if (scrambleDepth <= 5) return Math.round(sampleInRange(rng, 40, 90));
    if (scrambleDepth <= 10) return Math.round(sampleInRange(rng, 700, 1400));
    if (scrambleDepth <= 15) return Math.round(sampleInRange(rng, 1500, 2600));
    return Math.round(sampleInRange(rng, 1400, 2600));
  }

  if (algorithm === 'kociemba') {
    if (scrambleDepth <= 5) return Math.round(sampleInRange(rng, 250, 500));
    if (scrambleDepth <= 10) return Math.round(sampleInRange(rng, 120, 350));
    if (scrambleDepth <= 15) return Math.round(sampleInRange(rng, 6000, 10000));
    return Math.round(sampleInRange(rng, 7000, 12000));
  }

  if (scrambleDepth <= 5) return Math.round(sampleInRange(rng, 1, 5));
  if (scrambleDepth <= 10) return Math.round(sampleInRange(rng, 1, 8));
  if (scrambleDepth <= 15) return Math.round(sampleInRange(rng, 200, 800));
  return Math.round(sampleInRange(rng, 7000, 14000));
}

function simulateMemoryUsage(
  algorithm: Algorithm,
  scrambleDepth: number,
  rng: () => number
): number {
  let value = 0;

  switch (algorithm) {
    case 'thistlethwaite':
      value = sampleInRange(rng, 2.0, 5.0);
      break;
    case 'kociemba':
      value = sampleInRange(rng, 0.5, 2.5);
      break;
    case 'korf':
      if (scrambleDepth <= 10) value = sampleInRange(rng, 1.0, 5.0);
      else if (scrambleDepth <= 15) value = sampleInRange(rng, 80, 180);
      else value = sampleInRange(rng, 180, 360);
      break;
  }

  return Math.round(value * 100) / 100;
}

function simulateNodesExplored(
  algorithm: Algorithm,
  scrambleDepth: number,
  solutionLength: number,
  rng: () => number
): number {
  if (algorithm === 'korf') {
    if (scrambleDepth <= 5) return Math.round(sampleInRange(rng, 20, 120));
    if (scrambleDepth <= 10) return Math.round(sampleInRange(rng, 80, 300));
    if (scrambleDepth <= 15) return Math.round(sampleInRange(rng, 20000, 180000));
    return Math.round(sampleInRange(rng, 2000000, 12000000));
  }

  const multiplier = algorithm === 'thistlethwaite' ? 100 : 500;
  return Math.floor(solutionLength * multiplier * sampleInRange(rng, 0.75, 1.25));
}

// Generate a valid synthetic solution for demo purposes.
function generateDemoSolution(scramble: Move[]): Move[] {
  return inverseMoves(scramble);
}

// Main solve function
export async function solveCube(
  _state: CubeState,
  scramble: Move[],
  algorithm: Algorithm,
  timeout: number = 30000
): Promise<SolveResult> {
  const startTime = performance.now();
  const metadata = backendInfo(algorithm);
  const scrambleState = applyMoves({ ...SOLVED_STATE }, scramble);
  const scrambleKey = scrambleSignature(scramble);
  const solveTimeRng = createDeterministicRng('solve-time', algorithm, scrambleKey);
  const memoryRng = createDeterministicRng('memory', algorithm, scrambleKey);
  const nodesRng = createDeterministicRng('nodes', algorithm, scrambleKey);
  const timeoutRng = createDeterministicRng('timeout', algorithm, scrambleKey);

  // Simulate async solving with timeout
  return new Promise((resolve) => {
    const solveTime = simulateSolveTime(algorithm, scramble.length, solveTimeRng);
    const shouldTimeout =
      algorithm === 'korf' &&
      scramble.length >= 20 &&
      timeout <= 120000 &&
      timeoutRng() < 0.12;

    // Check if it would timeout
    if (solveTime > timeout || shouldTimeout) {
      setTimeout(() => {
        resolve({
          algorithm,
          solved: false,
          solution: [],
          solutionLength: 0,
          timeMs: timeout,
          memoryMb: simulateMemoryUsage(algorithm, scramble.length, memoryRng),
          backend: metadata.backend,
          optimality: metadata.optimality,
          notes: metadata.notes,
          demoOnly: true,
          error: algorithm === 'korf'
            ? 'Synthetic preview timed out on a hard exact-search scenario'
            : 'Synthetic preview exceeded the selected timeout',
        });
      }, Math.min(timeout, 1000)); // Cap actual wait to 1s for demo
      return;
    }

    // Simulate actual solving
    setTimeout(() => {
      const solution = generateDemoSolution(scramble);
      const solvedState = applyMoves(scrambleState, solution);
      const actualTime = performance.now() - startTime;

      if (!isSolved(solvedState)) {
        resolve({
          algorithm,
          solved: false,
          solution: [],
          solutionLength: 0,
          timeMs: Math.max(solveTime, actualTime),
          memoryMb: simulateMemoryUsage(algorithm, scramble.length, memoryRng),
          backend: metadata.backend,
          optimality: metadata.optimality,
          notes: metadata.notes,
          demoOnly: true,
          error: 'Synthetic demo solution failed validation',
        });
        return;
      }

      resolve({
        algorithm,
        solved: true,
        solution,
        solutionLength: solution.length,
        timeMs: Math.max(solveTime, actualTime),
        memoryMb: simulateMemoryUsage(algorithm, scramble.length, memoryRng),
        nodesExplored: simulateNodesExplored(algorithm, scramble.length, solution.length, nodesRng),
        backend: metadata.backend,
        optimality: metadata.optimality,
        notes: metadata.notes,
        demoOnly: true,
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
  // This comparison intentionally reuses the synthetic preview pipeline rather than live solver execution.
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
  const solved = results.filter((r) => r.solved);

  const selectUniqueBest = (selector: (result: SolveResult) => number): Algorithm | null => {
    if (solved.length === 0) {
      return null;
    }

    let bestValue = Number.POSITIVE_INFINITY;
    let bestAlgorithm: Algorithm | null = null;
    let tie = false;

    for (const result of solved) {
      const value = selector(result);

      if (value < bestValue) {
        bestValue = value;
        bestAlgorithm = result.algorithm;
        tie = false;
      } else if (value === bestValue) {
        tie = true;
      }
    }

    return tie ? null : bestAlgorithm;
  };

  return {
    fastest: selectUniqueBest((result) => result.timeMs),
    fewestMoves: selectUniqueBest((result) => result.solutionLength),
    leastMemory: selectUniqueBest((result) => result.memoryMb),
  };
}
