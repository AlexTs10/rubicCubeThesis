import { Algorithm, AlgorithmInfo, CubeState, FaceColor } from '@/types/cube';

// Color mapping for rendering
export const COLOR_MAP: Record<FaceColor, string> = {
  W: '#FFFFFF', // White
  Y: '#FFD500', // Yellow
  R: '#B71234', // Red
  O: '#FF5800', // Orange
  B: '#0046AD', // Blue
  G: '#009B48', // Green
};

// Initial solved cube state
export const SOLVED_STATE: CubeState = {
  U: ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'], // White top
  D: ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'], // Yellow bottom
  F: ['G', 'G', 'G', 'G', 'G', 'G', 'G', 'G', 'G'], // Green front
  B: ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'], // Blue back
  L: ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], // Orange left
  R: ['R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'], // Red right
};

// Algorithm information
export const ALGORITHMS: Record<Algorithm, AlgorithmInfo> = {
  thistlethwaite: {
    name: 'Thistlethwaite',
    fullName: "Thistlethwaite's Algorithm",
    year: 1981,
    speed: '0.2-0.5s',
    moves: '30-52',
    description: '4-phase group theory approach. Fast execution, longer solutions.',
    color: 'yellow',
    emoji: '⚡',
  },
  kociemba: {
    name: 'Kociemba',
    fullName: "Kociemba's Two-Phase Algorithm",
    year: 1992,
    speed: '1-3s',
    moves: '<19',
    description: '2-phase IDA* search. Balanced speed and solution length.',
    color: 'blue',
    emoji: '🚀',
  },
  korf: {
    name: 'Korf IDA*',
    fullName: "Korf's IDA* with Pattern Databases",
    year: 1997,
    speed: '1-30s',
    moves: '≤20',
    description: 'Pattern database heuristics. Optimal solutions, variable time.',
    color: 'purple',
    emoji: '🐢',
  },
};

// All possible moves
export const ALL_MOVES = [
  'R', "R'", 'R2',
  'L', "L'", 'L2',
  'U', "U'", 'U2',
  'D', "D'", 'D2',
  'F', "F'", 'F2',
  'B', "B'", 'B2',
] as const;

// Navigation items
export const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: 'Home' },
  { href: '/solver', label: 'Single Solver', icon: 'Target' },
  { href: '/comparison', label: 'Comparison', icon: 'Scale' },
  { href: '/educational', label: 'Educational', icon: 'GraduationCap' },
];

// Educational content sections
export const EDUCATIONAL_TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'thistlethwaite', label: 'Thistlethwaite' },
  { id: 'kociemba', label: 'Kociemba' },
  { id: 'korf', label: 'Korf IDA*' },
  { id: 'glossary', label: 'Glossary' },
];

// Glossary terms
export const GLOSSARY_TERMS = [
  { term: 'Cubie', definition: 'One of the 26 visible pieces of a Rubik\'s Cube (8 corners, 12 edges, 6 centers).' },
  { term: 'Face', definition: 'One of the 6 sides of the cube: Up (U), Down (D), Front (F), Back (B), Left (L), Right (R).' },
  { term: 'Sticker', definition: 'The colored square on each visible face of a cubie.' },
  { term: 'God\'s Number', definition: 'The minimum number of moves needed to solve any cube configuration (proven to be 20 in HTM).' },
  { term: 'HTM', definition: 'Half-Turn Metric - counts 180° turns as one move.' },
  { term: 'QTM', definition: 'Quarter-Turn Metric - counts only 90° turns, 180° = 2 moves.' },
  { term: 'IDA*', definition: 'Iterative Deepening A* - search algorithm combining depth-first search with heuristic guidance.' },
  { term: 'Heuristic', definition: 'A function estimating the cost to reach the goal. Must be admissible (never overestimate) for optimal solutions.' },
  { term: 'Pattern Database', definition: 'Precomputed lookup table storing optimal solutions for partial cube states.' },
  { term: 'Pruning Table', definition: 'Table used to eliminate search branches that cannot lead to solutions.' },
  { term: 'Group Theory', definition: 'Mathematical framework treating cube moves as elements of a permutation group.' },
  { term: 'Subgroup', definition: 'A subset of moves that forms a complete group. Thistlethwaite uses nested subgroups: G₀ ⊃ G₁ ⊃ G₂ ⊃ G₃.' },
  { term: 'Coordinate', definition: 'A number encoding a specific aspect of cube state (e.g., corner orientation, edge permutation).' },
  { term: 'Move Table', definition: 'Precomputed table showing how coordinates change under each move.' },
  { term: 'Admissible Heuristic', definition: 'A heuristic that never overestimates the actual cost, guaranteeing optimal solutions.' },
];
