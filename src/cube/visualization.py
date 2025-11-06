"""
Enhanced visualization utilities for Rubik's Cube.

This module provides various ways to visualize cube states:
1. 2D unfolded net (text-based)
2. Colored terminal output (ANSI colors)
3. Compact state representation
4. HTML visualization for notebooks
"""

import numpy as np
from typing import Optional
from enum import Enum
from src.cube.rubik_cube import RubikCube, Face, Color, FACE_COLORS


class DisplayMode(Enum):
    """Display mode options for cube visualization."""
    TEXT = "text"           # Simple text representation
    COLORED = "colored"     # ANSI colored terminal output
    COMPACT = "compact"     # Compact single-line representation
    UNFOLDED = "unfolded"   # 2D unfolded net


# ANSI color codes for terminal output
ANSI_COLORS = {
    'W': '\033[97m',  # Bright white
    'Y': '\033[93m',  # Yellow
    'G': '\033[92m',  # Green
    'B': '\033[94m',  # Blue
    'O': '\033[38;5;208m',  # Orange
    'R': '\033[91m',  # Red
    'RESET': '\033[0m',
    'BG_WHITE': '\033[107m',
    'BG_YELLOW': '\033[103m',
    'BG_GREEN': '\033[102m',
    'BG_BLUE': '\033[104m',
    'BG_ORANGE': '\033[48;5;208m',
    'BG_RED': '\033[101m',
}

# Unicode block characters for colored display
BLOCK = '█'
SMALL_BLOCK = '▪'


def face_to_color_char(face_value: int) -> str:
    """
    Convert a face value to its color character.

    Args:
        face_value: Integer representing the face (0-5)

    Returns:
        Color character (W, Y, G, B, O, R)
    """
    face_enum = Face(face_value)
    color = FACE_COLORS[face_enum]
    return color.value


def get_colored_block(color_char: str, use_background: bool = True) -> str:
    """
    Get a colored block character for terminal display.

    Args:
        color_char: Color character (W, Y, G, B, O, R)
        use_background: If True, use background color with black text

    Returns:
        ANSI-colored string
    """
    if use_background:
        color_map = {
            'W': ANSI_COLORS['BG_WHITE'] + ' W ' + ANSI_COLORS['RESET'],
            'Y': ANSI_COLORS['BG_YELLOW'] + ' Y ' + ANSI_COLORS['RESET'],
            'G': ANSI_COLORS['BG_GREEN'] + ' G ' + ANSI_COLORS['RESET'],
            'B': ANSI_COLORS['BG_BLUE'] + ' B ' + ANSI_COLORS['RESET'],
            'O': ANSI_COLORS['BG_ORANGE'] + ' O ' + ANSI_COLORS['RESET'],
            'R': ANSI_COLORS['BG_RED'] + ' R ' + ANSI_COLORS['RESET'],
        }
    else:
        color_map = {
            'W': ANSI_COLORS['W'] + BLOCK + ANSI_COLORS['RESET'],
            'Y': ANSI_COLORS['Y'] + BLOCK + ANSI_COLORS['RESET'],
            'G': ANSI_COLORS['G'] + BLOCK + ANSI_COLORS['RESET'],
            'B': ANSI_COLORS['B'] + BLOCK + ANSI_COLORS['RESET'],
            'O': ANSI_COLORS['O'] + BLOCK + ANSI_COLORS['RESET'],
            'R': ANSI_COLORS['R'] + BLOCK + ANSI_COLORS['RESET'],
        }

    return color_map.get(color_char, color_char)


