import { CubeState, Face, FaceColor, Move } from '@/types/cube';
import { SOLVED_STATE } from './constants';

// Deep clone a cube state
export function cloneCubeState(state: CubeState): CubeState {
  return {
    U: [...state.U],
    D: [...state.D],
    F: [...state.F],
    B: [...state.B],
    L: [...state.L],
    R: [...state.R],
  };
}

// Rotate a face clockwise
function rotateFaceCW(face: FaceColor[]): FaceColor[] {
  return [
    face[6], face[3], face[0],
    face[7], face[4], face[1],
    face[8], face[5], face[2],
  ];
}

// Rotate a face counter-clockwise
function rotateFaceCCW(face: FaceColor[]): FaceColor[] {
  return [
    face[2], face[5], face[8],
    face[1], face[4], face[7],
    face[0], face[3], face[6],
  ];
}

// Apply a single move to the cube state
export function applyMove(state: CubeState, move: Move): CubeState {
  const newState = cloneCubeState(state);

  switch (move) {
    case 'R':
      newState.R = rotateFaceCW(state.R);
      [newState.F[2], newState.F[5], newState.F[8]] = [state.D[2], state.D[5], state.D[8]];
      [newState.U[2], newState.U[5], newState.U[8]] = [state.F[2], state.F[5], state.F[8]];
      [newState.B[0], newState.B[3], newState.B[6]] = [state.U[8], state.U[5], state.U[2]];
      [newState.D[2], newState.D[5], newState.D[8]] = [state.B[6], state.B[3], state.B[0]];
      break;
    case "R'":
      newState.R = rotateFaceCCW(state.R);
      [newState.F[2], newState.F[5], newState.F[8]] = [state.U[2], state.U[5], state.U[8]];
      [newState.U[2], newState.U[5], newState.U[8]] = [state.B[6], state.B[3], state.B[0]];
      [newState.B[0], newState.B[3], newState.B[6]] = [state.D[8], state.D[5], state.D[2]];
      [newState.D[2], newState.D[5], newState.D[8]] = [state.F[2], state.F[5], state.F[8]];
      break;
    case 'R2':
      return applyMove(applyMove(state, 'R'), 'R');

    case 'L':
      newState.L = rotateFaceCW(state.L);
      [newState.F[0], newState.F[3], newState.F[6]] = [state.U[0], state.U[3], state.U[6]];
      [newState.U[0], newState.U[3], newState.U[6]] = [state.B[8], state.B[5], state.B[2]];
      [newState.B[2], newState.B[5], newState.B[8]] = [state.D[6], state.D[3], state.D[0]];
      [newState.D[0], newState.D[3], newState.D[6]] = [state.F[0], state.F[3], state.F[6]];
      break;
    case "L'":
      newState.L = rotateFaceCCW(state.L);
      [newState.F[0], newState.F[3], newState.F[6]] = [state.D[0], state.D[3], state.D[6]];
      [newState.U[0], newState.U[3], newState.U[6]] = [state.F[0], state.F[3], state.F[6]];
      [newState.B[2], newState.B[5], newState.B[8]] = [state.U[6], state.U[3], state.U[0]];
      [newState.D[0], newState.D[3], newState.D[6]] = [state.B[8], state.B[5], state.B[2]];
      break;
    case 'L2':
      return applyMove(applyMove(state, 'L'), 'L');

    case 'U':
      newState.U = rotateFaceCW(state.U);
      [newState.F[0], newState.F[1], newState.F[2]] = [state.R[0], state.R[1], state.R[2]];
      [newState.L[0], newState.L[1], newState.L[2]] = [state.F[0], state.F[1], state.F[2]];
      [newState.B[0], newState.B[1], newState.B[2]] = [state.L[0], state.L[1], state.L[2]];
      [newState.R[0], newState.R[1], newState.R[2]] = [state.B[0], state.B[1], state.B[2]];
      break;
    case "U'":
      newState.U = rotateFaceCCW(state.U);
      [newState.F[0], newState.F[1], newState.F[2]] = [state.L[0], state.L[1], state.L[2]];
      [newState.L[0], newState.L[1], newState.L[2]] = [state.B[0], state.B[1], state.B[2]];
      [newState.B[0], newState.B[1], newState.B[2]] = [state.R[0], state.R[1], state.R[2]];
      [newState.R[0], newState.R[1], newState.R[2]] = [state.F[0], state.F[1], state.F[2]];
      break;
    case 'U2':
      return applyMove(applyMove(state, 'U'), 'U');

    case 'D':
      newState.D = rotateFaceCW(state.D);
      [newState.F[6], newState.F[7], newState.F[8]] = [state.L[6], state.L[7], state.L[8]];
      [newState.L[6], newState.L[7], newState.L[8]] = [state.B[6], state.B[7], state.B[8]];
      [newState.B[6], newState.B[7], newState.B[8]] = [state.R[6], state.R[7], state.R[8]];
      [newState.R[6], newState.R[7], newState.R[8]] = [state.F[6], state.F[7], state.F[8]];
      break;
    case "D'":
      newState.D = rotateFaceCCW(state.D);
      [newState.F[6], newState.F[7], newState.F[8]] = [state.R[6], state.R[7], state.R[8]];
      [newState.L[6], newState.L[7], newState.L[8]] = [state.F[6], state.F[7], state.F[8]];
      [newState.B[6], newState.B[7], newState.B[8]] = [state.L[6], state.L[7], state.L[8]];
      [newState.R[6], newState.R[7], newState.R[8]] = [state.B[6], state.B[7], state.B[8]];
      break;
    case 'D2':
      return applyMove(applyMove(state, 'D'), 'D');

    case 'F':
      newState.F = rotateFaceCW(state.F);
      [newState.U[6], newState.U[7], newState.U[8]] = [state.L[8], state.L[5], state.L[2]];
      [newState.R[0], newState.R[3], newState.R[6]] = [state.U[6], state.U[7], state.U[8]];
      [newState.D[0], newState.D[1], newState.D[2]] = [state.R[6], state.R[3], state.R[0]];
      [newState.L[2], newState.L[5], newState.L[8]] = [state.D[0], state.D[1], state.D[2]];
      break;
    case "F'":
      newState.F = rotateFaceCCW(state.F);
      [newState.U[6], newState.U[7], newState.U[8]] = [state.R[0], state.R[3], state.R[6]];
      [newState.R[0], newState.R[3], newState.R[6]] = [state.D[2], state.D[1], state.D[0]];
      [newState.D[0], newState.D[1], newState.D[2]] = [state.L[2], state.L[5], state.L[8]];
      [newState.L[2], newState.L[5], newState.L[8]] = [state.U[8], state.U[7], state.U[6]];
      break;
    case 'F2':
      return applyMove(applyMove(state, 'F'), 'F');

    case 'B':
      newState.B = rotateFaceCW(state.B);
      [newState.U[0], newState.U[1], newState.U[2]] = [state.R[2], state.R[5], state.R[8]];
      [newState.R[2], newState.R[5], newState.R[8]] = [state.D[8], state.D[7], state.D[6]];
      [newState.D[6], newState.D[7], newState.D[8]] = [state.L[0], state.L[3], state.L[6]];
      [newState.L[0], newState.L[3], newState.L[6]] = [state.U[2], state.U[1], state.U[0]];
      break;
    case "B'":
      newState.B = rotateFaceCCW(state.B);
      [newState.U[0], newState.U[1], newState.U[2]] = [state.L[6], state.L[3], state.L[0]];
      [newState.R[2], newState.R[5], newState.R[8]] = [state.U[0], state.U[1], state.U[2]];
      [newState.D[6], newState.D[7], newState.D[8]] = [state.R[8], state.R[5], state.R[2]];
      [newState.L[0], newState.L[3], newState.L[6]] = [state.D[6], state.D[7], state.D[8]];
      break;
    case 'B2':
      return applyMove(applyMove(state, 'B'), 'B');
  }

  return newState;
}

