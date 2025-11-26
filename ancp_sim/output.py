"""
This module provides functions for formatting and printing simulation results.
"""

def print_banner():
    """Prints the main simulator banner."""
    print("--- ANCP-Sim: Ammonium Nitrate Chemical Propulsion Simulator ---")

def print_inputs(config, recipe_file, chamber_pressure):
    """Prints a summary of the simulation inputs."""
    print("\n--- Simulation Inputs ---")
    print(f"Configuration File: {config}")
    print(f"Recipe File: {recipe_file}")
    print(f"Chamber Pressure: {chamber_pressure:.1f} bar")
    print("-------------------------\n")

def print_stoichiometry(recipe_name, results):
    """Prints formatted stoichiometry results."""
    print("--- Stoichiometry Results ---")
    print(f"Propellant: {recipe_name}")
    print("  Elemental Moles (per 100g):")
    for element, moles in results['elemental_moles'].items():
        print(f"    {element:<2}: {moles:.4f} mol")
    print(f"  Reactant Enthalpy: {results['reactant_enthalpy_kJ_100g']:.2f} kJ/100g")
    print(f"  Oxygen Balance: {results['oxygen_balance_percent']:.2f} %")
    print("-----------------------------\n")

def print_thermo(results):
    """Prints formatted thermodynamic and performance results."""
    print("--- Performance Results ---")
    if 'error' in results:
        print(f"  Calculation Error: {results['error']}")
        return

    print("  Thermodynamic Properties:")
    print(f"    Flame Temperature (T_flame): {results['t_flame_K']:.1f} K")
    print(f"    Specific Heat Ratio (gamma): {results['gamma']:.4f}")
    print(f"    Product Mol. Weight: {results['product_molecular_weight_g_mol']:.2f} g/mol")

    print("\n  Ideal Performance:")
    print(f"    Characteristic Velocity (C*): {results['c_star_m_s']:.1f} m/s")
    print(f"    Vacuum Specific Impulse (Isp): {results['isp_vacuum_sec_ideal']:.1f} s")

    print("\n  Delivered Performance (with efficiencies):")
    print(f"    Vacuum Specific Impulse (Isp): {results['isp_vacuum_sec_delivered']:.1f} s")
    print("---------------------------\n")