def display_cube_unfolded(cube: RubikCube, colored: bool = False) -> str:
    """
    Display cube as an unfolded 2D net.

    Standard unfolded net layout:
            U U U
            U U U
            U U U
        L L L F F F R R R B B B
        L L L F F F R R R B B B
        L L L F F F R R R B B B
            D D D
            D D D
            D D D

    Args:
        cube: RubikCube instance
        colored: If True, use ANSI colors

    Returns:
        String representation of unfolded cube
    """
    lines = []

    # Get face data as color characters
    faces_data = {}
    for face in Face:
        face_state = cube.get_face(face)
        faces_data[face.name] = [face_to_color_char(val) for val in face_state]

    def get_cell(face_name: str, index: int) -> str:
        """Get a single cell, optionally colored."""
        char = faces_data[face_name][index]
        if colored:
            return get_colored_block(char)
        return f' {char} '

    # Top section (U face)
    lines.append("        " + get_cell('U', 0) + get_cell('U', 1) + get_cell('U', 2))
    lines.append("        " + get_cell('U', 3) + get_cell('U', 4) + get_cell('U', 5))
    lines.append("        " + get_cell('U', 6) + get_cell('U', 7) + get_cell('U', 8))

    # Middle section (L F R B)
    for row in range(3):
        line = ""
        line += get_cell('L', row * 3 + 0) + get_cell('L', row * 3 + 1) + get_cell('L', row * 3 + 2)
        line += get_cell('F', row * 3 + 0) + get_cell('F', row * 3 + 1) + get_cell('F', row * 3 + 2)
        line += get_cell('R', row * 3 + 0) + get_cell('R', row * 3 + 1) + get_cell('R', row * 3 + 2)
        line += get_cell('B', row * 3 + 0) + get_cell('B', row * 3 + 1) + get_cell('B', row * 3 + 2)
        lines.append(line)

    # Bottom section (D face)
    lines.append("        " + get_cell('D', 0) + get_cell('D', 1) + get_cell('D', 2))
    lines.append("        " + get_cell('D', 3) + get_cell('D', 4) + get_cell('D', 5))
    lines.append("        " + get_cell('D', 6) + get_cell('D', 7) + get_cell('D', 8))

    return '\n'.join(lines)


def display_cube_compact(cube: RubikCube) -> str:
    """
    Display cube in compact format (one line per face).

    Args:
        cube: RubikCube instance

    Returns:
        Compact string representation
    """
    lines = []
    for face in Face:
        face_state = cube.get_face(face)
        colors = ''.join(face_to_color_char(val) for val in face_state)
        lines.append(f"{face.name}: {colors[:3]} {colors[3:6]} {colors[6:9]}")
    return '\n'.join(lines)


def display_cube_state_vector(cube: RubikCube) -> str:
    """
    Display cube as a single-line state vector.

    Format: UUUUUUUUU-DDDDDDDDD-FFFFFFFFF-BBBBBBBBB-LLLLLLLLL-RRRRRRRRR

    Args:
        cube: RubikCube instance

    Returns:
        Single-line state representation
    """
    parts = []
    for face in Face:
        face_state = cube.get_face(face)
        colors = ''.join(face_to_color_char(val) for val in face_state)
        parts.append(colors)
    return '-'.join(parts)


def print_cube(cube: RubikCube, mode: DisplayMode = DisplayMode.COLORED) -> None:
    """
    Print the cube to console with specified display mode.

    Args:
        cube: RubikCube instance
        mode: Display mode (text, colored, compact, unfolded)
    """
    print("=" * 60)
    print(f"Rubik's Cube State (Solved: {cube.is_solved()})")
    print("=" * 60)

    if mode == DisplayMode.TEXT:
        print(display_cube_unfolded(cube, colored=False))
    elif mode == DisplayMode.COLORED:
        print(display_cube_unfolded(cube, colored=True))
    elif mode == DisplayMode.COMPACT:
        print(display_cube_compact(cube))
    elif mode == DisplayMode.UNFOLDED:
        print(display_cube_unfolded(cube, colored=False))
    else:
        print(str(cube))

    print("=" * 60)


def display_face_grid(cube: RubikCube, face: Face, colored: bool = True) -> str:
    """
    Display a single face as a 3x3 grid.

    Args:
        cube: RubikCube instance
        face: Face to display
        colored: Use ANSI colors

    Returns:
        String representation of the face
    """
    face_state = cube.get_face(face)
    lines = [f"{face.name} Face:"]

    for row in range(3):
        row_str = ""
        for col in range(3):
            index = row * 3 + col
            color_char = face_to_color_char(face_state[index])
            if colored:
                row_str += get_colored_block(color_char)
            else:
                row_str += f" {color_char} "
        lines.append(row_str)

    return '\n'.join(lines)


