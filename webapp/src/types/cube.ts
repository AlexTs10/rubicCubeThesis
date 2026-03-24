// Cube face colors
export type FaceColor = 'W' | 'Y' | 'R' | 'O' | 'B' | 'G';

// Face positions
export type Face = 'U' | 'D' | 'F' | 'B' | 'L' | 'R';

// Move notation
export type Move =
  | 'R' | "R'" | 'R2'
  | 'L' | "L'" | 'L2'
  | 'U' | "U'" | 'U2'
  | 'D' | "D'" | 'D2'
  | 'F' | "F'" | 'F2'
  | 'B' | "B'" | 'B2';

// Cube state: 6 faces, each with 9 stickers
export type CubeState = {
  [key in Face]: FaceColor[];
};

// Algorithm types
export type Algorithm = 'thistlethwaite' | 'kociemba' | 'korf';

// Algorithm info
export interface AlgorithmInfo {
  name: string;
  fullName: string;
  year: number;
  speed: string;
  moves: string;
  description: string;
  color: string;
  emoji: string;
}

// Solve result
export interface SolveResult {
  algorithm: Algorithm;
  solved: boolean;
  solution: Move[];
  solutionLength: number;
  timeMs: number;
  memoryMb: number;
  nodesExplored?: number;
  backend?: string;
  optimality?: string;
  notes?: string;
  error?: string;
  demoOnly?: boolean;
}

// Comparison result
export interface ComparisonResult {
  scramble: Move[];
  results: SolveResult[];
  timestamp: Date;
}

// Animation state
export interface AnimationState {
  isPlaying: boolean;
  currentMoveIndex: number;
  speed: number;
}

// Cube position for 3D rendering
export interface CubiePosition {
  x: number;
  y: number;
  z: number;
}

// Cubie with position and colors
export interface Cubie {
  position: CubiePosition;
  colors: {
    right?: FaceColor;
    left?: FaceColor;
    top?: FaceColor;
    bottom?: FaceColor;
    front?: FaceColor;
    back?: FaceColor;
  };
}
