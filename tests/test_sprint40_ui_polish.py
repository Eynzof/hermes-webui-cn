"""
Sprint 40 UI Polish Tests: Active session title uses CSS theme variable (issue #440).

Covers:
- .session-item.active .session-title uses var(--gold) instead of hardcoded #e8a030
- The hardcoded amber color #e8a030 is NOT present in the active session title rule
"""
import os
import pathlib
import re
import sys
import unittest
from unittest import mock

# Ensure repo is on sys.path so api.config can be imported
_REPO_ROOT = pathlib.Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

REPO_ROOT  = _REPO_ROOT
STYLE_CSS  = (REPO_ROOT / "static" / "style.css").read_text()
SESSIONS_JS = (REPO_ROOT / "static" / "sessions.js").read_text()
PANELS_JS   = (REPO_ROOT / "static" / "panels.js").read_text()

try:
    from api import config as _api_config
    _config_available = True
except Exception:
    _api_config = None
    _config_available = False

# Combined tests for Sprint 40 — Session + UI Polish
# Covers: active title color, unknown model, Telegram badge,
#         custom endpoint model routing, workspace chip


# ── #451 active title ─────────────────────────────────────────────
class TestActiveSessionTitleThemeColor(unittest.TestCase):

    def test_active_session_title_uses_theme_variable(self):
        """
        .session-item.active .session-title must use var(--gold) not a hardcoded hex.
        The light-theme override line (data-theme="light") is allowed to keep its own
        hardcoded color; we only check the base/dark rule.
        """
        # Find all lines that match the active session title selector
        lines = STYLE_CSS.splitlines()
        base_rule_lines = [
            line for line in lines
            if ".session-item.active .session-title" in line
            and 'data-theme="light"' not in line
        ]

        self.assertTrue(
            len(base_rule_lines) >= 1,
            "Could not find .session-item.active .session-title base rule in style.css"
        )

        for line in base_rule_lines:
            self.assertIn(
                "var(--gold)",
                line,
                f"Expected var(--gold) in active session title rule, got: {line.strip()}"
            )
            self.assertNotIn(
                "#e8a030",
                line,
                f"Hardcoded #e8a030 must be removed from active session title rule: {line.strip()}"
            )


if __name__ == "__main__":
    unittest.main()

# ── #452 unknown model ─────────────────────────────────────────────
class TestGatewaySessionNullModel(unittest.TestCase):
    """Verify that api/models.py and api/gateway_watcher.py do not
    fall back to the string 'unknown' for missing model values."""

    def test_gateway_session_null_model_returns_none_not_unknown(self):
        """api/models.py must not use `or 'unknown'` for the model field
        so that a NULL model in state.db is returned as None (falsy) to
        the frontend rather than the truthy string 'unknown'."""
        models_src = (REPO_ROOT / "api" / "models.py").read_text()
        # Ensure the old fallback pattern is gone
        self.assertNotIn(
            "'model': row['model'] or 'unknown'",
            models_src,
            "api/models.py must not use `or 'unknown'` for the model field "
            "(fixes #443: gateway sessions showed 'telegram · unknown')",
        )

    def test_gateway_watcher_null_model_returns_none_not_unknown(self):
        """api/gateway_watcher.py must not use `or 'unknown'` for the model
        field so that a NULL model in state.db is returned as None (falsy)."""
        gw_src = (REPO_ROOT / "api" / "gateway_watcher.py").read_text()
        self.assertNotIn(
            "'model': row['model'] or 'unknown'",
            gw_src,
            "api/gateway_watcher.py must not use `or 'unknown'` for the model "
            "field (fixes #443: gateway sessions showed 'telegram · unknown')",
        )

    def test_gateway_session_model_uses_none_fallback(self):
        """Both source files must use `row['model'] or None` (explicit None
        fallback) for the model field assignment."""
        models_src = (REPO_ROOT / "api" / "models.py").read_text()
        gw_src = (REPO_ROOT / "api" / "gateway_watcher.py").read_text()
        self.assertIn(
            "'model': row['model'] or None,",
            models_src,
            "api/models.py should assign `row['model'] or None` for the model field",
        )
        self.assertIn(
            "'model': row['model'] or None,",
            gw_src,
            "api/gateway_watcher.py should assign `row['model'] or None` for the model field",
        )


if __name__ == "__main__":
    unittest.main()

