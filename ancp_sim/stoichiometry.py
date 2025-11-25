import re
import json
from ancp_sim.chemdb import load_ingredients

def parse_formula(formula):
    """
    Parses a chemical formula string and returns a dictionary of element counts.

    Args:
        formula (str): A string representing a chemical formula (e.g., 'H2O', 'C6H12O6').

    Returns:
        dict: A dictionary where keys are element symbols and values are their counts.
    """
    pattern = r'([A-Z][a-z]*)(\d*)'
    matches = re.findall(pattern, formula)

    element_counts = {}
    for element, count in matches:
        count = int(count) if count else 1
        element_counts[element] = element_counts.get(element, 0) + count

    return element_counts

def calculate_stoichiometry(recipe, ingredients_db):
    """
    Calculates the stoichiometry for a given propellant recipe.

    Args:
        recipe (dict): A dictionary with ingredient names as keys and their mass percentages as values.
        ingredients_db (dict): The chemical database loaded from JSON.

    Returns:
        dict: A dictionary containing the calculated stoichiometric properties.
    """
    total_moles_elements = {}
    total_enthalpy = 0
    total_mass = 0

    for ingredient_name, percentage in recipe.items():
        if ingredient_name not in ingredients_db:
            raise ValueError(f"Ingredient '{ingredient_name}' not found in the database.")

        ingredient_data = ingredients_db[ingredient_name]
        formula = ingredient_data['formula']
        molecular_weight = ingredient_data['molecular_weight_g_mol']
        enthalpy_formation = ingredient_data['enthalpy_formation_kJ_mol']

        # Mass of the ingredient in a 100g sample of propellant
        mass = percentage
        total_mass += mass

        # Moles of the ingredient
        moles_ingredient = mass / molecular_weight

        # Total enthalpy of reactants
        total_enthalpy += moles_ingredient * enthalpy_formation

        # Elemental composition
        element_counts = parse_formula(formula)
        for element, count in element_counts.items():
            total_moles_elements[element] = total_moles_elements.get(element, 0) + (moles_ingredient * count)

    if abs(total_mass - 100.0) > 1e-6:
        print(f"Warning: The sum of recipe percentages is {total_mass}%, not 100%.")

    # Oxygen Balance Calculation
    # OB% = (O - 2*C - H/2 - 2*Mg) * 16 / MW_total * 100
    # For simplicity, we'll calculate based on elemental moles first.

    element_moles = total_moles_elements
    o_moles = element_moles.get('O', 0)
    c_moles = element_moles.get('C', 0)
    h_moles = element_moles.get('H', 0)
    mg_moles = element_moles.get('Mg', 0)

    # This is a simplified oxygen balance calculation.
    # A more complete one would consider all oxidizable elements.
    oxygen_needed = (2 * c_moles) + (h_moles / 2) + (2 * mg_moles)
    oxygen_balance_moles = o_moles - oxygen_needed

    # Convert oxygen balance to percentage by weight
    oxygen_balance_grams = oxygen_balance_moles * 15.999 # Atomic weight of Oxygen
    oxygen_balance_percent = (oxygen_balance_grams / 100.0) * 100.0 # Assuming 100g total mass

    return {
        'elemental_moles': total_moles_elements,
        'reactant_enthalpy_kJ_100g': total_enthalpy,
        'oxygen_balance_percent': oxygen_balance_percent
    }

if __name__ == '__main__':
    # Example Usage
    db = load_ingredients('../../data/ingredients.json')

    # A sample recipe
    example_recipe = {
        "Ammonium Nitrate": 70.0,
        "Magnesium": 20.0,
        "Castor Oil": 5.0,
        "Methylene Diphenyl Diisocyanate": 5.0
    }

    if db:
        stoichiometry_results = calculate_stoichiometry(example_recipe, db)
        print("Stoichiometry Results:")
        print(json.dumps(stoichiometry_results, indent=2))
