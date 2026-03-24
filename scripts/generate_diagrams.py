#!/usr/bin/env python3
"""
Generate algorithm diagrams for the Rubik's Cube thesis.

Creates conceptual diagrams using matplotlib for:
1. Cube facelet representation
2. Singmaster notation (move notation)
3. Thistlethwaite 4-phase flowchart
4. Kociemba 2-phase flowchart
5. A* vs IDA* comparison
6. Pattern database structure
7. Composite heuristic architecture
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np
from pathlib import Path
import os

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "figures" / "diagrams"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color scheme
COLORS = {
    'U': '#FFFFFF',  # White (top)
    'D': '#FFFF00',  # Yellow (bottom)
    'F': '#00FF00',  # Green (front)
    'B': '#0000FF',  # Blue (back)
    'L': '#FFA500',  # Orange (left)
    'R': '#FF0000',  # Red (right)
    'bg': '#F5F5F5',
    'arrow': '#333333',
    'box': '#E8E8E8',
    'highlight': '#4CAF50',
    'text': '#333333',
}


def save_figure(fig, name):
    """Save figure to output directory."""
    filepath = OUTPUT_DIR / f"{name}.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"  Saved: {filepath}")
    plt.close(fig)


def generate_cube_representation():
    """Generate diagram showing cube facelet numbering."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Unfolded cube view
    ax = axes[0]
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 9.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Cube Facelet Layout (Unfolded)", fontsize=14, fontweight='bold', pad=10)

    # Face positions in unfolded view
    face_positions = {
        'U': (3, 6),  # Top face at position (3,6)
        'L': (0, 3),  # Left
        'F': (3, 3),  # Front
        'R': (6, 3),  # Right
        'B': (9, 3),  # Back
        'D': (3, 0),  # Bottom/Down
    }

    for face, (start_x, start_y) in face_positions.items():
        color = COLORS[face]
        for i in range(3):
            for j in range(3):
                x = start_x + j
                y = start_y + (2 - i)
                idx = i * 3 + j

                rect = Rectangle((x, y), 1, 1,
                                 facecolor=color,
                                 edgecolor='black',
                                 linewidth=1.5)
                ax.add_patch(rect)

                # Add facelet number
                ax.text(x + 0.5, y + 0.5, f'{face}{idx}',
                       ha='center', va='center', fontsize=8, fontweight='bold',
                       color='black' if face in ['U', 'D'] else 'white')

    # Add face labels
    for face, (start_x, start_y) in face_positions.items():
        ax.text(start_x + 1.5, start_y + 3.3, face,
               ha='center', va='center', fontsize=12, fontweight='bold')

    # Right: 3D-ish representation
    ax2 = axes[1]
    ax2.set_xlim(-2, 6)
    ax2.set_ylim(-2, 6)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title("3D Cube View", fontsize=14, fontweight='bold', pad=10)

    # Draw 3D cube (isometric-like)
    # Front face
    for i in range(3):
        for j in range(3):
            x = j * 0.9
            y = (2 - i) * 0.9
            rect = Rectangle((x, y), 0.85, 0.85,
                             facecolor=COLORS['F'], edgecolor='black', linewidth=1)
            ax2.add_patch(rect)

    # Top face (perspective)
    dx, dy = 0.5, 0.5  # Offset for perspective
    for i in range(3):
        for j in range(3):
            x_base = j * 0.9
            y_base = 2.7 + i * 0.45
            points = [
                [x_base + i * dx/3, y_base + i * dy/3],
                [x_base + 0.85 + i * dx/3, y_base + i * dy/3],
                [x_base + 0.85 + (i+1) * dx/3, y_base + dy/3 + i * dy/3],
                [x_base + (i+1) * dx/3, y_base + dy/3 + i * dy/3],
            ]
            poly = plt.Polygon(points, facecolor=COLORS['U'], edgecolor='black', linewidth=1)
            ax2.add_patch(poly)

    # Right face (perspective)
    for i in range(3):
        for j in range(3):
            x_base = 2.7 + j * 0.45
            y_base = (2 - i) * 0.9
            points = [
                [x_base + j * dx/3, y_base + j * dy/3],
                [x_base + dx/3 + j * dx/3, y_base + dy/3 + j * dy/3],
                [x_base + dx/3 + j * dx/3, y_base + 0.85 + dy/3 + j * dy/3],
                [x_base + j * dx/3, y_base + 0.85 + j * dy/3],
            ]
            poly = plt.Polygon(points, facecolor=COLORS['R'], edgecolor='black', linewidth=1)
            ax2.add_patch(poly)

    ax2.text(1.5, -0.8, "Front (F)", ha='center', fontsize=10)
    ax2.text(4, 2, "Right (R)", ha='center', fontsize=10, rotation=-45)
    ax2.text(1.5, 4.5, "Up (U)", ha='center', fontsize=10)

    plt.tight_layout()
    save_figure(fig, "01_cube_representation")


