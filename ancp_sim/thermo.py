import cantera as ct
import numpy as np
import math
from .stoichiometry import parse_formula

def calculate_thermo(recipe, ingredients_db, config, chamber_pressure_bar=70):
    """
    Calculates thermodynamic properties, including ideal and delivered performance.
    """
    # 1. Create a gas object with all possible species (reactants and products)
    # This is the core insight from the working example.

    # Define custom reactant species
    reactant_species = []
    for name, data in ingredients_db.items():
        composition_dict = parse_formula(data['formula'])
        h0_j_kmol = data['enthalpy_formation_kJ_mol'] * 1_000_000
        reactant_species.append(ct.Species.from_dict({
            'name': name.replace(" ", "_"), 'composition': composition_dict,
            'thermo': {'model': 'constant-cp', 'h0': h0_j_kmol, 's0': 0.0, 'cp0': 0.0}
        }))

    # Define standard product species (both gas and condensed)
    gas_species = ct.Species.list_from_file('nasa_gas.yaml')
    condensed_species = ct.Species.list_from_file('nasa_condensed.yaml')
    product_species = gas_species + condensed_species

    # Create the Solution object, which will model a multiphase mixture
    gas = ct.Solution(thermo='IdealGas', species=reactant_species + product_species)

    # 2. Set the initial state to the unburned reactants
    reactant_mass_fractions = {name.replace(" ", "_"): pct/100.0 for name, pct in recipe.items()}
    gas.TPY = 298.15, chamber_pressure_bar * 1e5, reactant_mass_fractions

    # 3. Equilibrate the mixture at constant enthalpy and pressure
    gas.equilibrate('HP')

    # 4. Extract results from the equilibrated mixture
    T_flame = gas.T
    M_products = gas.mean_molecular_weight
    gamma = gas.cp_mass / gas.cv_mass

    # 5. Calculate performance parameters
    R_u = ct.gas_constant
    g0 = 9.80665

    if gamma <= 1:
        return {'t_flame_K': T_flame, 'error': 'gamma <= 1'}

    vdk_gamma = math.sqrt(gamma) * (2 / (gamma + 1))**((gamma + 1) / (2 * (gamma - 1)))
    c_star = math.sqrt(R_u * T_flame / M_products) / vdk_gamma

    term1 = 2 * gamma**2 / (gamma - 1)
    term2 = (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))

    cf_vacuum = math.sqrt(term1 * term2)
    isp_sec_ideal = cf_vacuum * c_star / g0

    # 6. Apply efficiency factors for delivered performance
    efficiencies = config.get("efficiencies", {})
    combustion_eff = efficiencies.get("combustion_efficiency", 1.0)
    nozzle_eff = efficiencies.get("nozzle_efficiency", 1.0)
    two_phase_eff = efficiencies.get("two_phase_efficiency", 1.0)

    isp_sec_delivered = isp_sec_ideal * combustion_eff * nozzle_eff * two_phase_eff

    return {
        't_flame_K': T_flame,
        'gamma': gamma,
        'product_molecular_weight_g_mol': M_products * 1000,
        'c_star_m_s': c_star,
        'isp_vacuum_sec_ideal': isp_sec_ideal,
        'isp_vacuum_sec_delivered': isp_sec_delivered
    }
