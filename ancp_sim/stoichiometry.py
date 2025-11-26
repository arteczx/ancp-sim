import re
import json
from .chemdb import load_ingredients

def parse_formula(formula):
    """
    Parses a chemical formula string, including those with parentheses,
    and returns a dictionary of element counts.
    """
    # Regex to find elements, numbers, parentheses
    tokens = re.findall(r'([A-Z][a-z]*)(\d*)|(\()|(\))(\d*)', formula)

    # Stack-based processing
    stack = [{}]
    for element, num, l_paren, r_paren, r_num in tokens:
        if element: # An element and its count
            count = int(num) if num else 1
            stack[-1][element] = stack[-1].get(element, 0) + count
        elif l_paren: # A left parenthesis
            stack.append({})
        elif r_paren: # A right parenthesis and its multiplier
            multiplier = int(r_num) if r_num else 1
            top = stack.pop()
            for elem, count in top.items():
                stack[-1][elem] = stack[-1].get(elem, 0) + count * multiplier

    return stack[0]

def calculate_stoichiometry(recipe, ingredients_db):
    """
    Calculates the stoichiometry for a given propellant recipe.
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

        mass = percentage
        total_mass += mass

        moles_ingredient = mass / molecular_weight
        total_enthalpy += moles_ingredient * enthalpy_formation

        element_counts = parse_formula(formula)
        for element, count in element_counts.items():
            total_moles_elements[element] = total_moles_elements.get(element, 0) + (moles_ingredient * count)

    if abs(total_mass - 100.0) > 1e-6:
        print(f"Warning: The sum of recipe percentages is {total_mass}%, not 100%.")

    element_moles = total_moles_elements
    o_moles = element_moles.get('O', 0)
    c_moles = element_moles.get('C', 0)
    h_moles = element_moles.get('H', 0)
    mg_moles = element_moles.get('Mg', 0)

    oxygen_needed = (2 * c_moles) + (h_moles / 2) + (2 * mg_moles)
    oxygen_balance_moles = o_moles - oxygen_needed

    oxygen_balance_grams = oxygen_balance_moles * 15.999
    oxygen_balance_percent = (oxygen_balance_grams / 100.0) * 100.0

    return {
        'elemental_moles': total_moles_elements,
        'reactant_enthalpy_kJ_100g': total_enthalpy,
        'oxygen_balance_percent': oxygen_balance_percent
    }