// Apply a sequence of moves
export function applyMoves(state: CubeState, moves: Move[]): CubeState {
  return moves.reduce((currentState, move) => applyMove(currentState, move), state);
}

// Check if cube is solved
export function isSolved(state: CubeState): boolean {
  return Object.keys(state).every((face) => {
    const faceState = state[face as Face];
    return faceState.every((color) => color === faceState[0]);
  });
}

// Generate random scramble
export function generateScramble(depth: number, seed?: number): Move[] {
  const moves: Move[] = [];
  const faces: Face[] = ['R', 'L', 'U', 'D', 'F', 'B'];
  const modifiers = ['', "'", '2'];

  // Simple seeded random
  let randomFn = Math.random;
  if (seed !== undefined) {
    let s = seed;
    randomFn = () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
  }

  let lastFace = '';
  let lastLastFace = '';

  for (let i = 0; i < depth; i++) {
    let face: Face;
    do {
      face = faces[Math.floor(randomFn() * faces.length)];
    } while (
      face === lastFace ||
      (face === lastLastFace && isOppositeFace(face, lastFace))
    );

    const modifier = modifiers[Math.floor(randomFn() * modifiers.length)];
    moves.push((face + modifier) as Move);

    lastLastFace = lastFace;
    lastFace = face;
  }

  return moves;
}

// Check if two faces are opposite
function isOppositeFace(face1: string, face2: string): boolean {
  const opposites: Record<string, string> = {
    R: 'L', L: 'R',
    U: 'D', D: 'U',
    F: 'B', B: 'F',
  };
  return opposites[face1] === face2;
}

// Parse move string to Move array
export function parseMoves(moveString: string): Move[] {
  const validMoves = new Set([
    'R', "R'", 'R2', 'L', "L'", 'L2',
    'U', "U'", 'U2', 'D', "D'", 'D2',
    'F', "F'", 'F2', 'B', "B'", 'B2',
  ]);

  // Handle both space-separated and continuous notation
  const normalized = moveString
    .replace(/[']/g, "'") // Normalize apostrophes
    .replace(/2/g, '2 ')   // Add space after 2
    .replace(/'/g, "' ")   // Add space after '
    .split(/\s+/)
    .filter(Boolean);

  const moves: Move[] = [];
  for (const token of normalized) {
    // Try to parse as full move first
    if (validMoves.has(token as Move)) {
      moves.push(token as Move);
    } else if (token.length === 1 && validMoves.has(token as Move)) {
      moves.push(token as Move);
    }
  }

  return moves;
}

// Get inverse of a move
export function inverseMove(move: Move): Move {
  if (move.endsWith('2')) return move;
  if (move.endsWith("'")) return move.slice(0, -1) as Move;
  return (move + "'") as Move;
}

// Get inverse of a move sequence
export function inverseMoves(moves: Move[]): Move[] {
  return [...moves].reverse().map(inverseMove);
}

// Format moves for display
export function formatMoves(moves: Move[]): string {
  return moves.join(' ');
}