# ── #453 telegram badge ─────────────────────────────────────────────
class TestTelegramBadgeMutedColor(unittest.TestCase):

    def test_telegram_badge_uses_muted_color(self):
        """Telegram badge rules must use rgba(0, 136, 204, 0.55) not #0088cc."""
        # Extract only the telegram-related CSS block
        telegram_lines = [
            line for line in STYLE_CSS.splitlines()
            if 'data-source="telegram"' in line or "data-source='telegram'" in line
        ]
        self.assertTrue(
            len(telegram_lines) >= 2,
            "Expected at least 2 telegram badge CSS rules"
        )
        muted_color = "rgba(0, 136, 204, 0.55)"
        for line in telegram_lines:
            self.assertIn(
                muted_color, line,
                f"Telegram CSS rule should use {muted_color!r}, got: {line!r}"
            )
            self.assertNotIn(
                "#0088cc", line,
                f"Telegram CSS rule must not use saturated #0088cc, got: {line!r}"
            )

    def test_telegram_border_left_color_muted(self):
        """The border-left-color rule for telegram uses rgba."""
        pattern = r'\.session-item\.cli-session\[data-source=["\']telegram["\']\]\s*\{[^}]*border-left-color:\s*rgba\(0,\s*136,\s*204,\s*0\.55\)'
        self.assertRegex(STYLE_CSS, pattern,
            "border-left-color for telegram should be rgba(0, 136, 204, 0.55)")

    def test_telegram_after_color_muted(self):
        """The ::after color rule for telegram uses rgba."""
        pattern = r'\.session-item\.cli-session\[data-source=["\']telegram["\']\]::after\s*\{[^}]*color:\s*rgba\(0,\s*136,\s*204,\s*0\.55\)'
        self.assertRegex(STYLE_CSS, pattern,
            "::after color for telegram should be rgba(0, 136, 204, 0.55)")


class TestFormatSourceTagHelper(unittest.TestCase):

    def test_format_source_tag_helper_exists(self):
        """_formatSourceTag function must be defined in sessions.js."""
        self.assertIn("function _formatSourceTag(", SESSIONS_JS,
            "_formatSourceTag helper function not found in sessions.js")

    def test_format_source_tag_maps_telegram(self):
        """_formatSourceTag maps 'telegram' to 'via Telegram'."""
        self.assertIn("telegram:'via Telegram'", SESSIONS_JS,
            "sessions.js should map telegram -> 'via Telegram'")

    def test_format_source_tag_maps_discord(self):
        """_formatSourceTag maps 'discord' to 'via Discord'."""
        self.assertIn("discord:'via Discord'", SESSIONS_JS,
            "sessions.js should map discord -> 'via Discord'")

    def test_format_source_tag_maps_slack(self):
        """_formatSourceTag maps 'slack' to 'via Slack'."""
        self.assertIn("slack:'via Slack'", SESSIONS_JS,
            "sessions.js should map slack -> 'via Slack'")

    def test_metabits_uses_format_helper(self):
        """The metaBits push for source_tag should use _formatSourceTag."""
        self.assertIn("metaBits.push(_formatSourceTag(s.source_tag))", SESSIONS_JS,
            "metaBits push should wrap source_tag with _formatSourceTag()")

    def test_raw_source_tag_not_pushed_directly(self):
        """The old raw metaBits.push(s.source_tag) should not exist."""
        self.assertNotIn("metaBits.push(s.source_tag)", SESSIONS_JS,
            "Raw s.source_tag should not be pushed directly to metaBits")


if __name__ == "__main__":
    unittest.main()