def generate_singmaster_notation():
    """Generate diagram showing Singmaster move notation."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Singmaster Notation - Cube Move Names", fontsize=16, fontweight='bold', pad=20)

    # Draw 6 mini cubes showing each face move
    moves = [
        ('U', 'Up (Top)', 1, 5.5, COLORS['U'], 'Rotate top face 90° clockwise'),
        ('D', 'Down (Bottom)', 5, 5.5, COLORS['D'], 'Rotate bottom face 90° clockwise'),
        ('F', 'Front', 9, 5.5, COLORS['F'], 'Rotate front face 90° clockwise'),
        ('B', 'Back', 1, 2, COLORS['B'], 'Rotate back face 90° clockwise'),
        ('L', 'Left', 5, 2, COLORS['L'], 'Rotate left face 90° clockwise'),
        ('R', 'Right', 9, 2, COLORS['R'], 'Rotate right face 90° clockwise'),
    ]

    for move, name, cx, cy, color, desc in moves:
        # Draw face representation
        size = 1.2
        rect = Rectangle((cx - size/2, cy - size/2), size, size,
                         facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)

        # Add rotation arrow
        from matplotlib.patches import Arc
        arc = Arc((cx, cy), 0.8, 0.8, angle=0, theta1=0, theta2=270,
                 color='black', linewidth=2)
        ax.add_patch(arc)
        # Arrow head
        ax.annotate('', xy=(cx, cy+0.4), xytext=(cx-0.15, cy+0.35),
                   arrowprops=dict(arrowstyle='->', color='black', lw=2))

        # Labels
        ax.text(cx, cy - 1, f"{move}", ha='center', fontsize=16, fontweight='bold')
        ax.text(cx, cy - 1.4, name, ha='center', fontsize=10)
        ax.text(cx, cy - 1.8, desc, ha='center', fontsize=7, style='italic')

    # Add notation explanation
    explanation = """
Move Notation:
  X    = Clockwise 90° (looking at that face)
  X'   = Counter-clockwise 90° (X prime)
  X2   = 180° turn (half turn)

Examples:
  R    = Right face clockwise
  R'   = Right face counter-clockwise
  R2   = Right face 180°