def compare_cubes(cube1: RubikCube, cube2: RubikCube,
                  labels: tuple = ("Cube 1", "Cube 2")) -> str:
    """
    Display two cubes side by side for comparison.

    Args:
        cube1: First cube
        cube2: Second cube
        labels: Labels for the two cubes

    Returns:
        Side-by-side comparison string
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"{labels[0]:^38} | {labels[1]:^38}")
    lines.append("-" * 80)

    # Get unfolded representations
    unfold1 = display_cube_unfolded(cube1, colored=False).split('\n')
    unfold2 = display_cube_unfolded(cube2, colored=False).split('\n')

    for line1, line2 in zip(unfold1, unfold2):
        lines.append(f"{line1:38} | {line2:38}")

    lines.append("=" * 80)
    return '\n'.join(lines)


def generate_html_visualization(cube: RubikCube) -> str:
    """
    Generate HTML visualization of the cube (for Jupyter notebooks).

    Args:
        cube: RubikCube instance

    Returns:
        HTML string
    """
    color_styles = {
        'W': 'background-color: #FFFFFF; color: #000;',
        'Y': 'background-color: #FFFF00; color: #000;',
        'G': 'background-color: #00FF00; color: #000;',
        'B': 'background-color: #0000FF; color: #FFF;',
        'O': 'background-color: #FF8800; color: #000;',
        'R': 'background-color: #FF0000; color: #FFF;',
    }

    def cell(color_char: str) -> str:
        """Generate HTML for a single cell."""
        style = color_styles[color_char]
        return f'<td style="{style} border: 1px solid #000; width: 30px; height: 30px; text-align: center; font-weight: bold;">{color_char}</td>'

    html = ['<div style="font-family: monospace;">']
    html.append(f'<h3>Rubik\'s Cube (Solved: {cube.is_solved()})</h3>')
    html.append('<table style="border-collapse: collapse; margin: 10px;">')

    # Get face data
    faces_data = {}
    for face in Face:
        face_state = cube.get_face(face)
        faces_data[face.name] = [face_to_color_char(val) for val in face_state]

    # U face (top)
    html.append('<tr><td colspan="3"></td>')
    for i in range(3):
        html.append(cell(faces_data['U'][i]))
    html.append('</tr>')

    html.append('<tr><td colspan="3"></td>')
    for i in range(3, 6):
        html.append(cell(faces_data['U'][i]))
    html.append('</tr>')

    html.append('<tr><td colspan="3"></td>')
    for i in range(6, 9):
        html.append(cell(faces_data['U'][i]))
    html.append('</tr>')

    # L F R B faces (middle)
    for row in range(3):
        html.append('<tr>')
        # L face
        for face_name in ['L', 'F', 'R', 'B']:
            for col in range(3):
                index = row * 3 + col
                html.append(cell(faces_data[face_name][index]))
        html.append('</tr>')

    # D face (bottom)
    for row in range(3):
        html.append('<tr><td colspan="3"></td>')
        for col in range(3):
            index = row * 3 + col
            html.append(cell(faces_data['D'][index]))
        html.append('</tr>')

    html.append('</table>')
    html.append('</div>')

    return ''.join(html)


def display_move_sequence(cube: RubikCube, moves: list,
                         show_intermediate: bool = True) -> None:
    """
    Display cube state after each move in a sequence.

    Args:
        cube: Starting cube state (will be copied, not modified)
        moves: List of moves to apply
        show_intermediate: If True, show state after each move
    """
    current = cube.copy()

    print("=" * 60)
    print("Move Sequence Visualization")
    print("=" * 60)
    print(f"\nStarting State (Solved: {current.is_solved()}):")
    print(display_cube_compact(current))
    print()

    for i, move in enumerate(moves, 1):
        current.apply_move(move)

        if show_intermediate or i == len(moves):
            print(f"After move {i}: {move}")
            print(display_cube_compact(current))
            print()

    print(f"Final State (Solved: {current.is_solved()})")
    print("=" * 60)


# Convenience function for quick display
def show(cube: RubikCube, colored: bool = True) -> None:
    """
    Quick display function for interactive use.

    Args:
        cube: RubikCube instance
        colored: Use colored output
    """
    mode = DisplayMode.COLORED if colored else DisplayMode.TEXT
    print_cube(cube, mode)


if __name__ == '__main__':
    # Demo the visualization module
    print("Visualization Module Demo")
    print("=" * 60)

    # Create and display a solved cube
    cube = RubikCube()
    print("\n1. Solved Cube (Colored):")
    show(cube, colored=True)

    print("\n2. Solved Cube (Text):")
    show(cube, colored=False)

    print("\n3. Compact Display:")
    print(display_cube_compact(cube))

    print("\n4. State Vector:")
    print(display_cube_state_vector(cube))

    # Apply some moves
    cube.apply_move_sequence("R U R' U'")
    print("\n5. After R U R' U' (Colored):")
    show(cube, colored=True)

    # Scramble
    cube = RubikCube()
    cube.scramble(moves=10, seed=42)
    print("\n6. Scrambled Cube:")
    show(cube, colored=True)
