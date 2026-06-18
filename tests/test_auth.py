"""
Tests for auth.py — per-client password matching and vertical restriction.
No Streamlit involved; clients_config is a plain dict standing in for
st.secrets.get("clients", {}).
"""
import pytest

from auth import find_client, allowed_verticals, authenticate

ALL_VERTICALS = ["Insurance Broker", "Accounting Firm", "Construction", "Logistics"]

CLIENTS = {
    "abc_insurance": {"password": "abc123", "display_name": "ABC Insurance Brokers", "verticals": ["Insurance Broker"]},
    "xyz_accounting": {"password": "xyz456", "display_name": "XYZ Accounting", "verticals": ["Accounting Firm", "Construction"]},
    "admin": {"password": "adminpw", "display_name": "AgriSolve Admin"},  # no "verticals" key -> sees everything
}


class TestFindClient:
    def test_matches_correct_password_to_correct_client(self):
        client = find_client("abc123", CLIENTS)
        assert client is not None
        assert client["client_id"] == "abc_insurance"
        assert client["display_name"] == "ABC Insurance Brokers"

    def test_wrong_password_matches_nothing(self):
        assert find_client("wrong-password", CLIENTS) is None

    def test_empty_password_never_matches_even_with_misconfigured_empty_client_password(self):
        clients_with_blank = {**CLIENTS, "broken": {"password": "", "verticals": []}}
        assert find_client("", clients_with_blank) is None

    def test_empty_clients_config_matches_nothing(self):
        assert find_client("anything", {}) is None

    def test_client_without_verticals_key_still_matches_by_password(self):
        client = find_client("adminpw", CLIENTS)
        assert client is not None
        assert client["client_id"] == "admin"


class TestAllowedVerticals:
    def test_no_client_sees_everything_legacy_behaviour(self):
        assert allowed_verticals(None, ALL_VERTICALS) == ALL_VERTICALS

    def test_client_with_one_vertical_sees_only_that_one(self):
        client = find_client("abc123", CLIENTS)
        assert allowed_verticals(client, ALL_VERTICALS) == ["Insurance Broker"]

    def test_client_with_multiple_verticals_sees_only_those_in_registry_order(self):
        client = find_client("xyz456", CLIENTS)
        assert allowed_verticals(client, ALL_VERTICALS) == ["Accounting Firm", "Construction"]

    def test_client_with_no_verticals_key_sees_everything(self):
        client = find_client("adminpw", CLIENTS)
        assert allowed_verticals(client, ALL_VERTICALS) == ALL_VERTICALS

    def test_typo_in_secrets_toml_silently_omits_rather_than_crashing(self):
        client = {"client_id": "typo_client", "verticals": ["Insurnace Broker"]}  # misspelled
        assert allowed_verticals(client, ALL_VERTICALS) == []


class TestAuthenticate:
    def test_per_client_password_authenticates_with_that_client_returned(self):
        ok, client = authenticate("abc123", legacy_password="", clients_config=CLIENTS)
        assert ok is True
        assert client["client_id"] == "abc_insurance"

    def test_legacy_password_still_works_during_transition_with_no_client_attached(self):
        ok, client = authenticate("old-shared-pw", legacy_password="old-shared-pw", clients_config=CLIENTS)
        assert ok is True
        assert client is None

    def test_wrong_password_fails_both_checks(self):
        ok, client = authenticate("nope", legacy_password="old-shared-pw", clients_config=CLIENTS)
        assert ok is False
        assert client is None

    def test_no_clients_configured_falls_back_to_legacy_only(self):
        ok, client = authenticate("old-shared-pw", legacy_password="old-shared-pw", clients_config={})
        assert ok is True
        assert client is None

    def test_empty_entered_password_never_authenticates(self):
        ok, client = authenticate("", legacy_password="old-shared-pw", clients_config=CLIENTS)
        assert ok is False