"""
    ax.text(6, 0.2, explanation, ha='center', va='bottom', fontsize=9,
           family='monospace', bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))

    save_figure(fig, "02_singmaster_notation")


def generate_thistlethwaite_flowchart():
    """Generate Thistlethwaite 4-phase algorithm flowchart."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title("Thistlethwaite's Algorithm - Four Phase Reduction",
                fontsize=16, fontweight='bold', pad=20)

    # Phase boxes
    phases = [
        ('G₀', 'All States\n(4.33×10¹⁹)', 0.5, 3, '#FFE4E1'),
        ('G₁', 'Edges Oriented\n(2.11×10¹⁶)', 3.5, 3, '#E1FFE4'),
        ('G₂', 'Corners Oriented\nE-slice in place\n(1.95×10¹⁰)', 6.5, 3, '#E4E1FF'),
        ('G₃', 'Tetrads Formed\nSlices Correct\n(6.63×10⁵)', 9.5, 3, '#FFE4FF'),
        ('G₄', 'Solved\n(1)', 12.5, 3, '#E1FFFF'),
    ]

    box_width = 2.2
    box_height = 1.8

    for name, desc, x, y, color in phases:
        rect = FancyBboxPatch((x - box_width/2, y - box_height/2),
                              box_width, box_height,
                              boxstyle="round,pad=0.05,rounding_size=0.2",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y + 0.3, name, ha='center', va='center', fontsize=14, fontweight='bold')
        ax.text(x, y - 0.4, desc, ha='center', va='center', fontsize=8, linespacing=1.2)

    # Arrows between phases
    arrow_props = dict(arrowstyle='->', color='#333333', lw=2,
                      connectionstyle='arc3,rad=0')

    for i in range(4):
        x1 = phases[i][2] + box_width/2 + 0.1
        x2 = phases[i+1][2] - box_width/2 - 0.1
        y = 3
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                   arrowprops=arrow_props)

    # Phase labels with allowed moves
    phase_info = [
        ('Phase 0\nU,D,F,B,L,R\n(18 moves)', 2, 1),
        ('Phase 1\nU,D,F²,B²,L,R\n(14 moves)', 5, 1),
        ('Phase 2\nU,D,F²,B²,L²,R²\n(10 moves)', 8, 1),
        ('Phase 3\nU²,D²,F²,B²,L²,R²\n(6 moves)', 11, 1),
    ]

    for text, x, y in phase_info:
        ax.text(x, y, text, ha='center', va='center', fontsize=8,
               bbox=dict(boxstyle='round', facecolor='#F0F0F0', edgecolor='gray'))

    # Summary
    ax.text(7, 5.2, "Maximum moves: 7 + 10 + 13 + 15 = 45 (typical) to 52 (worst case)",
           ha='center', fontsize=10, style='italic')

    save_figure(fig, "03_thistlethwaite_flowchart")


