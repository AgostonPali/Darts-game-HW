# Mechatronikai szimuláció: Darts game

## Project Description
This project is a 2D, physics-based darts simulator developed for a university mechatronic simulation assignment. The program utilizes the kinematic equations of projectile motion to calculate the dart's flight trajectory based on the user's horizontal and vertical aiming inputs.

## Core Features and Technical Details
*   **Physics-Based Ballistic Model:** Simulates the dart's flight path using projectile motion equations. The dart's visual pitch angle dynamically aligns with the tangent of its flight parabola.
*   **Standard 301 Game Mode:** Features an accurate scoring algorithm (sectors, doubles, triples, bullseye) that fully implements the "Bust" (overthrow) rule.
*   **Player vs. Computer (PvE):** Includes an automated AI opponent with randomized error margins and built-in decision delays for a realistic pacing.
*   **Responsive Graphics Engine:** Supports distortion-free fullscreen scaling, dynamic drop shadows, a particle system for impact sparks, and modern UI components.

## Installation
A Python 3.x environment is required to run the simulation.

1. Clone the repository to your local machine:
   ```bash
   git clone <repo-url>