# test_app_streamlit_sheets.py
import unittest
# We will move the suma function to this file for testing,
# as it is not used in the Streamlit app.

def suma(a, b):
    """Suma dos números."""
    return a + b

class TestSuma(unittest.TestCase):

    def test_suma_positivos(self):
        """Prueba la suma de dos números positivos."""
        self.assertEqual(suma(2, 3), 5)

    def test_suma_negativos(self):
        """Prueba la suma de dos números negativos."""
        self.assertEqual(suma(-5, -10), -15)

    def test_suma_positivo_y_negativo(self):
        """Prueba la suma de un número positivo y uno negativo."""
        self.assertEqual(suma(10, -3), 7)

    def test_suma_con_cero(self):
        """Prueba la suma con cero."""
        self.assertEqual(suma(5, 0), 5)
        self.assertEqual(suma(0, 0), 0)

    def test_suma_flotantes(self):
        """Prueba la suma de números de punto flotante."""
        self.assertAlmostEqual(suma(1.5, 2.7), 4.2)