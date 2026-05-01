# Mechatronic Simulation: Darts Game 301

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
   git clone https://github.com/AgostonPali/Darts-game-HW.git
   ```
2. Navigate into the project directory:
   ```bash
   cd Darts-game-HW
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage and Controls
1. Launch the simulation from your terminal:
   ```bash
   python main.py
   ```
2. **Aiming System:** During the player's turn, the aiming cursors move automatically.
   * **First Left-Click:** Locks the horizontal (X-axis) direction.
   * **Second Left-Click:** Locks the vertical (Y-axis) elevation and throws the dart.
3. **Display Settings:** Press the **F11** key at any time to toggle between Windowed and Fullscreen modes.

## File Structure
*   **`main.py`**: The entry point of the program. Manages the State Machine, the main game loop, event handling, rendering, and physics animation calculations.
*   **`config.py`**: Stores global simulation constants, scaling factors (pixels-to-meters conversion), and the RGBA color palette.
*   **`dartboard.py`**: Handles the geometric construction of the dartboard (sectors, spider wire) and calculates the exact score based on impact coordinates.