def generate_kociemba_flowchart():
    """Generate Kociemba 2-phase algorithm flowchart."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title("Kociemba's Two-Phase Algorithm",
                fontsize=16, fontweight='bold', pad=20)

    # Phase boxes
    phases = [
        ('G₀', 'Scrambled\nState', 1.5, 3, '#FFE4E1'),
        ('G₁', 'Phase 1 Goal\n\nCorners oriented\nEdges oriented\nUD-slice edges\nin UD-slice', 5.5, 3, '#E1FFE4'),
        ('Solved', 'Solved\nState', 10, 3, '#E1FFFF'),
    ]

    box_sizes = [(2.2, 1.5), (3, 2.2), (2.2, 1.5)]

    for (name, desc, x, y, color), (w, h) in zip(phases, box_sizes):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.05,rounding_size=0.2",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y + h/4, name, ha='center', va='center', fontsize=14, fontweight='bold')
        ax.text(x, y - 0.2, desc, ha='center', va='center', fontsize=8, linespacing=1.2)

    # Arrows
    arrow_props = dict(arrowstyle='->', color='#333333', lw=2)
    ax.annotate('', xy=(3.8, 3), xytext=(2.8, 3), arrowprops=arrow_props)
    ax.annotate('', xy=(8.7, 3), xytext=(7.2, 3), arrowprops=arrow_props)

    # Phase labels
    ax.text(3.3, 3.7, 'Phase 1\nU,D,F,B,L,R,U²,D²,F²,B²,L²,R²\n(IDA* search)',
           ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='#F0F0F0'))
    ax.text(8, 3.7, 'Phase 2\nU²,D²,F²,B²,L²,R²\n(IDA* search)',
           ha='center', fontsize=8, bbox=dict(boxstyle='round', facecolor='#F0F0F0'))

    # Key insight
    ax.text(6, 0.8,
           "Key Insight: Phase 1 finds ANY sequence to G₁, then Phase 2 finishes.\n"
           "IDA* with pruning tables makes this very fast (~20 moves average).",
           ha='center', fontsize=9, style='italic',
           bbox=dict(boxstyle='round', facecolor='#FFFFCC', edgecolor='orange'))

    save_figure(fig, "04_kociemba_flowchart")


def generate_astar_comparison():
    """Generate A* vs IDA* comparison diagram."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # A* Tree (left)
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("A* Search", fontsize=14, fontweight='bold')

    # Draw tree structure with "explored" nodes in memory
    def draw_node(ax, x, y, color='white', text=''):
        circle = Circle((x, y), 0.3, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(circle)
        if text:
            ax.text(x, y, text, ha='center', va='center', fontsize=8)

    # A* keeps all nodes in memory
    positions = [
        (5, 7),
        (3, 5.5), (7, 5.5),
        (2, 4), (4, 4), (6, 4), (8, 4),
        (1.5, 2.5), (2.5, 2.5), (3.5, 2.5), (4.5, 2.5), (5.5, 2.5), (6.5, 2.5), (7.5, 2.5), (8.5, 2.5),
    ]

    colors = ['#90EE90', '#90EE90', '#90EE90', '#FFB6C1', '#FFB6C1', '#90EE90', '#FFB6C1',
              '#FFFFCC', '#FFFFCC', '#FFFFCC', '#FFFFCC', '#FFFFCC', '#FFFFCC', '#FFFFCC', '#FFFFCC']

    for (x, y), c in zip(positions, colors):
        draw_node(ax, x, y, c)

    # Draw edges
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6),
             (3, 7), (3, 8), (4, 9), (4, 10), (5, 11), (5, 12), (6, 13), (6, 14)]
    for i, j in edges:
        x1, y1 = positions[i]
        x2, y2 = positions[j]
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1)

    ax.text(5, 0.5, "Memory: O(b^d)\nAll explored nodes stored", ha='center', fontsize=10)

    # Legend
    legend_items = [
        ('#90EE90', 'Explored (in memory)'),
        ('#FFB6C1', 'Pruned (but stored)'),
        ('#FFFFCC', 'Frontier (open list)'),
    ]
    for i, (color, label) in enumerate(legend_items):
        y = 1.5 - i * 0.4
        rect = Rectangle((1, y - 0.15), 0.3, 0.3, facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(1.5, y, label, va='center', fontsize=9)

    # IDA* (right)
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 8)
    ax2.axis('off')
    ax2.set_title("IDA* (Iterative Deepening A*)", fontsize=14, fontweight='bold')

    # IDA* only keeps current path in memory
    current_path_colors = ['#90EE90', '#90EE90', '#FFB6C1', '#90EE90', '#FFB6C1',
                          '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF',
                          '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF']

    for (x, y), c in zip(positions, current_path_colors):
        draw_node(ax2, x, y, c)

    for i, j in edges:
        x1, y1 = positions[i]
        x2, y2 = positions[j]
        ax2.plot([x1, x2], [y1, y2], 'k-', linewidth=1, alpha=0.3)

    # Highlight current path
    current_path = [(0, 1), (1, 4)]
    for i, j in current_path:
        x1, y1 = positions[i]
        x2, y2 = positions[j]
        ax2.plot([x1, x2], [y1, y2], 'g-', linewidth=3)

    ax2.text(5, 0.5, "Memory: O(d)\nOnly current path stored", ha='center', fontsize=10)

    # Legend
    legend_items2 = [
        ('#90EE90', 'Current path'),
        ('#FFB6C1', 'Being explored'),
        ('#FFFFFF', 'Not in memory'),
    ]
    for i, (color, label) in enumerate(legend_items2):
        y = 1.5 - i * 0.4
        rect = Rectangle((1, y - 0.15), 0.3, 0.3, facecolor=color, edgecolor='black')
        ax2.add_patch(rect)
        ax2.text(1.5, y, label, va='center', fontsize=9)

    fig.suptitle("A* vs IDA* Memory Usage", fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_figure(fig, "05_astar_vs_idastar")


def generate_pattern_database():
    """Generate pattern database structure diagram."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title("Pattern Database Structure", fontsize=16, fontweight='bold', pad=20)

    # Cube abstraction
    ax.text(1.5, 7, "Full Cube State", ha='center', fontsize=12, fontweight='bold')
    cube_rect = FancyBboxPatch((0.3, 5.8), 2.4, 1,
                               boxstyle="round,pad=0.05", facecolor='#FFE4E1', edgecolor='black')
    ax.add_patch(cube_rect)
    ax.text(1.5, 6.3, "8 corners × 3 orient\n12 edges × 2 orient\n≈ 4.3×10¹⁹ states",
           ha='center', fontsize=8)

    # Arrow down
    ax.annotate('', xy=(1.5, 5.5), xytext=(1.5, 5.8),
               arrowprops=dict(arrowstyle='->', lw=2))
    ax.text(2.5, 5.6, "Extract pattern", fontsize=9, style='italic')

    # Pattern extraction examples
    patterns = [
        ("Corner Pattern", 3, 4.2, "#E1FFE4", "8! × 3⁷ = 88M states"),
        ("Edge Pattern 1", 6, 4.2, "#E4E1FF", "C(12,6) × 6! × 2⁶ = 42M"),
        ("Edge Pattern 2", 9, 4.2, "#FFE4FF", "C(12,6) × 6! × 2⁶ = 42M"),
    ]

    for name, x, y, color, size in patterns:
        rect = FancyBboxPatch((x-1.3, y-0.5), 2.6, 1.2,
                              boxstyle="round,pad=0.05", facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y + 0.2, name, ha='center', fontsize=10, fontweight='bold')
        ax.text(x, y - 0.2, size, ha='center', fontsize=8)

    # Arrows from cube to patterns
    for x in [3, 6, 9]:
        ax.annotate('', xy=(x, 4.7), xytext=(1.5, 5.5),
                   arrowprops=dict(arrowstyle='->', lw=1.5,
                                  connectionstyle='arc3,rad=-0.2'))

    # Pattern database lookup tables
    ax.text(6, 3.2, "↓ Precomputed BFS from solved state", ha='center', fontsize=10)

    db_y = 2
    for i, (name, x, y, color, _) in enumerate(patterns):
        rect = FancyBboxPatch((x-1.3, db_y-0.5), 2.6, 1,
                              boxstyle="round,pad=0.05", facecolor='#FFFFCC', edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, db_y + 0.2, "Lookup Table", ha='center', fontsize=10, fontweight='bold')
        ax.text(x, db_y - 0.2, "state → min_moves", ha='center', fontsize=8)

        ax.annotate('', xy=(x, db_y + 0.5), xytext=(x, 3.7),
                   arrowprops=dict(arrowstyle='->', lw=1.5))

    # Combined heuristic
    ax.text(6, 0.8, "h(state) = max(corner_db, edge_db1, edge_db2)",
           ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='#90EE90', edgecolor='black'))

    for x in [3, 6, 9]:
        ax.annotate('', xy=(6, 1.1), xytext=(x, 1.5),
                   arrowprops=dict(arrowstyle='->', lw=1.5))

    save_figure(fig, "06_pattern_database")


def generate_composite_heuristic():
    """Generate composite heuristic architecture diagram."""
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_title("Composite Heuristic Architecture\n(Novel Contribution)",
                fontsize=16, fontweight='bold', pad=20)

    # Input cube
    rect = FancyBboxPatch((4.5, 7.2), 3, 1,
                          boxstyle="round,pad=0.05", facecolor='#FFE4E1', edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(6, 7.7, "Cube State", ha='center', fontsize=12, fontweight='bold')

    # Feature extractors
    extractors = [
        ("Corner\nFeatures", 1.5, 5.5, "#E1FFE4"),
        ("Edge\nFeatures", 4.5, 5.5, "#E4E1FF"),
        ("Coordinate\nFeatures", 7.5, 5.5, "#FFE4FF"),
        ("Symmetry\nFeatures", 10.5, 5.5, "#FFFFD0"),
    ]

    for name, x, y, color in extractors:
        rect = FancyBboxPatch((x-1, y-0.6), 2, 1.2,
                              boxstyle="round,pad=0.05", facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

    # Arrows from cube to extractors
    for name, x, y, color in extractors:
        ax.plot([6, x], [7.2, 6.1], 'k-', linewidth=1.5)
        ax.plot([x-0.1, x, x+0.1], [6.2, 6.1, 6.2], 'k-', linewidth=1.5)

    # Individual heuristics
    heuristics = [
        ("Pattern\nDB 1", 1.5, 3.5, "#90EE90"),
        ("Pattern\nDB 2", 4.5, 3.5, "#90EE90"),
        ("Manhattan", 7.5, 3.5, "#87CEEB"),
        ("Neural\nNet", 10.5, 3.5, "#DDA0DD"),
    ]

    for i, (name, x, y, color) in enumerate(heuristics):
        rect = FancyBboxPatch((x-1, y-0.6), 2, 1.2,
                              boxstyle="round,pad=0.05", facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

        # Arrow from extractor
        _, ex, ey, _ = extractors[i]
        ax.plot([ex, x], [ey - 0.6, y + 0.6], 'k-', linewidth=1.5)
        ax.plot([x-0.1, x, x+0.1], [y + 0.7, y + 0.6, y + 0.7], 'k-', linewidth=1.5)

    # Combination layer
    rect = FancyBboxPatch((3.5, 1.5), 5, 1.2,
                          boxstyle="round,pad=0.05", facecolor='#FFD700', edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(6, 2.1, "Combination Strategy", ha='center', fontsize=11, fontweight='bold')
    ax.text(6, 1.7, "max(h1, h2, h3, ...) or weighted sum", ha='center', fontsize=9)

    # Arrows to combination
    for name, x, y, color in heuristics:
        ax.plot([x, 6], [2.9, 2.7], 'k-', linewidth=1.5)

    ax.plot([5.9, 6, 6.1], [2.8, 2.7, 2.8], 'k-', linewidth=1.5)

    # Output
    rect = FancyBboxPatch((4.5, 0), 3, 1,
                          boxstyle="round,pad=0.05", facecolor='#98FB98', edgecolor='black', lw=2)
    ax.add_patch(rect)
    ax.text(6, 0.5, "h(state) <= h*(state)", ha='center', fontsize=11, fontweight='bold')

    ax.plot([6, 6], [1.5, 1], 'k-', linewidth=2)
    ax.plot([5.9, 6, 6.1], [1.1, 1, 1.1], 'k-', linewidth=2)

    # Annotation
    ax.text(0.5, 0.5, "Admissible: never overestimates", fontsize=9, style='italic')

    save_figure(fig, "07_composite_heuristic")


def main():
    """Generate all diagrams."""
    print("Generating thesis diagrams...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    print("1. Generating cube representation...")
    generate_cube_representation()

    print("2. Generating Singmaster notation...")
    generate_singmaster_notation()

    print("3. Generating Thistlethwaite flowchart...")
    generate_thistlethwaite_flowchart()

    print("4. Generating Kociemba flowchart...")
    generate_kociemba_flowchart()

    print("5. Generating A* vs IDA* comparison...")
    generate_astar_comparison()

    print("6. Generating pattern database diagram...")
    generate_pattern_database()

    print("7. Generating composite heuristic diagram...")
    generate_composite_heuristic()

    print()
    print(f"All 7 diagrams generated successfully!")
    print(f"Location: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
