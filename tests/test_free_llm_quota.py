"""
Test Suite: Curated Free LLM Token Quota & Auto-Failover Engine (V8)
Verifies:
1. Company-wide free token quota ceiling (5,300,000 TPD across all 6 curated providers).
2. All 11 bots tracked with explicit 'used / limit' metrics (TPD, TPM, RPM), primary/fallback models,
   failover triggering, and failback reloaded states.
3. REST API endpoints: GET /api/free_llm_quota and POST /api/failover_check.
4. Backward compatibility with existing economy reports and legacy database/dashboard consumers.
"""
import io
import json
import tempfile
import os
import pytest

from engine.token_economy import (
    TokenEconomyEngine,
    FREE_LLM_PROVIDERS,
    TOTAL_FREE_QUOTA_CEILING_DAILY,
    BOT_DEFAULT_CONFIG,
    get_bot_quotas,
    get_bot_historical_token_table,
    QuotaList
)
from data.database import CompanyDatabase
from server import V7RequestHandler


class MockServerHandler(V7RequestHandler):
    """Mock HTTP Request Handler to test endpoints without spinning up a live socket."""
    def __init__(self, method: str, path: str, body_dict: dict | None = None):
        self.command = method
        self.path = path
        self.request_version = "HTTP/1.1"
        self.close_connection = True
        self.headers = {"Content-Type": "application/json"}
        payload_bytes = json.dumps(body_dict or {}).encode("utf-8") if body_dict else b""
        self.headers["Content-Length"] = str(len(payload_bytes))
        self.rfile = io.BytesIO(payload_bytes)
        self.wfile = io.BytesIO()
        self._response_status = 200
        self._response_headers = {}

    def send_response(self, code, message=None):
        self._response_status = code

    def send_header(self, keyword, value):
        self._response_headers[keyword] = value

    def end_headers(self):
        pass

    def get_json_response(self) -> dict:
        self.wfile.seek(0)
        raw = self.wfile.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def test_free_llm_providers_and_company_ceiling():
    """Verify the 6 curated providers from awesome-free-llm-apis and 5,300,000 TPD ceiling."""
    expected_providers = {"cerebras", "groq", "sambanova", "gemini", "openrouter", "mistral"}
    assert set(FREE_LLM_PROVIDERS.keys()) == expected_providers

    assert TOTAL_FREE_QUOTA_CEILING_DAILY == 5300000

    # Verify individual limits
    assert FREE_LLM_PROVIDERS["cerebras"]["daily_token_limit"] == 1000000
    assert FREE_LLM_PROVIDERS["groq"]["daily_token_limit"] == 500000
    assert FREE_LLM_PROVIDERS["sambanova"]["daily_token_limit"] == 1000000
    assert FREE_LLM_PROVIDERS["gemini"]["daily_token_limit"] == 1500000
    assert FREE_LLM_PROVIDERS["openrouter"]["daily_token_limit"] == 800000
    assert FREE_LLM_PROVIDERS["mistral"]["daily_token_limit"] == 500000