# ── #454 model routing ─────────────────────────────────────────────
@unittest.skipUnless(_config_available, "api.config not importable")
class TestCustomEndpointModelStripping:
    """Tests for fix #433: strip provider prefix when custom base_url is set."""

    def _resolve(self, model_id, provider=None, base_url=None):
        """Helper: set cfg directly (same pattern as test_model_resolver.py)."""
        old_cfg = dict(_api_config.cfg)
        model_cfg = {}
        if provider:
            model_cfg['provider'] = provider
        if base_url:
            model_cfg['base_url'] = base_url
        _api_config.cfg['model'] = model_cfg
        try:
            return _api_config.resolve_model_provider(model_id)
        finally:
            _api_config.cfg.clear()
            _api_config.cfg.update(old_cfg)

    def test_prefixed_model_stripped_for_custom_endpoint(self):
        """Issue #433: 'openai/gpt-5.4' with custom base_url returns bare 'gpt-5.4'."""
        model, provider, base_url = self._resolve(
            'openai/gpt-5.4',
            provider='custom',
            base_url='http://my-proxy.local:8080/v1',
        )
        assert model == 'gpt-5.4', (
            "Expected bare 'gpt-5.4' for custom endpoint, got '{}'."
            " Stale provider-prefix must be stripped.".format(model)
        )
        assert base_url == 'http://my-proxy.local:8080/v1'
        assert provider == 'custom'

    def test_bare_model_unchanged_for_custom_endpoint(self):
        """Bare model ID (no slash) must pass through untouched with custom base_url."""
        model, provider, base_url = self._resolve(
            'gpt-4o',
            provider='custom',
            base_url='http://my-proxy.local:8080/v1',
        )
        assert model == 'gpt-4o', (
            "Bare model 'gpt-4o' should not be modified, got '{}'.".format(model)
        )
        assert base_url == 'http://my-proxy.local:8080/v1'
        assert provider == 'custom'

    def test_prefixed_model_kept_for_openrouter(self):
        """When NO custom base_url (openrouter route), prefixed model must stay prefixed."""
        model, provider, base_url = self._resolve(
            'openai/gpt-5.4',
            provider='anthropic',  # cross-provider pick triggers openrouter routing
        )
        # Cross-provider model with openrouter routing must keep full provider/model path
        assert 'openai/gpt-5.4' in model or provider == 'openrouter', (
            "Expected prefixed model or openrouter routing for non-custom endpoint, "
            "got model='{}', provider='{}'.".format(model, provider)
        )
        assert base_url is None, (
            "OpenRouter routing must not set a base_url, got '{}'.".format(base_url)
        )

# ── #455 workspace chip ─────────────────────────────────────────────
class TestWorkspaceChipAfterProfileSwitch(unittest.TestCase):
    """Verify that switchToProfile() applies the profile default workspace
    to the new session when a conversation is in progress (fixes #424)."""

    def test_workspace_chip_updated_after_profile_switch(self):
        """After await newSession(false) in the sessionInProgress branch,
        the code must call updateWorkspaceChip() so the chip reflects the
        new profile's default workspace instead of showing 'No active workspace'."""
        # Find the sessionInProgress block
        idx = PANELS_JS.find('if (sessionInProgress)')
        self.assertGreater(idx, -1, "sessionInProgress branch must exist in panels.js")

        # Slice from that point to cover the relevant block
        block = PANELS_JS[idx:idx + 1000]

        # newSession(false) must be called first
        self.assertIn('await newSession(false)', block,
                      "sessionInProgress branch must call await newSession(false)")

        # The fix: updateWorkspaceChip() must be called after newSession(false)
        pos_new_session = block.find('await newSession(false)')
        pos_update_chip = block.find('updateWorkspaceChip()')
        self.assertGreater(pos_update_chip, -1,
                           "updateWorkspaceChip() must be called in the sessionInProgress branch")
        self.assertGreater(pos_update_chip, pos_new_session,
                           "updateWorkspaceChip() must be called AFTER newSession(false)")

    def test_profile_default_workspace_applied_to_new_session(self):
        """After newSession(false) the code must assign S._profileDefaultWorkspace
        to S.session.workspace so the session is correctly tagged."""
        idx = PANELS_JS.find('if (sessionInProgress)')
        self.assertGreater(idx, -1)
        block = PANELS_JS[idx:idx + 1000]

        # The fix block must set S.session.workspace from S._profileDefaultWorkspace
        self.assertIn('S.session.workspace = S._profileDefaultWorkspace', block,
                      "S.session.workspace must be set from S._profileDefaultWorkspace "
                      "in the sessionInProgress branch after newSession(false)")

    def test_api_session_update_called_for_new_session_workspace(self):
        """The fix must call /api/session/update to persist the workspace on the server."""
        idx = PANELS_JS.find('if (sessionInProgress)')
        self.assertGreater(idx, -1)
        block = PANELS_JS[idx:idx + 1000]

        # Must patch the session on the backend too
        self.assertIn('/api/session/update', block,
                      "The sessionInProgress branch must call /api/session/update "
                      "to persist the new workspace after newSession(false)")

    def test_update_workspace_chip_before_render_session_list(self):
        """updateWorkspaceChip() should be called before renderSessionList()
        so the chip is correct when the UI re-renders."""
        idx = PANELS_JS.find('if (sessionInProgress)')
        self.assertGreater(idx, -1)
        block = PANELS_JS[idx:idx + 1000]

        pos_chip = block.find('updateWorkspaceChip()')
        pos_render = block.find('await renderSessionList()')
        self.assertGreater(pos_chip, -1, "updateWorkspaceChip() must exist in block")
        self.assertGreater(pos_render, -1, "renderSessionList() must exist in block")
        self.assertLess(pos_chip, pos_render,
                        "updateWorkspaceChip() must be called before renderSessionList()")


if __name__ == '__main__':
    unittest.main()
