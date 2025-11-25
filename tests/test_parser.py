import unittest
from ancp_sim.stoichiometry import parse_formula

class TestFormulaParser(unittest.TestCase):

    def test_simple_formula(self):
        """Test a simple formula without parentheses."""
        self.assertEqual(parse_formula('H2O'), {'H': 2, 'O': 1})
        self.assertEqual(parse_formula('C6H12O6'), {'C': 6, 'H': 12, 'O': 6})

    def test_formula_with_parentheses(self):
        """Test a formula with parentheses."""
        self.assertEqual(parse_formula('Ca(OH)2'), {'Ca': 1, 'O': 2, 'H': 2})
        self.assertEqual(parse_formula('(NH4)2SO4'), {'N': 2, 'H': 8, 'S': 1, 'O': 4})

    def test_nested_parentheses(self):
        """Test a formula with nested parentheses."""
        self.assertEqual(parse_formula('C(C(H)3)3'), {'C': 4, 'H': 9})

    def test_no_trailing_number(self):
        """Test a formula with an element that has no trailing number."""
        self.assertEqual(parse_formula('C2H5OH'), {'C': 2, 'H': 6, 'O': 1})

if __name__ == '__main__':
    unittest.main()
