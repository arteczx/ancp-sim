import cantera as ct
import numpy as np
import math
from .stoichiometry import parse_formula

def calculate_thermo(recipe, ingredients_db, config, chamber_pressure_bar=70):
    """
    Calculates thermodynamic properties using single-phase approach.
    Simpler and more reliable than Mixture class for this application.
    """
    try:
        print("\n=== Thermodynamic Calculation ===")
        
        # 1. Create all species in a single phase
        print("Setting up species...")
        
        # Create reactant species
        reactant_species = []
        for name, data in ingredients_db.items():
            if recipe.get(name, 0) > 0:
                composition_dict = parse_formula(data['formula'])
                h0_j_kmol = data['enthalpy_formation_kJ_mol'] * 1_000_000
                
                # Use NASA7 format with proper coefficients
                # a1=cp/R, a5=h/RT, a6=s/R at 298K
                h_reduced = h0_j_kmol / 8314.46  # Divide by R
                
                reactant_species.append(ct.Species.from_dict({
                    'name': name.replace(" ", "_"), 
                    'composition': composition_dict,
                    'thermo': {
                        'model': 'NASA7',
                        'temperature-ranges': [200.0, 1000.0, 6000.0],
                        'data': [
                            # Low temp: [a1, a2, a3, a4, a5, a6, a7]
                            [5.0, 0.0, 0.0, 0.0, 0.0, h_reduced, 0.0],
                            # High temp
                            [5.0, 0.0, 0.0, 0.0, 0.0, h_reduced, 0.0]
                        ]
                    }
                }))
        
        print(f"  Created {len(reactant_species)} reactant species")
        
        # 2. Load product species
        print("Loading product databases...")
        gas_species = ct.Species.list_from_file('nasa_gas.yaml')
        
        # Load condensed species (only relevant ones)
        condensed_species = []
        try:
            all_condensed = ct.Species.list_from_file('nasa_condensed.yaml')
            relevant = ['MgO(s)', 'MgO(l)']  # Start with just MgO
            for species in all_condensed:
                if species.name in relevant:
                    condensed_species.append(species)
            print(f"  Loaded {len(condensed_species)} condensed species")
        except Exception as e:
            print(f"  Warning: {e}")
        
        # 3. Create single Solution with all species
        all_species = reactant_species + gas_species + condensed_species
        gas = ct.Solution(thermo='ideal-gas', species=all_species)
        
        # 4. Set initial state
        reactant_mass_fractions = {
            name.replace(" ", "_"): pct/100.0 
            for name, pct in recipe.items()
        }
        
        pressure_pa = chamber_pressure_bar * 1e5
        T_initial = 298.15
        
        gas.TPY = T_initial, pressure_pa, reactant_mass_fractions
        
        print(f"  Initial T: {T_initial:.1f} K")
        print(f"  Pressure: {chamber_pressure_bar:.1f} bar")
        print(f"  Initial H: {gas.enthalpy_mass/1e6:.2f} MJ/kg")
        
        # 5. CRITICAL FIX: Use gibbs minimization, not HP directly
        # First equilibrate at high T to get good initial guess
        print("\nStep 1: Initial equilibration at fixed T...")
        gas.TP = 2200, pressure_pa  # Good guess for AN propellants
        
        try:
            gas.equilibrate('TP', solver='vcs', max_steps=500, max_iter=200)
            print(f"  ✓ Initial state: T={gas.T:.0f}K")
        except Exception as e:
            print(f"  Warning: Initial TP equilibration had issues: {e}")
        
        # Now do HP equilibration from this better starting point
        print("Step 2: Adiabatic equilibration (HP)...")
        
        # Reset to initial enthalpy
        gas.TPY = T_initial, pressure_pa, reactant_mass_fractions
        h_reactants = gas.enthalpy_mass
        p_chamber = pressure_pa
        
        # Set to high temp state then impose HP constraint
        gas.TP = 2200, p_chamber
        gas.HP = h_reactants, p_chamber
        
        try:
            # Use Gibbs minimization with VCS
            gas.equilibrate('HP', solver='vcs', 
                          rtol=1e-6,
                          max_steps=2000, 
                          max_iter=500,
                          estimate_equil=0)  # Don't use fast estimate
            
            print(f"  ✓ Converged! T_flame = {gas.T:.1f} K")
            
        except ct.CanteraError as e:
            print(f"  First attempt failed, trying with looser tolerance...")
            try:
                gas.equilibrate('HP', solver='vcs', 
                              rtol=1e-5,
                              max_steps=3000)
                print(f"  ✓ Converged with relaxed tolerance")
            except:
                # Last resort: use auto solver
                print(f"  Trying auto solver...")
                gas.equilibrate('HP', solver='auto', max_steps=2000)
        
        # 6. Extract and validate results
        T_flame = gas.T
        M_products = gas.mean_molecular_weight
        
        # Sanity checks
        if T_flame < 500:
            raise ValueError(f"Flame temperature too low ({T_flame:.0f}K) - combustion didn't occur")
        
        if M_products > 50:
            print(f"  Warning: High molecular weight ({M_products:.1f} g/mol)")
        
        if gas.cv_mass <= 0:
            raise ValueError(f"Invalid cv_mass: {gas.cv_mass}")
        
        gamma = gas.cp_mass / gas.cv_mass
        
        if gamma <= 1.0:
            raise ValueError(f"Invalid gamma: {gamma:.4f}")
        
        if gamma < 1.15 or gamma > 1.35:
            print(f"  Warning: Gamma ({gamma:.4f}) outside typical range 1.15-1.35")
        
        # 7. Calculate performance
        R_u = ct.gas_constant
        g0 = 9.80665
        
        # Characteristic velocity
        vdk_gamma = math.sqrt(gamma) * (2 / (gamma + 1))**((gamma + 1) / (2 * (gamma - 1)))
        c_star = math.sqrt(R_u * T_flame / M_products) / vdk_gamma
        
        # Vacuum thrust coefficient
        term1 = 2 * gamma**2 / (gamma - 1)
        term2 = (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))
        cf_vacuum = math.sqrt(term1 * term2)
        
        # Ideal specific impulse
        isp_sec_ideal = cf_vacuum * c_star / g0
        
        # 8. Apply efficiencies
        efficiencies = config.get("efficiencies", {})
        combustion_eff = efficiencies.get("combustion_efficiency", 1.0)
        nozzle_eff = efficiencies.get("nozzle_efficiency", 1.0)
        two_phase_eff = efficiencies.get("two_phase_efficiency", 1.0)
        
        isp_sec_delivered = isp_sec_ideal * combustion_eff * nozzle_eff * two_phase_eff
        
        # 9. Display results
        print(f"\n=== Equilibrium Products ===")
        print(f"Flame Temperature: {T_flame:.1f} K")
        print(f"Molecular Weight: {M_products:.2f} g/mol")
        print(f"Gamma: {gamma:.4f}")
        print(f"C*: {c_star:.1f} m/s")
        print(f"Isp (ideal): {isp_sec_ideal:.1f} s")
        print(f"Isp (delivered): {isp_sec_delivered:.1f} s")
        
        # Show major products
        print(f"\nMajor Products (>2%):")
        products = []
        for i, name in enumerate(gas.species_names):
            if gas.X[i] > 0.02:
                phase = "condensed" if "(s)" in name or "(l)" in name else "gas"
                products.append((name, gas.X[i], phase))
        
        for name, frac, phase in sorted(products, key=lambda x: x[1], reverse=True):
            print(f"  {name:15s}: {frac*100:5.2f}% ({phase})")
        
        print("=" * 50)
        
        return {
            't_flame_K': T_flame,
            'gamma': gamma,
            'product_molecular_weight_g_mol': M_products * 1000,
            'c_star_m_s': c_star,
            'isp_vacuum_sec_ideal': isp_sec_ideal,
            'isp_vacuum_sec_delivered': isp_sec_delivered
        }
        
    except ct.CanteraError as e:
        error_msg = str(e)
        print(f"\n✗ Cantera Error:")
        print(f"  {error_msg[:400]}")
        print(f"\nTroubleshooting:")
        print(f"  - Try different pressure: --pc 50 or --pc 100")
        print(f"  - Check recipe sums to 100%")
        print(f"  - Verify ingredients.json has valid data")
        return {'error': 'Equilibration failed', 't_flame_K': 0}
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 't_flame_K': 0}