def test_all_11_bots_quotas_and_metrics():
    """Verify all 11 bots return explicit 'used / limit' metrics and exact schema fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_quotas.db")
        db = CompanyDatabase(db_path)
        quotas = get_bot_quotas(db)

        assert isinstance(quotas, QuotaList)
        assert len(quotas) == 11

        expected_bot_ids = [
            "ag_cio", "ag_cos", "ag_news", "ag_quant", "ag_ta",
            "ag_macro", "ag_bull", "ag_bear", "ag_risk", "ag_bot", "ag_venture"
        ]
        assert [b["agent_id"] for b in quotas] == expected_bot_ids

        # Test dual list & dict indexing on QuotaList
        assert quotas[0]["agent_id"] == "ag_cio"
        assert quotas["ag_cio"]["name"] == "Arthur Pendelton"
        assert "ag_quant" in quotas

        for b in quotas:
            # Required core fields from prompt specifications
            assert "primary_provider" in b
            assert b["primary_provider"] in ("Cerebras", "Groq", "SambaNova", "Gemini", "OpenRouter", "Mistral")
            assert "primary_model" in b and len(b["primary_model"]) > 0
            assert "rpm_limit" in b and b["rpm_limit"] > 0
            assert "tpm_limit" in b and b["tpm_limit"] > 0
            assert "tpd_limit" in b and b["tpd_limit"] > 0
            assert "tokens_used_today" in b and b["tokens_used_today"] >= 0
            assert "tokens_used_total" in b and b["tokens_used_total"] >= 148000
            assert "usage_vs_cap_display" in b
            assert f"{b['tokens_used_today']:,} / {b['tpd_limit']:,} TPD" == b["usage_vs_cap_display"]
            assert "fallback_provider" in b
            assert "fallback_model" in b
            assert "is_failover_active" in b and isinstance(b["is_failover_active"], bool)
            assert "failback_eligible" in b and isinstance(b["failback_eligible"], bool)
            assert b["status"] in ("PRIMARY_ACTIVE", "FAILOVER_ACTIVE", "RELOADED_PRIMARY")
            # Realistic organic daily load (10% - 65% green load, no premature 100% caps)
            assert 10.0 <= b["cap_pct"] <= 65.0
            assert b["is_failover_active"] is False
            assert b["status"] == "PRIMARY_ACTIVE"

        assert quotas["ag_cio"]["tokens_used_today"] == 360000
        assert quotas["ag_quant"]["tokens_used_today"] == 520000
        assert quotas["ag_macro"]["tokens_used_today"] == 290000


def test_auto_failover_and_failback_simulation():
    """Verify auto-failover switching and failback reload to primary provider."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_failover.db")
        db = CompanyDatabase(db_path)
        econ = TokenEconomyEngine(db)

        # 1. Initially all bots are normal (PRIMARY_ACTIVE)
        econ.reset_provider_limits()
        rep1 = econ.get_economy_report()
        cio_quota = rep1["bot_quotas"]["ag_cio"]
        assert cio_quota["is_failover_active"] is False
        assert cio_quota["status"] == "PRIMARY_ACTIVE"
        assert cio_quota["current_provider"] == "Cerebras"
        assert cio_quota["primary_provider"] == "Cerebras"

        # 2. Trigger failover on ag_cio via check_failover_status API
        fail_res = econ.check_failover_status({"action": "failover", "agent_id": "ag_cio"})
        assert fail_res["status"] == "OK"
        cio_failed = fail_res["bot_quotas"]["ag_cio"]
        assert cio_failed["is_failover_active"] is True
        assert cio_failed["status"] == "FAILOVER_ACTIVE"
        assert cio_failed["current_provider"] == "Groq"  # Switched to fallback
        assert cio_failed["current_model"] == "Llama-3.3-70B-Versatile"

        # 3. Trigger failback / reset on ag_cio, returning to primary
        restore_res = econ.check_failover_status({"action": "failback", "agent_id": "ag_cio"})
        assert restore_res["status"] == "OK"
        cio_restored = restore_res["bot_quotas"]["ag_cio"]
        assert cio_restored["is_failover_active"] is False
        assert cio_restored["status"] == "RELOADED_PRIMARY"
        assert cio_restored["current_provider"] == "Cerebras"
        assert cio_restored["failback_eligible"] is True

        # Clean up
        econ.reset_provider_limits()


def test_api_endpoints_free_llm_quota_and_failover_check():
    """Verify HTTP GET /api/free_llm_quota and POST /api/failover_check."""
    # 1. Test GET /api/free_llm_quota
    get_handler = MockServerHandler("GET", "/api/free_llm_quota")
    get_handler.do_GET()
    assert get_handler._response_status == 200
    res_get = get_handler.get_json_response()

    assert "total_company_used_today" in res_get
    assert res_get["total_company_ceiling_daily"] == 5300000
    assert "total_company_display" in res_get
    assert "Tokens/วัน" in res_get["total_company_display"]
    assert "total_lifetime_tokens" in res_get and res_get["total_lifetime_tokens"] > 0
    assert "total_usd_saved" in res_get and res_get["total_usd_saved"] > 0.0
    assert "bot_quotas" in res_get
    assert len(res_get["bot_quotas"]) == 11

    # 2. Test POST /api/failover_check
    post_handler = MockServerHandler("POST", "/api/failover_check", {
        "action": "trip",
        "agent_id": "ag_quant"
    })
    post_handler.do_POST()
    assert post_handler._response_status == 200
    res_post = post_handler.get_json_response()

    assert res_post["status"] == "OK"
    assert "bot_quotas" in res_post
    quant_quota = next(b for b in res_post["bot_quotas"] if b["agent_id"] == "ag_quant")
    assert quant_quota["is_failover_active"] is True
    assert quant_quota["status"] == "FAILOVER_ACTIVE"
    assert quant_quota["current_provider"] == "SambaNova"

    # Reset
    reset_handler = MockServerHandler("POST", "/api/failover_check", {"action": "reset_all"})
    reset_handler.do_POST()
    assert reset_handler._response_status == 200


def test_backward_compatibility_get_economy_report():
    """Verify get_economy_report() maintains all legacy fields for existing tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_compat.db")
        db = CompanyDatabase(db_path)
        econ = TokenEconomyEngine(db)
        rep = econ.get_economy_report()

        # Legacy fields
        assert rep["status"] == "ok"
        assert rep["is_uncapped"] is True
        assert rep["token_limit_mode"] == "UNCAPPED_REAL_USAGE"
        assert "daily_budget_tokens" in rep
        assert "total_tokens_used" in rep
        assert "remaining_tokens" in rep
        assert "utilization_pct" in rep
        assert "agent_allocations" in rep and len(rep["agent_allocations"]) == 11
        assert "leaderboard_by_usage" in rep
        assert "available_models" in rep
        assert "bot_historical_token_table" in rep and len(rep["bot_historical_token_table"]) == 11

        # Confirm bot_historical_token_table maintains nested dict primary_provider
        first_hist = rep["bot_historical_token_table"][0]
        assert isinstance(first_hist["primary_provider"], dict)
        assert "key" in first_hist["primary_provider"]
        assert "name" in first_hist["primary_provider"]
        assert "daily_limit" in first_hist["primary_provider"]
