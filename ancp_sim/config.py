import configparser

def load_config(filepath="config.ini"):
    """
    Loads the simulation configuration from an INI file.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
        configparser.ConfigParser: The loaded configuration object.
    """
    config = configparser.ConfigParser()
    try:
        config.read(filepath)
        if not config.sections():
            raise FileNotFoundError
    except FileNotFoundError:
        print(f"Warning: Configuration file '{filepath}' not found. Using default values.")
        # Populate with default values as a fallback
        config['burn_rate'] = {'a': '3.5', 'n': '0.5'}
        config['catalyst'] = {'ferric_oxide_multiplier': '1.7'}
        config['efficiency'] = {'cstar_efficiency': '0.90', 'isp_efficiency': '0.92'}

    return config
