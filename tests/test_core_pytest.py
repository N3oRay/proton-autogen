# tests/test_core_pytest.py
"""Tests avec pytest (plus simple)."""

import pytest
from unittest.mock import patch, MagicMock
from proton_autogen.core import filter_env, apply_user_profile


@pytest.mark.unit
class TestFilterEnvPytest:
    """Tests filter_env avec pytest."""

    @patch('proton_autogen.core.ALLOWED_ENV_VARS')
    def test_filter_keeps_allowed(self, mock_allowed):
        """Garde les variables autorisées."""
        mock_allowed.__contains__ = lambda self, x: x == "PROTON_NO_ESYNC"

        env = {"PROTON_NO_ESYNC": "1", "BAD_VAR": "value"}
        result = filter_env(env)

        assert "PROTON_NO_ESYNC" in result
        assert "BAD_VAR" not in result

    @patch('proton_autogen.core.ALLOWED_ENV_VARS')
    def test_filter_empty_input(self, mock_allowed):
        """Gère l'entrée vide."""
        mock_allowed.__contains__ = lambda self, x: False

        assert filter_env({}) == {}
