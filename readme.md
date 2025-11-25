# ANCP-Sim (Ammonium Nitrate Chemical Propulsion Simulator)

ANCP-Sim is a command-line tool for the numerical simulation of solid rocket motors based on Phase-Stabilized Ammonium Nitrate (PSAN) propellants. It provides a foundational framework for analyzing the thermodynamic performance of custom propellant formulations.

## Overview

This simulator is designed to predict the key performance characteristics of a PSAN-based solid rocket motor by modeling its internal ballistics. The current version focuses on the core thermochemical calculations, providing a robust engine for future expansion into grain geometry and transient ballistics simulation.

The project is built with a modular architecture, including:
- **ChemDB:** An external JSON database for storing the properties of propellant ingredients.
- **Stoichiometry Engine:** A flexible calculator for determining the elemental composition and reactant enthalpy of a given propellant recipe.
- **ThermoEngine:** A powerful thermodynamics module that uses the Cantera library to solve for the chemical equilibrium of the combustion products, yielding key performance metrics such as flame temperature, specific impulse (Isp), and characteristic velocity (C*).

## Installation

To set up the simulator, clone the repository and install the required Python packages.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3.  **Install dependencies:**
    Install the required Python packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The simulator is run from the command line, taking a propellant recipe file as input.

### Running a Simulation

To run a simulation, use the following command from the root of the repository:

```bash
python3 -m ancp_sim.main [path/to/your/recipe.json] --pc [chamber_pressure_bar]
```

-   `[path/to/your/recipe.json]`: The path to the JSON file containing the propellant formulation. An example is provided in `data/example_recipe.json`.
-   `--pc [chamber_pressure_bar]`: (Optional) The chamber pressure in bar. Defaults to 70 bar.

### Example

```bash
python3 -m ancp_sim.main data/example_recipe.json --pc 70
```

This will output the stoichiometry and thermodynamic performance results for the propellant defined in the example recipe file.

### Recipe File Format

The recipe file must be a JSON file with the following structure:

```json
{
  "propellant_name": "Your Propellant Name",
  "composition": {
    "Ingredient Name 1": 65.0,
    "Ingredient Name 2": 5.0,
    "Ingredient Name 3": 30.0
  }
}
```

The ingredient names must match the names in `data/ingredients.json`, and the percentages in the `composition` object must sum to 100.
