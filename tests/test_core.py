"""
Tests unitaires pour proton_autogen.core

Tests les fonctions pures et critiques sans dependances externes.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'usr', 'lib', 'python3', 'dist-packages'))


class TestFilterEnv(unittest.TestCase):
    """Tests de filter_env() - filtre les variables d'environnement autorisees."""

    @patch('proton_autogen.core.ALLOWED_ENV_VARS', {"PROTON_NO_ESYNC", "DXVK_CONFIG", "MANGOHUD"})
    def test_filter_env_keeps_allowed_vars(self):
        """PASS: Garde les variables autorisees."""
        from proton_autogen.core import filter_env

        env = {
            "PROTON_NO_ESYNC": "1",
            "DXVK_CONFIG": "async=1",
            "MANGOHUD": "1",
            "BAD_VAR": "should_be_removed"
        }

        result = filter_env(env)

        self.assertEqual(len(result), 3)
        self.assertIn("PROTON_NO_ESYNC", result)
        self.assertIn("DXVK_CONFIG", result)
        self.assertNotIn("BAD_VAR", result)

    @patch('proton_autogen.core.ALLOWED_ENV_VARS', {"PROTON_NO_ESYNC"})
    def test_filter_env_removes_forbidden_vars(self):
        """PASS: Supprime les variables non autorisees."""
        from proton_autogen.core import filter_env

        env = {
            "PROTON_NO_ESYNC": "1",
            "LD_PRELOAD": "/bad/path",
            "SHELL": "/bin/bash"
        }

        result = filter_env(env)

        self.assertEqual(len(result), 1)
        self.assertNotIn("LD_PRELOAD", result)
        self.assertNotIn("SHELL", result)

    @patch('proton_autogen.core.ALLOWED_ENV_VARS', set())
    def test_filter_env_empty_input(self):
        """PASS: Gere l'entree vide."""
        from proton_autogen.core import filter_env

        result = filter_env({})
        self.assertEqual(result, {})

    @patch('proton_autogen.core.ALLOWED_ENV_VARS', set())
    def test_filter_env_all_forbidden(self):
        """PASS: Retourne vide si toutes les vars sont interdites."""
        from proton_autogen.core import filter_env

        env = {
            "PATH": "/usr/bin",
            "HOME": "/home/user",
            "SECRET": "value"
        }

        result = filter_env(env)
        self.assertEqual(result, {})


class TestNormalizeFlag(unittest.TestCase):
    """Tests de normalize_flag() - conversion de drapeaux booleens."""

    def test_normalize_flag_true_values(self):
        """PASS: Reconnait les valeurs vraies."""
        from proton_autogen.backend import normalize_flag

        true_values = ["1", "true", "True", "TRUE", "yes", "Yes", "on", "ON"]

        for val in true_values:
            with self.subTest(value=val):
                result = normalize_flag(val)
                self.assertTrue(result, f"'{val}' devrait etre True")

    def test_normalize_flag_false_values(self):
        """PASS: Reconnait les valeurs fausses."""
        from proton_autogen.backend import normalize_flag

        false_values = ["0", "false", "False", "no", "No", "off", "OFF", ""]

        for val in false_values:
            with self.subTest(value=val):
                result = normalize_flag(val)
                self.assertFalse(result, f"'{val}' devrait etre False")

    def test_normalize_flag_none_uses_default(self):
        """PASS: Utilise la valeur par defaut si None."""
        from proton_autogen.backend import normalize_flag

        result = normalize_flag(None, default=True)
        self.assertTrue(result)

        result = normalize_flag(None, default=False)
        self.assertFalse(result)

    def test_normalize_flag_bool_input(self):
        """PASS: Gere les booleens directement."""
        from proton_autogen.backend import normalize_flag

        self.assertTrue(normalize_flag(True))
        self.assertFalse(normalize_flag(False))


class TestApplyUserProfile(unittest.TestCase):
    """Tests de apply_user_profile() - override d'env par profil utilisateur."""

    @patch('proton_autogen.core.logger')
    def test_apply_user_profile_adds_variables(self, mock_logger):
        """PASS: Ajoute les variables du profil."""
        from proton_autogen.core import apply_user_profile

        env = {"EXISTING": "value"}
        profile = {
            "name": "test_profile",
            "env": {
                "DXVK_ASYNC": "1",
                "PROTON_NO_ESYNC": "0"
            }
        }

        result = apply_user_profile(env, profile)

        self.assertEqual(result["DXVK_ASYNC"], "1")
        self.assertEqual(result["PROTON_NO_ESYNC"], "0")
        self.assertEqual(result["EXISTING"], "value")

    @patch('proton_autogen.core.logger')
    def test_apply_user_profile_overrides_variables(self, mock_logger):
        """PASS: Override les variables existantes."""
        from proton_autogen.core import apply_user_profile

        env = {"DXVK_ASYNC": "0"}
        profile = {
            "name": "test_profile",
            "env": {"DXVK_ASYNC": "1"}
        }

        result = apply_user_profile(env, profile)

        self.assertEqual(result["DXVK_ASYNC"], "1")

    @patch('proton_autogen.core.logger')
    def test_apply_user_profile_removes_variables(self, mock_logger):
        """PASS: Supprime les variables demandees."""
        from proton_autogen.core import apply_user_profile

        env = {
            "KEEP_THIS": "value",
            "REMOVE_THIS": "value"
        }
        profile = {
            "name": "test_profile",
            "env": {},
            "remove": ["REMOVE_THIS"]
        }

        result = apply_user_profile(env, profile)

        self.assertIn("KEEP_THIS", result)
        self.assertNotIn("REMOVE_THIS", result)

    def test_apply_user_profile_none_returns_unchanged(self):
        """PASS: Retourne l'env inchangee si profil None."""
        from proton_autogen.core import apply_user_profile

        env = {"VAR": "value"}

        result = apply_user_profile(env, None)

        self.assertEqual(result, env)


if __name__ == '__main__':
    unittest.main()
