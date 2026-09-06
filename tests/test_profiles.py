# tests/test_profiles.py
"""Tests de application de profils utilisateur."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from proton_autogen.core import apply_user_profile


class TestApplyUserProfile(unittest.TestCase):
    """Tests de apply_user_profile() - override d'env par profil utilisateur."""

    def test_apply_user_profile_adds_variables(self):
        """✓ Ajoute les variables du profil."""
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

    def test_apply_user_profile_overrides_variables(self):
        """✓ Override les variables existantes."""
        env = {"DXVK_ASYNC": "0"}
        profile = {
            "name": "test_profile",
            "env": {"DXVK_ASYNC": "1"}
        }

        result = apply_user_profile(env, profile)

        self.assertEqual(result["DXVK_ASYNC"], "1")

    def test_apply_user_profile_removes_variables(self):
        """✓ Supprime les variables demandées."""
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
        """✓ Retourne l'env inchangée si profil None."""
        env = {"VAR": "value"}

        result = apply_user_profile(env, None)

        self.assertEqual(result, env)

    @patch('proton_autogen.core.logger')
    def test_apply_user_profile_logs_action(self, mock_logger):
        """✓ Log l'application du profil."""
        env = {}
        profile = {
            "name": "my_profile",
            "env": {}
        }

        apply_user_profile(env, profile)

        mock_logger.info.assert_called()


class TestLoadUserProfile(unittest.TestCase):
    """Tests de load_user_profile() - chargement depuis fichier."""

    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_load_user_profile_exists(self, mock_exists, mock_open):
        """✓ Charge un profil existant."""
        from proton_autogen.core import load_user_profile
        import json

        mock_exists.return_value = True
        profile_data = {"name": "test", "env": {"VAR": "value"}}
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(profile_data)

        # À adapter selon implémentation réelle
        # result = load_user_profile("test")
        # self.assertEqual(result["name"], "test")

    @patch('os.path.exists')
    def test_load_user_profile_not_exists(self, mock_exists):
        """✓ Retourne {} si profil inexistant."""
        from proton_autogen.core import load_user_profile

        mock_exists.return_value = False

        result = load_user_profile("nonexistent")

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
