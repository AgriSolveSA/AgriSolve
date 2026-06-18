"""
Per-client authentication.

Replaces the old single shared `dashboard_password` (one secret, everyone
who knew it saw all 4 verticals and whatever data was in their session)
with a `[clients]` table in secrets.toml: each client gets their own
password and is restricted to their own vertical(s).

Pure functions, no Streamlit import — testable without mocking st.secrets
(see test_auth.py), matching this repo's existing style of keeping
vertical-agnostic logic Streamlit-free (verticals/base.py and friends).
"""
from __future__ import annotations


def find_client(entered_password: str, clients_config: dict) -> dict | None:
    """
    clients_config is st.secrets.get("clients", {}): a dict of
    client_id -> {"password": ..., "display_name": ..., "verticals": [...]}.

    Returns the matched client's config (with "client_id" merged in), or
    None if no client's password matches. An empty entered_password never
    matches, even if a client config has an empty/missing password — an
    unset password must never be treated as "no password required."
    """
    if not entered_password:
        return None
    for client_id, cfg in clients_config.items():
        client_password = cfg.get("password") if hasattr(cfg, "get") else None
        if client_password and client_password == entered_password:
            merged = dict(cfg)
            merged["client_id"] = client_id
            return merged
    return None


def allowed_verticals(client: dict | None, all_verticals: list[str]) -> list[str]:
    """
    Returns the list of vertical names this client may see.

    - No client matched (legacy single shared password, or no [clients]
      table configured at all) -> every vertical, preserving today's
      behaviour for anyone not yet migrated to per-client config.
    - Client matched but its "verticals" key is missing/empty -> every
      vertical too, so an "admin"/demo client entry can see everything by
      simply omitting the key, without needing to enumerate all 4 by name.
    - Client matched with a non-empty "verticals" list -> intersected with
      the real REGISTRY keys (preserving REGISTRY's order), so a typo in
      secrets.toml just silently omits that one vertical rather than
      crashing the sidebar or granting access to a vertical that doesn't
      exist.
    """
    if not client:
        return list(all_verticals)
    requested = client.get("verticals")
    if not requested:
        return list(all_verticals)
    return [v for v in all_verticals if v in requested]


def authenticate(entered_password: str, legacy_password: str, clients_config: dict) -> tuple[bool, dict | None]:
    """
    Single entry point app.py calls. Returns (is_authenticated, client_or_none).

    Checks per-client passwords first (clients_config), then falls back to
    the legacy single shared dashboard_password for anyone not yet
    migrated — both can be configured at once during a transition period
    without either breaking the other.
    """
    client = find_client(entered_password, clients_config) if clients_config else None
    if client:
        return True, client
    if legacy_password and entered_password == legacy_password:
        return True, None
    return False, None
