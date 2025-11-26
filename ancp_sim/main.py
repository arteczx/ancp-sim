import argparse
import json
from ancp_sim.chemdb import load_ingredients
from ancp_sim.stoichiometry import calculate_stoichiometry
from ancp_sim.thermo import calculate_thermo
from ancp_sim.config import load_config
import ancp_sim.output as output

def apply_catalyst_logic(recipe_composition, config):
    """
    Checks for a catalyst in the recipe and applies a burn rate multiplier if found.
    """
    ferric_oxide_pct = recipe_composition.get("Ferric Oxide", 0.0)
    if ferric_oxide_pct > 1.0:
        multiplier = config.get("catalyst", {}).get("ferric_oxide_multiplier", 1.0)
        original_a = config["burn_rate"]["a"]
        config["burn_rate"]["a"] *= multiplier
        print(f"\n--- Catalyst Logic Applied ---")
        print(f"Ferric Oxide detected at {ferric_oxide_pct}%.")
        print(f"Burn rate coefficient 'a' modified: {original_a} -> {config['burn_rate']['a']}")
        print("----------------------------\n")
    return config

def main():
    parser = argparse.ArgumentParser(description="ANCP-Sim: Ammonium Nitrate Chemical Propulsion Simulator")
    parser.add_argument('recipe_file', type=str, help="Path to the propellant recipe file (e.g., recipe.json)")
    parser.add_argument('--config', type=str, default='config.json', help="Path to the configuration file")
    parser.add_argument('--pc', type=float, default=70.0, help="Chamber pressure in bar")

    args = parser.parse_args()

    output.print_banner()

    # Load configuration
    config = load_config(args.config)
    output.print_inputs(args.config, args.recipe_file, args.pc)

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

    # Apply catalyst logic
    composition = recipe_data.get("composition", {})
    config = apply_catalyst_logic(composition, config)

    # Run calculations and print results
    try:
        # Stoichiometry
        stoichiometry_results = calculate_stoichiometry(composition, ingredients_db)
        output.print_stoichiometry(recipe_data.get('propellant_name', 'N/A'), stoichiometry_results)

        # Thermodynamics
        thermo_results = calculate_thermo(
            composition,
            ingredients_db,
            config,
            chamber_pressure_bar=args.pc
        )
        output.print_thermo(thermo_results)

    except ValueError as e:
        print(f"Error during calculation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
