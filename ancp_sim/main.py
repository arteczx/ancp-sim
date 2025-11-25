import argparse
import json
from ancp_sim.chemdb import load_ingredients
from ancp_sim.stoichiometry import calculate_stoichiometry
from ancp_sim.thermo import calculate_thermo
from ancp_sim.config import load_config

def main():
    parser = argparse.ArgumentParser(description="ANCP-Sim: Ammonium Nitrate Chemical Propulsion Simulator")
    parser.add_argument('recipe_file', type=str, help="Path to the propellant recipe file (e.g., recipe.json)")
    parser.add_argument('--config', type=str, default='config.ini', help="Path to the configuration file")
    parser.add_argument('--pc', type=float, default=70.0, help="Chamber pressure in bar")

    args = parser.parse_args()

    print("--- ANCP-Sim Initialized ---")

    # Load configuration
    config = load_config(args.config)
    print(f"Loaded configuration from: {args.config}")
    for section in config.sections():
        print(f"[{section}]")
        for key, val in config.items(section):
            print(f"  {key} = {val}")

    print(f"Recipe File: {args.recipe_file}")
    print(f"Chamber Pressure: {args.pc} bar")
    print("----------------------------")

    # Load the chemical database
    ingredients_db = load_ingredients()
    if not ingredients_db:
        return

    # Load the recipe
    try:
        with open(args.recipe_file, 'r') as f:
            recipe_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The recipe file {args.recipe_file} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The recipe file {args.recipe_file} is not a valid JSON file.")
        return

    # Calculate stoichiometry
    try:
        composition = recipe_data.get("composition", {})
        stoichiometry_results = calculate_stoichiometry(composition, ingredients_db)

        print("\n--- Stoichiometry Results ---")
        print(f"Propellant: {recipe_data.get('propellant_name', 'N/A')}")
        print(json.dumps(stoichiometry_results, indent=2))
        print("-----------------------------\n")

        # Calculate thermodynamics
        thermo_results = calculate_thermo(
            composition,
            ingredients_db,
            chamber_pressure_bar=args.pc
        )

        print("\n--- Thermodynamic Results (Cantera) ---")
        print(json.dumps(thermo_results, indent=2))
        print("---------------------------------------\n")

    except ValueError as e:
        print(f"Error during calculation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
