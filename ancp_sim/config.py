import json

def load_config(filepath="config.json"):
    """
    Loads the simulation configuration from a JSON file.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration object.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Configuration file '{filepath}' not found. Using default values.")
        # Populate with default values as a fallback
        return {
            "burn_rate": {
                "a": 3.5,
                "n": 0.5
            },
            "catalyst": {
                "ferric_oxide_multiplier": 1.7
            },
            "efficiencies": {
                "combustion_efficiency": 0.90,
                "nozzle_efficiency": 0.92,
                "two_phase_efficiency": 0.95
            }
        }
    except json.JSONDecodeError:
        print(f"Error: The file {filepath} is not a valid JSON file.")
        return None
