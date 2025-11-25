import unittest
import os
import json
from ancp_sim.stoichiometry import calculate_stoichiometry
from ancp_sim.chemdb import load_ingredients

class TestStoichiometry(unittest.TestCase):

    def setUp(self):
        """Set up for the tests."""
        # It's better to load the db once for all tests in this class
        self.db = load_ingredients(os.path.join(os.path.dirname(__file__), '..', 'data', 'ingredients.json'))
        self.assertIsNotNone(self.db, "Failed to load ingredients database.")

    def test_an_only_stoichiometry(self):
        """Test stoichiometry for pure Ammonium Nitrate."""
        recipe = {"Ammonium Nitrate": 100.0}
        results = calculate_stoichiometry(recipe, self.db)

        # AN is H4N2O3, MW = 80.043
        # Moles in 100g = 100 / 80.043 = 1.2493
        self.assertAlmostEqual(results['elemental_moles']['H'], 1.2493 * 4, places=3)
        self.assertAlmostEqual(results['elemental_moles']['N'], 1.2493 * 2, places=3)
        self.assertAlmostEqual(results['elemental_moles']['O'], 1.2493 * 3, places=3)

        # Enthalpy of AN is -365.56 kJ/mol
        self.assertAlmostEqual(results['reactant_enthalpy_kJ_100g'], 1.2493 * -365.56, places=1)

    def test_example_recipe_stoichiometry(self):
        """Test the stoichiometry of the example recipe."""
        recipe = {
            "Ammonium Nitrate": 65.0,
            "Potassium Nitrate": 5.0,
            "Magnesium": 15.0,
            "Castor Oil": 7.5,
            "Methylene Diphenyl Diisocyanate": 7.5
        }
        results = calculate_stoichiometry(recipe, self.db)

        # Update with more precise values from the previous successful run
        self.assertAlmostEqual(results['elemental_moles']['H'], 4.384, places=3)
        self.assertAlmostEqual(results['elemental_moles']['N'], 1.7335, places=4)
        self.assertAlmostEqual(results['elemental_moles']['O'], 2.717, places=3)
        self.assertAlmostEqual(results['elemental_moles']['K'], 0.049, places=3)
        self.assertAlmostEqual(results['elemental_moles']['Mg'], 0.617, places=3)
        self.assertAlmostEqual(results['elemental_moles']['C'], 0.908, places=3)
        self.assertAlmostEqual(results['reactant_enthalpy_kJ_100g'], -343.8, places=1)
        self.assertAlmostEqual(results['oxygen_balance_percent'], -40.4087, places=4) # Increased precision

if __name__ == '__main__':
    unittest.main()
