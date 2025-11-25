import json

def load_ingredients(filepath="data/ingredients.json"):
    """
    Loads the chemical properties of ingredients from a JSON file.

    Args:
        filepath (str): The path to the ingredients JSON file.

    Returns:
        dict: A dictionary containing the ingredient data.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {filepath} is not a valid JSON file.")
        return None
