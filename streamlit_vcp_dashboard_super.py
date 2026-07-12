from __future__ import annotations

import html
import json
import re
from datetime import timedelta
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="StockGita Private Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_OUTPUT_DIR = Path("outputs")
APP_BUILD = "private-v1-latest-data"


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
  --bg1: #08111f;
  --bg2: #111827;
  --card: rgba(255,255,255,0.075);
  --card2: rgba(255,255,255,0.105);
  --border: rgba(255,255,255,0.14);
  --text: #f8fafc;
  --muted: rgba(248,250,252,0.70);
  --faint: rgba(248,250,252,0.52);
  --gold: #f5c451;
  --green: #28d17c;
  --red: #ff6b6b;
  --blue: #6ea8fe;
  --violet: #b79cff;
  --amber: #ffb454;
}
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 12% 0%, rgba(110,168,254,0.20), rgba(110,168,254,0.00) 34%),
    radial-gradient(circle at 92% 8%, rgba(245,196,81,0.16), rgba(245,196,81,0.00) 28%),
    linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%) !important;
  color: var(--text) !important;
}
.block-container {max-width: 1520px; padding-top: 0.75rem; padding-left: 1.0rem; padding-right: 1.0rem; padding-bottom: 2rem;}
#MainMenu, footer, header {visibility: hidden;}
.private-hero, .metric-card, .stock-card, .panel-card, .data-card {
  border: 1px solid var(--border);
  background: linear-gradient(180deg, var(--card2), var(--card));
  border-radius: 22px;
  padding: 0.95rem 1rem;
  box-shadow: 0 18px 42px rgba(0,0,0,0.23);
  backdrop-filter: blur(12px);
}
.private-hero {margin-bottom: 0.75rem;}
.brand {font-size: 2.25rem; font-weight: 950; letter-spacing: -0.055em; line-height: 1;}
.brand span {color: var(--gold);}
.subtitle {color: var(--muted); font-size: 0.94rem; line-height: 1.35; margin-top: 0.32rem;}
.kicker {font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--faint); font-weight: 900;}
.metric-value {font-size: 1.38rem; font-weight: 950; line-height: 1.08; margin-top: 0.14rem; color: var(--text);}
.metric-sub {font-size: 0.82rem; color: var(--muted); line-height: 1.30; margin-top: 0.20rem;}
.section-title {font-size: 1.25rem; font-weight: 950; margin: 1.15rem 0 0.25rem 0; letter-spacing: -0.025em;}
.section-note {font-size: 0.88rem; color: var(--muted); margin-bottom: 0.68rem;}
.stock-card {margin: 0.75rem 0 1.05rem 0; padding: 0.9rem;}
.stock-head {display:flex; justify-content:space-between; gap:0.8rem; align-items:flex-start;}
.stock-name {font-size: 1.05rem; font-weight: 950; line-height:1.16;}
.stock-meta {font-size: 0.86rem; color: var(--muted); line-height:1.30; margin-top:0.18rem;}
.rank-badge {min-width: 72px; text-align:right;}
.rank-label {font-size: 0.65rem; color: var(--faint); font-weight:900; text-transform:uppercase;}
.rank-value {font-size: 1.34rem; color: var(--gold); font-weight:950; line-height:1; margin-top:0.08rem;}
.badge-strip {display:flex; flex-wrap:wrap; gap:0.35rem; margin-top:0.58rem;}
.badge {display:inline-flex; align-items:center; border-radius:999px; border:1px solid var(--border); padding:0.20rem 0.52rem; font-size:0.72rem; font-weight:900; color:var(--text); background:rgba(255,255,255,0.07);}
.badge-green {color:var(--green); border-color:rgba(40,209,124,0.36); background:rgba(40,209,124,0.10);}
.badge-red {color:var(--red); border-color:rgba(255,107,107,0.36); background:rgba(255,107,107,0.10);}
.badge-gold {color:var(--gold); border-color:rgba(245,196,81,0.40); background:rgba(245,196,81,0.10);}
.badge-blue {color:var(--blue); border-color:rgba(110,168,254,0.38); background:rgba(110,168,254,0.10);}
.badge-violet {color:var(--violet); border-color:rgba(183,156,255,0.36); background:rgba(183,156,255,0.10);}
.signal-line {font-size:0.86rem; color:var(--muted); line-height:1.32; margin-top:0.36rem;}
.failure-line {font-size:0.80rem; color:rgba(255,190,190,0.95); line-height:1.35; margin-top:0.42rem; border-left:3px solid rgba(255,107,107,0.50); padding-left:0.55rem;}
.chart-grid {display:grid; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap:0.8rem; margin-top:0.72rem;}
.chart-panel {border:1px solid var(--border); border-radius:16px; overflow:hidden; background:#fff;}
.chart-title {font-size:0.82rem; color:#172033; font-weight:950; text-align:center; padding:0.40rem 0.5rem; background:#eef5ff; border-bottom:1px solid rgba(0,0,0,0.08);}
.chart-panel img {width:100%; display:block; height:auto;}
.chart-missing {padding:1.1rem; text-align:center; color:var(--muted); border:1px dashed var(--border); border-radius:16px; margin-top:0.72rem;}
.stage1 {border-color: rgba(110,168,254,0.34);}
.stage2 {border-color: rgba(40,209,124,0.34);}
.stage3 {border-color: rgba(255,180,84,0.36);}
.stage4 {border-color: rgba(255,107,107,0.34);}
.failed {border-color: rgba(255,107,107,0.58); box-shadow: 0 18px 42px rgba(255,107,107,0.08);}
.stDataFrame {border-radius: 16px; overflow:hidden;}
.small-note {font-size:0.82rem; color:var(--muted); line-height:1.35;}
.private-warning {border-left:4px solid var(--gold); background:rgba(245,196,81,0.08); padding:0.72rem 0.85rem; border-radius:14px; font-size:0.86rem; color:var(--muted); margin:0.7rem 0;}
@media(max-width: 900px) {
  .chart-grid {grid-template-columns: 1fr;}
  .brand {font-size:1.7rem;}
  .block-container {padding-left:0.55rem; padding-right:0.55rem;}
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------
def esc(value) -> str:
    try:
        if pd.isna(value):
            return "-"
    except Exception:
        pass
    return html.escape(str(value))


@st.cache_data(show_spinner=False)
def read_csv_cached(path: str, mtime_ns: int) -> pd.DataFrame:
    return pd.read_csv(path)


def safe_read(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return read_csv_cached(str(path), path.stat().st_mtime_ns)
    except Exception:
        return pd.DataFrame()


def boolish(value) -> bool:
    if isinstance(value, bool):
        return value
    try:
        if pd.isna(value):
            return False
    except Exception:
        pass
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "y", "t"}


def normalize_ticker(value) -> str:
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE"}:
        return ""
    if text.startswith("^") or text.endswith(".NS"):
        return text
    return f"{text}.NS"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame() if df is None else df
    out = df.copy()
    if "Company Name" not in out.columns:
        for col in ["Company Name_x", "Company Name_y", "company", "company_name", "name", "stock_name"]:
            if col in out.columns:
                out["Company Name"] = out[col]
                break
    if "Industry" not in out.columns:
        for col in ["Industry_x", "Industry_y", "industry", "sector", "Sector"]:
            if col in out.columns:
                out["Industry"] = out[col]
                break
    if "ticker" not in out.columns:
        for col in ["Ticker", "symbol", "Symbol", "SYMBOL"]:
            if col in out.columns:
                out["ticker"] = out[col]
                break
    if "ticker" in out.columns:
        out["ticker"] = out["ticker"].apply(normalize_ticker)
    if "Company Name" not in out.columns and "ticker" in out.columns:
        out["Company Name"] = out["ticker"].astype(str).str.replace(".NS", "", regex=False)
    if "Industry" not in out.columns:
        out["Industry"] = "Unknown"
    return out


def numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def ensure_rank(df: pd.DataFrame, score_col: str = "final_combined_score") -> pd.DataFrame:
    if df.empty:
        return df
    out = normalize_columns(df)
    rank_col = next((c for c in ["current_rank", "stock_rank", "final_rank", "combined_rank", "rank", "rs_rank"] if c in out.columns), None)
    if rank_col:
        out["current_rank"] = pd.to_numeric(out[rank_col], errors="coerce")
    else:
        sort_col = next((c for c in [score_col, "internal_quality_score", "structure_score", "final_combined_score", "combined_score"] if c in out.columns), None)
        if sort_col:
            out = out.sort_values(sort_col, ascending=False, na_position="last").reset_index(drop=True)
        out["current_rank"] = range(1, len(out) + 1)
    return out


def canonical_stage(value) -> str:
    text = str(value or "").strip()
    if text in {"Stage 2 Failed", "Failed Stage 2", "Failed Stage 2 Setup"}:
        return "Failed Stage 2"
    if text in {"Stage 1", "Stage 2", "Stage 3", "Stage 4", "Not Sure"}:
        return text
    if "failed" in text.lower() and "stage 2" in text.lower():
        return "Failed Stage 2"
    if "stage 1" in text.lower():
        return "Stage 1"
    if "stage 2" in text.lower():
        return "Stage 2"
    if "stage 3" in text.lower():
        return "Stage 3"
    if "stage 4" in text.lower():
        return "Stage 4"
    return "Not Sure" if not text or text.lower() in {"nan", "none", "unknown"} else text


def public_stage_label(row: pd.Series) -> str:
    existing = str(row.get("public_stage_label", "") or "").strip()
    if existing and existing.lower() not in {"nan", "none"}:
        return existing.replace("Stage 2 Failed", "Failed Stage 2")
    stage = canonical_stage(row.get("stage", "Not Sure"))
    variant = str(row.get("stage_variant", row.get("stage_classification", "")) or "").lower()
    if stage == "Stage 1":
        return "Stage 1"
    if stage == "Stage 2":
        return "Stage 2 - Extended" if "extended" in variant else "Stage 2 - Advancing"
    if stage == "Stage 3":
        late_words = ["late", "distribution", "damage", "failed", "break"]
        return "Stage 3 Late" if any(w in variant for w in late_words) else "Stage 3 Early"
    if stage == "Stage 4":
        return "Stage 4"
    if stage == "Failed Stage 2":
        return "Failed Stage 2"
    return "Not Sure - Unclear"


def structure_score(row: pd.Series) -> float:
    for col in ["structure_score", "internal_quality_score", "final_combined_score", "combined_score"]:
        val = pd.to_numeric(row.get(col), errors="coerce")
        if pd.notna(val):
            return round(float(max(0, min(100, val))), 2)
    return 0.0


def volume_pattern_display(row: pd.Series) -> str:
    existing = str(row.get("volume_pattern_display", "") or "").strip()
    if existing and existing.lower() not in {"nan", "none"}:
        return existing
    ratio = pd.to_numeric(row.get("weekly_volume_ratio", row.get("volume_dryup_ratio")), errors="coerce")
    if pd.isna(ratio):
        return "Volume: not available"
    ratio = float(ratio)
    if ratio <= 0.8:
        return f"Volume Drying Up ({ratio:.2f}x vs 10W Avg)"
    if ratio >= 1.2:
        return f"Volume Expanding ({ratio:.2f}x vs 10W Avg)"
    return f"Volume Normal ({ratio:.2f}x vs 10W Avg)"


def nifty_outperformance_label(row: pd.Series) -> str:
    existing = str(row.get("nifty_3m_outperformance_label", "") or "").strip()
    if existing and existing.lower() not in {"nan", "none"}:
        return existing
    val = pd.to_numeric(row.get("nifty_3m_outperformance_pct", row.get("rs_3m_pct")), errors="coerce")
    if pd.isna(val):
        return "Nifty 3M relative performance: not available"
    val = float(val)
    return (f"Outperformed Nifty by {abs(val):.2f}% in 3 Months" if val >= 0 else f"Underperformed Nifty by {abs(val):.2f}% in 3 Months")


def relative_strength_label(row: pd.Series) -> str:
    existing = str(row.get("relative_strength_label", "") or "").strip()
    if existing and existing.lower() not in {"nan", "none"}:
        return existing
    val = pd.to_numeric(row.get("rs_3m_pct"), errors="coerce")
    if pd.isna(val):
        return "Unknown"
    if val >= 15:
        return "Very Strong"
    if val >= 5:
        return "Strong"
    if val > -5:
        return "Neutral"
    return "Weak"


def company_label(row: pd.Series) -> str:
    company = str(row.get("Company Name", row.get("ticker", "Stock")) or "Stock").strip()
    ticker = str(row.get("ticker", "") or "").replace(".NS", "").strip()
    return f"{company} ({ticker})" if ticker and ticker not in company else company


def prepare_internal_df(internal: pd.DataFrame) -> pd.DataFrame:
    if internal.empty:
        return internal
    out = normalize_columns(internal)
    rename_map = {
        "leader_score": "internal_leader_score",
        "trend_score": "internal_trend_score",
        "setup_score": "internal_setup_score",
        "risk_score": "internal_risk_score",
        "quality_score": "internal_quality_score",
        "is_true_leader": "internal_is_true_leader",
        "is_proper_setup": "internal_is_proper_setup",
        "is_low_risk": "internal_is_low_risk",
        "is_buyable_setup_internal": "internal_is_buyable_setup",
        "failure_reasons": "internal_failure_reasons",
    }
    for src, dst in rename_map.items():
        if src in out.columns and dst not in out.columns:
            out = out.rename(columns={src: dst})
    return out


def merge_internal(combined: pd.DataFrame, internal: pd.DataFrame) -> pd.DataFrame:
    combined = ensure_rank(combined)
    if combined.empty:
        return combined
    internal = prepare_internal_df(internal)
    if internal.empty or "ticker" not in internal.columns:
        for col in [
            "internal_leader_score", "internal_trend_score", "internal_setup_score", "internal_risk_score",
            "internal_quality_score", "internal_is_true_leader", "internal_is_proper_setup",
            "internal_is_low_risk", "internal_is_buyable_setup", "internal_failure_reasons",
            "setup_quality_label", "technical_flags", "risk_pct", "setup_state",
        ]:
            if col not in combined.columns:
                combined[col] = pd.NA
        return combined
    wanted = ["ticker"] + [c for c in [
        "internal_leader_score", "internal_trend_score", "internal_setup_score", "internal_risk_score",
        "internal_quality_score", "internal_is_true_leader", "internal_is_proper_setup",
        "internal_is_low_risk", "internal_is_buyable_setup", "internal_failure_reasons",
        "setup_quality_label", "technical_flags", "risk_pct", "setup_state",
        "leader_score", "trend_score", "setup_score", "risk_score", "quality_score",
    ] if c in internal.columns]
    internal = internal[wanted].drop_duplicates("ticker")
    out = combined.merge(internal, on="ticker", how="left", suffixes=("", "_internal"))
    # If columns came from older names, copy them into the canonical internal names.
    fallback_pairs = [
        ("leader_score", "internal_leader_score"), ("trend_score", "internal_trend_score"),
        ("setup_score", "internal_setup_score"), ("risk_score", "internal_risk_score"),
        ("quality_score", "internal_quality_score"),
    ]
    for src, dst in fallback_pairs:
        if src in out.columns and dst not in out.columns:
            out[dst] = out[src]
        elif src in out.columns and dst in out.columns:
            out[dst] = out[dst].where(out[dst].notna(), out[src])
    return out


def engine_timestamp(outdir: Path) -> str:
    path = outdir / "engine_run_metadata.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            raw = data.get("engine_ran_at_ist") or data.get("engine_ran_at_utc")
            if raw:
                ts = pd.Timestamp(raw)
                if ts.tzinfo is None:
                    ts = ts.tz_localize("Asia/Kolkata")
                else:
                    ts = ts.tz_convert("Asia/Kolkata")
                return ts.strftime("%d-%b-%Y %I:%M %p IST").replace(" 0", " ")
        except Exception:
            pass
    files = [p for p in outdir.glob("*.csv")]
    if files:
        ts = pd.Timestamp.fromtimestamp(max(p.stat().st_mtime for p in files), tz="Asia/Kolkata")
        return ts.strftime("%d-%b-%Y %I:%M %p IST").replace(" 0", " ")
    return "Not available"


def load_data(outdir: Path):
    combined = safe_read(outdir / "vcp_combined_ranked.csv")
    internal = safe_read(outdir / "internal_setup_ranked.csv")
    daily = safe_read(outdir / "vcp_daily_ranked.csv")
    weekly = safe_read(outdir / "vcp_weekly_ranked.csv")
    industry = safe_read(outdir / "industry_strength.csv")
    regime = safe_read(outdir / "market_regime.csv")
    changes = safe_read(outdir / "stock_changes.csv")
    moves = safe_read(outdir / "stock_price_moves.csv")
    history = safe_read(outdir / "stage_action_history.csv")
    interesting = safe_read(outdir / "interesting20_latest.csv")

    num_cols = [
        "current_rank", "structure_score", "final_combined_score", "combined_score",
        "internal_leader_score", "internal_trend_score", "internal_setup_score", "internal_risk_score",
        "internal_quality_score", "rs_3m_pct", "rs_6m_pct", "nifty_3m_outperformance_pct",
        "volume_dryup_ratio", "weekly_volume_ratio", "breakout_volume_ratio", "risk_pct",
        "avg_turnover_inr", "change_1d_pct", "change_1w_pct", "change_1m_pct", "change_ytd_pct",
    ]
    combined = merge_internal(normalize_columns(combined), normalize_columns(internal))
    combined = numeric(combined, num_cols)
    daily = numeric(ensure_rank(normalize_columns(daily), "final_daily_score"), num_cols)
    weekly = numeric(ensure_rank(normalize_columns(weekly), "final_weekly_score"), num_cols)
    industry = numeric(ensure_rank(normalize_columns(industry), "avg_combined_score"), ["current_rank", "avg_combined_score", "rs_rank", "stock_count", "strong_combined", "actionable_daily", "actionable_weekly"])
    changes = numeric(ensure_rank(normalize_columns(changes)), num_cols + ["rank_change", "combined_score_change"])
    moves = numeric(normalize_columns(moves), num_cols + ["last_close"])
    history = numeric(normalize_columns(history), num_cols)
    interesting = normalize_columns(interesting)

    if not combined.empty:
        combined["stage"] = combined.get("stage", "Not Sure").apply(canonical_stage)
        combined["public_stage_label"] = combined.apply(public_stage_label, axis=1)
        combined["structure_score_public"] = combined.apply(structure_score, axis=1)
        combined["volume_pattern_display"] = combined.apply(volume_pattern_display, axis=1)
        combined["nifty_3m_outperformance_label"] = combined.apply(nifty_outperformance_label, axis=1)
        combined["relative_strength_label"] = combined.apply(relative_strength_label, axis=1)
        combined["internal_is_true_leader"] = combined.get("internal_is_true_leader", False).apply(boolish)
        combined["internal_is_proper_setup"] = combined.get("internal_is_proper_setup", False).apply(boolish)
        combined["internal_is_low_risk"] = combined.get("internal_is_low_risk", False).apply(boolish)
        combined["internal_is_buyable_setup"] = combined.get("internal_is_buyable_setup", False).apply(boolish)
    return combined, daily, weekly, industry, regime, changes, moves, history, interesting


# -----------------------------------------------------------------------------
# Chart helpers
# -----------------------------------------------------------------------------
def chart_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", str(value or "")).lower()


@st.cache_data(show_spinner=False)
def build_chart_index(chart_dir: str, suffix: str, mtime_ns: int) -> dict[str, str]:
    path = Path(chart_dir)
    if not path.exists():
        return {}
    out = {}
    for img in path.glob(f"*{suffix}"):
        stem = img.name[:-len(suffix)] if img.name.endswith(suffix) else img.stem
        for key in {stem.lower(), chart_key(stem), chart_key(stem.replace("_", ".")), img.name.lower()}:
            if key:
                out.setdefault(key, str(img))
    return out


@st.cache_data(show_spinner=False)
def image_bytes(path: str, mtime_ns: int) -> bytes:
    return Path(path).read_bytes()


def resolve_chart(index: dict[str, str], ticker: str) -> Optional[Path]:
    ticker = str(ticker or "").strip()
    raw = ticker.replace(".NS", "")
    candidates = {
        ticker, raw, ticker.replace(".", "_"), raw.replace(".", "_"),
        re.sub(r"[^A-Za-z0-9]+", "_", ticker), re.sub(r"[^A-Za-z0-9]+", "_", raw),
        re.sub(r"[^A-Za-z0-9]+", "", ticker), re.sub(r"[^A-Za-z0-9]+", "", raw),
    }
    for cand in candidates:
        for key in [cand.lower(), chart_key(cand)]:
            if key in index:
                return Path(index[key])
    raw_key = chart_key(raw)
    if raw_key:
        for key, p in index.items():
            if raw_key in key:
                return Path(p)
    return None


def chart_img_html(index: dict[str, str], ticker: str, title: str) -> str:
    path = resolve_chart(index, ticker)
    if not path:
        return f'<div class="chart-missing">{esc(title)} chart not available</div>'
    try:
        b = image_bytes(str(path), path.stat().st_mtime_ns)
        import base64
        uri = "data:image/png;base64," + base64.b64encode(b).decode("ascii")
        return f'<div class="chart-panel"><div class="chart-title">{esc(title)}</div><img src="{uri}" alt="{esc(title)} chart"></div>'
    except Exception:
        return f'<div class="chart-missing">{esc(title)} chart could not be loaded</div>'


# -----------------------------------------------------------------------------
# Analysis helpers
# -----------------------------------------------------------------------------
def stage_counts(combined: pd.DataFrame) -> dict[str, int]:
    if combined.empty or "stage" not in combined.columns:
        return {"Stage 1": 0, "Stage 2": 0, "Stage 3": 0, "Stage 4": 0, "Failed Stage 2": 0, "Not Sure": 0}
    counts = combined["stage"].astype(str).apply(canonical_stage).value_counts()
    return {k: int(counts.get(k, 0)) for k in ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Failed Stage 2", "Not Sure"]}


def market_mood(regime: pd.DataFrame) -> str:
    if not regime.empty and "regime_label" in regime.columns:
        raw = str(regime.iloc[0].get("regime_label", "")).strip().lower()
        return {
            "strong_risk_on": "Strong Risk On",
            "risk_on": "Risk On",
            "mixed": "Mixed",
            "risk_off": "Risk Off",
            "strong_risk_off": "Strong Risk Off",
        }.get(raw, raw.replace("_", " ").title())
    return "Mixed"


def breadth_text(regime: pd.DataFrame) -> str:
    if regime.empty:
        return "Breadth not available"
    row = regime.iloc[0]
    vals = []
    for col, label in [("breadth_above_20_pct", "20DMA"), ("breadth_above_50_pct", "50DMA"), ("breadth_above_200_pct", "200DMA")]:
        val = pd.to_numeric(row.get(col), errors="coerce")
        if pd.notna(val):
            vals.append(f"{float(val):.0f}% above {label}")
    return " · ".join(vals) if vals else "Breadth not available"


def stage_history_failed_7d(history: pd.DataFrame, combined: pd.DataFrame) -> pd.DataFrame:
    current_failed = pd.DataFrame()
    if not combined.empty and "stage" in combined.columns:
        current_failed = combined[combined["stage"].apply(canonical_stage).eq("Failed Stage 2")].copy()
        if not current_failed.empty:
            current_failed["failed_seen_date"] = "Current"
    if history.empty or "ticker" not in history.columns:
        return current_failed
    hist = normalize_columns(history).copy()
    date_col = "snapshot_date" if "snapshot_date" in hist.columns else None
    if date_col is None:
        return current_failed
    hist[date_col] = pd.to_datetime(hist[date_col], errors="coerce")
    hist = hist.dropna(subset=[date_col, "ticker"])
    if hist.empty:
        return current_failed
    latest = hist[date_col].max().normalize()
    start = latest - pd.Timedelta(days=6)
    stage_series = hist.get("stage", pd.Series("", index=hist.index)).astype(str).apply(canonical_stage)
    if "public_stage_label" in hist.columns:
        public_failed = hist["public_stage_label"].astype(str).str.contains("Failed Stage 2|Stage 2 Failed", case=False, na=False)
    else:
        public_failed = pd.Series(False, index=hist.index)
    failed = hist[(hist[date_col] >= start) & ((stage_series == "Failed Stage 2") | public_failed)].copy()
    if failed.empty:
        return current_failed
    latest_failed = failed.sort_values(date_col).drop_duplicates("ticker", keep="last")[["ticker", date_col]].copy()
    latest_failed["failed_seen_date"] = latest_failed[date_col].dt.date.astype(str)
    if not combined.empty and "ticker" in combined.columns:
        enrich = combined.drop_duplicates("ticker")
        out = latest_failed[["ticker", "failed_seen_date"]].merge(enrich, on="ticker", how="left")
        # Fill company/stage from history if not present.
        fallback = failed.drop_duplicates("ticker", keep="last").set_index("ticker")
        for col in ["Company Name", "Industry", "stage", "stage_variant", "public_stage_label"]:
            if col not in out.columns:
                out[col] = out["ticker"].map(fallback[col]) if col in fallback.columns else pd.NA
            else:
                out[col] = out[col].where(out[col].notna(), out["ticker"].map(fallback[col]) if col in fallback.columns else pd.NA)
        out["stage"] = "Failed Stage 2"
        out["public_stage_label"] = "Failed Stage 2"
        return ensure_rank(out)
    return latest_failed


def build_industry_rank_table(industry: pd.DataFrame, combined: pd.DataFrame) -> pd.DataFrame:
    if industry.empty:
        if combined.empty or "Industry" not in combined.columns:
            return pd.DataFrame()
        out = combined.groupby("Industry").agg(stock_count=("ticker", "count"), stage2_count=("stage", lambda s: int((s.astype(str) == "Stage 2").sum()))).reset_index()
        out = out.sort_values(["stage2_count", "stock_count"], ascending=[False, False]).reset_index(drop=True)
        out["current_rank"] = range(1, len(out) + 1)
        return out
    out = ensure_rank(industry, "avg_combined_score")
    if not combined.empty and "Industry" in combined.columns:
        counts = combined.groupby("Industry").agg(
            stock_count=("ticker", "count"),
            stage2_count=("stage", lambda s: int((s.astype(str) == "Stage 2").sum())),
            failed_stage2_count=("stage", lambda s: int((s.astype(str).apply(canonical_stage) == "Failed Stage 2").sum())),
        ).reset_index()
        out = out.merge(counts, on="Industry", how="left")
    for col in ["stock_count", "stage2_count", "failed_stage2_count"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0).astype(int)
    return out.sort_values("current_rank", ascending=True, na_position="last").reset_index(drop=True)


def industry_rank_for(row: pd.Series, ind_table: pd.DataFrame) -> str:
    if ind_table.empty or "Industry" not in ind_table.columns:
        return "-"
    name = str(row.get("Industry", "") or "").strip().lower()
    if not name:
        return "-"
    temp = ind_table.copy()
    temp["_key"] = temp["Industry"].astype(str).str.strip().str.lower()
    match = temp[temp["_key"].eq(name)]
    if match.empty:
        return "-"
    val = pd.to_numeric(match.iloc[0].get("current_rank"), errors="coerce")
    return str(int(val)) if pd.notna(val) else "-"


def latest_interesting_by_rank(combined: pd.DataFrame) -> pd.DataFrame:
    if combined.empty:
        return combined
    return ensure_rank(combined).sort_values("current_rank", ascending=True, na_position="last").head(20).reset_index(drop=True)


# -----------------------------------------------------------------------------
# Rendering helpers
# -----------------------------------------------------------------------------
def render_metric(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
<div class="metric-card">
  <div class="kicker">{esc(title)}</div>
  <div class="metric-value">{esc(value)}</div>
  <div class="metric-sub">{esc(subtitle)}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def badge(label: str, style: str = "") -> str:
    style_class = f" badge-{style}" if style else ""
    return f'<span class="badge{style_class}">{esc(label)}</span>'


def stage_class(stage: str) -> str:
    stage = canonical_stage(stage)
    return {
        "Stage 1": "stage1",
        "Stage 2": "stage2",
        "Stage 3": "stage3",
        "Stage 4": "stage4",
        "Failed Stage 2": "failed",
    }.get(stage, "")


def render_stock_card(row: pd.Series, idx: int, daily_index: dict[str, str], weekly_index: dict[str, str], ind_table: pd.DataFrame, show_charts: bool = True):
    ticker = str(row.get("ticker", "") or "").strip()
    stage = canonical_stage(row.get("stage", "Not Sure"))
    rank = pd.to_numeric(row.get("current_rank"), errors="coerce")
    rank_text = f"#{int(rank)}" if pd.notna(rank) else "-"
    internal_score = pd.to_numeric(row.get("internal_quality_score"), errors="coerce")
    public_score = structure_score(row)
    failures = str(row.get("internal_failure_reasons", "") or "").strip()
    technical_flags = str(row.get("technical_flags", "") or "").strip()
    setup_state = str(row.get("setup_state", "") or "").strip()

    badges = []
    badges.append(badge(public_stage_label(row), "gold" if stage == "Stage 2" else "red" if stage in {"Stage 4", "Failed Stage 2"} else "blue"))
    if boolish(row.get("internal_is_buyable_setup", False)):
        badges.append(badge("Internal Buyable Setup", "green"))
    if boolish(row.get("internal_is_true_leader", False)):
        badges.append(badge("True Leader", "green"))
    if boolish(row.get("internal_is_proper_setup", False)):
        badges.append(badge("Proper Setup", "blue"))
    if boolish(row.get("internal_is_low_risk", False)):
        badges.append(badge("Low Risk", "green"))
    if stage == "Failed Stage 2":
        badges.append(badge("Public Failed Stage 2", "red"))
    if setup_state:
        badges.append(badge(f"Setup: {setup_state}", "violet"))
    ind_rank = industry_rank_for(row, ind_table)
    if ind_rank != "-":
        badges.append(badge(f"Industry Rank: {ind_rank}", "blue"))

    score_bits = [f"Structure {public_score:.0f}/100"]
    if pd.notna(internal_score):
        score_bits.append(f"Internal Quality {float(internal_score):.0f}/100")
    for col, label in [("internal_leader_score", "Leader"), ("internal_trend_score", "Trend"), ("internal_setup_score", "Setup"), ("internal_risk_score", "Risk")]:
        val = pd.to_numeric(row.get(col), errors="coerce")
        if pd.notna(val):
            score_bits.append(f"{label} {float(val):.0f}")

    failure_html = ""
    private_notes = " · ".join([x for x in [technical_flags, failures] if x and x.lower() not in {"nan", "none"}])
    if private_notes:
        failure_html = f'<div class="failure-line"><b>Private diagnostics:</b> {esc(private_notes)}</div>'

    st.markdown(
        f"""
<div class="stock-card {stage_class(stage)}">
  <div class="stock-head">
    <div style="min-width:0;">
      <div class="stock-name">{idx}. {esc(company_label(row))}</div>
      <div class="stock-meta">{esc(str(row.get('Industry', 'Unknown')))} · {esc(volume_pattern_display(row))}</div>
      <div class="stock-meta">{esc(nifty_outperformance_label(row))} · RS: {esc(relative_strength_label(row))}</div>
    </div>
    <div class="rank-badge"><div class="rank-label">Stock Rank</div><div class="rank-value">{rank_text}</div></div>
  </div>
  <div class="badge-strip">{''.join(badges)}</div>
  <div class="signal-line">{' · '.join(score_bits)}</div>
  {failure_html}
</div>
""",
        unsafe_allow_html=True,
    )
    if show_charts:
        daily_html = chart_img_html(daily_index, ticker, "Daily Chart")
        weekly_html = chart_img_html(weekly_index, ticker, "Weekly Chart")
        st.markdown(f'<div class="chart-grid">{daily_html}{weekly_html}</div>', unsafe_allow_html=True)


def render_dataframe(df: pd.DataFrame, columns: list[str], height: int = 430):
    cols = [c for c in columns if c in df.columns]
    if not cols:
        st.info("No matching columns available.")
        return
    st.dataframe(df[cols], use_container_width=True, hide_index=True, height=height)


# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Private Controls")
    outdir_text = st.text_input("Output folder", value=str(DEFAULT_OUTPUT_DIR))
    output_dir = Path(outdir_text)
    max_cards = st.slider("Cards per section", 5, 50, 15, 5)
    show_charts = st.toggle("Show charts on cards", value=True)
    st.caption(f"Build: {APP_BUILD}")

combined, daily_df, weekly_df, industry_df, regime_df, changes_df, moves_df, history_df, interesting_latest = load_data(output_dir)
if combined.empty:
    st.error("No vcp_combined_ranked.csv found. Put generated output files inside the selected outputs folder.")
    st.stop()

try:
    daily_mtime = (output_dir / "charts" / "daily").stat().st_mtime_ns
except Exception:
    daily_mtime = 0
try:
    weekly_mtime = (output_dir / "charts" / "weekly").stat().st_mtime_ns
except Exception:
    weekly_mtime = 0

daily_index = build_chart_index(str(output_dir / "charts" / "daily"), "_daily.png", daily_mtime)
weekly_index = build_chart_index(str(output_dir / "charts" / "weekly"), "_weekly.png", weekly_mtime)

ind_table = build_industry_rank_table(industry_df, combined)
failed7 = stage_history_failed_7d(history_df, combined)
stage_cnt = stage_counts(combined)
interesting_ranked = latest_interesting_by_rank(combined)

buyable_count = int(combined.get("internal_is_buyable_setup", pd.Series(False, index=combined.index)).apply(boolish).sum())
leader_count = int(combined.get("internal_is_true_leader", pd.Series(False, index=combined.index)).apply(boolish).sum())
proper_count = int(combined.get("internal_is_proper_setup", pd.Series(False, index=combined.index)).apply(boolish).sum())
low_risk_count = int(combined.get("internal_is_low_risk", pd.Series(False, index=combined.index)).apply(boolish).sum())

st.markdown(
    f"""
<div class="private-hero">
  <div class="brand">Stock<span>Gita</span> Private Dashboard</div>
  <div class="subtitle">Internal control room with public stage labels plus private leader/setup/risk diagnostics. Latest engine run: <b>{esc(engine_timestamp(output_dir))}</b>.</div>
  <div class="private-warning"><b>Private view:</b> This screen includes internal scoring, setup diagnostics, failure reasons, and quality gates. Do not expose these raw fields on the public dashboard.</div>
</div>
""",
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    render_metric("Market Mood", market_mood(regime_df), breadth_text(regime_df))
with m2:
    render_metric("Stage 2 Stocks", f"{stage_cnt['Stage 2']}", f"Out of {len(combined):,} tracked stocks")
with m3:
    render_metric("Internal Buyable", str(buyable_count), "Private setup gate")
with m4:
    render_metric("True Leaders", str(leader_count), f"Proper: {proper_count} · Low risk: {low_risk_count}")
with m5:
    render_metric("Failed Stage 2", str(stage_cnt["Failed Stage 2"]), f"Last 7D: {len(failed7)}")
with m6:
    render_metric("Charts Indexed", f"{len(daily_index)} / {len(weekly_index)}", "Daily / Weekly")


tabs = st.tabs(["Control Room", "Internal Setups", "Failed Stage 2", "Stage Views", "Industries", "Charts", "Public Preview", "Data"])

with tabs[0]:
    st.markdown('<div class="section-title">Top Internal Setup Candidates</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Sorted by internal quality score, then public stock rank. These fields are private diagnostics.</div>', unsafe_allow_html=True)
    top_internal = combined.copy()
    if "internal_quality_score" in top_internal.columns:
        top_internal = top_internal.sort_values(["internal_is_buyable_setup", "internal_quality_score", "current_rank"], ascending=[False, False, True], na_position="last")
    else:
        top_internal = top_internal.sort_values("current_rank", ascending=True, na_position="last")
    for i, (_, row) in enumerate(top_internal.head(max_cards).iterrows(), start=1):
        render_stock_card(row, i, daily_index, weekly_index, ind_table, show_charts=show_charts)

with tabs[1]:
    st.markdown('<div class="section-title">Internal Setup Ranker</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stage_filter = st.multiselect("Stage", sorted(combined["stage"].dropna().astype(str).unique().tolist()), default=[])
    with c2:
        only_buyable = st.checkbox("Internal buyable only", value=False)
        only_leaders = st.checkbox("True leaders only", value=False)
    with c3:
        only_proper = st.checkbox("Proper setup only", value=False)
        only_low_risk = st.checkbox("Low risk only", value=False)
    with c4:
        min_quality = st.slider("Min internal quality", 0, 100, 0, 5)
    view = combined.copy()
    if stage_filter:
        view = view[view["stage"].astype(str).isin(stage_filter)]
    if only_buyable and "internal_is_buyable_setup" in view.columns:
        view = view[view["internal_is_buyable_setup"].apply(boolish)]
    if only_leaders and "internal_is_true_leader" in view.columns:
        view = view[view["internal_is_true_leader"].apply(boolish)]
    if only_proper and "internal_is_proper_setup" in view.columns:
        view = view[view["internal_is_proper_setup"].apply(boolish)]
    if only_low_risk and "internal_is_low_risk" in view.columns:
        view = view[view["internal_is_low_risk"].apply(boolish)]
    if "internal_quality_score" in view.columns:
        view = view[pd.to_numeric(view["internal_quality_score"], errors="coerce").fillna(0) >= min_quality]
        view = view.sort_values(["internal_quality_score", "current_rank"], ascending=[False, True], na_position="last")
    else:
        view = view.sort_values("current_rank", ascending=True, na_position="last")
    render_dataframe(view, [
        "current_rank", "Company Name", "ticker", "Industry", "public_stage_label", "structure_score_public",
        "internal_quality_score", "internal_leader_score", "internal_trend_score", "internal_setup_score", "internal_risk_score",
        "internal_is_true_leader", "internal_is_proper_setup", "internal_is_low_risk", "internal_is_buyable_setup",
        "risk_pct", "setup_state", "internal_failure_reasons",
    ], height=500)
    st.markdown('<div class="section-title">Cards</div>', unsafe_allow_html=True)
    for i, (_, row) in enumerate(view.head(max_cards).iterrows(), start=1):
        render_stock_card(row, i, daily_index, weekly_index, ind_table, show_charts=show_charts)

with tabs[2]:
    st.markdown('<div class="section-title">Failed Stage 2 - Last 7 Days</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Uses stage_action_history.csv and current combined output. Public label is visible, private diagnostics are shown here only.</div>', unsafe_allow_html=True)
    if failed7.empty:
        st.info("No Failed Stage 2 stocks found in the last 7 days from available history.")
    else:
        render_dataframe(failed7.sort_values("current_rank", ascending=True, na_position="last"), [
            "failed_seen_date", "current_rank", "Company Name", "ticker", "Industry", "public_stage_label",
            "internal_quality_score", "internal_failure_reasons", "volume_pattern_display", "nifty_3m_outperformance_label",
        ], height=360)
        for i, (_, row) in enumerate(failed7.sort_values("current_rank", ascending=True, na_position="last").head(max_cards).iterrows(), start=1):
            render_stock_card(row, i, daily_index, weekly_index, ind_table, show_charts=show_charts)

with tabs[3]:
    st.markdown('<div class="section-title">Stage Views</div>', unsafe_allow_html=True)
    stage_choice = st.radio("Stage", ["Stage 1", "Stage 2", "Failed Stage 2", "Stage 3", "Stage 4", "Not Sure"], horizontal=True)
    sv = combined[combined["stage"].astype(str).eq(stage_choice)].sort_values("current_rank", ascending=True, na_position="last")
    render_metric(f"{stage_choice} Count", str(len(sv)), "Sorted by stock rank")
    render_dataframe(sv, ["current_rank", "Company Name", "ticker", "Industry", "public_stage_label", "structure_score_public", "internal_quality_score", "volume_pattern_display", "nifty_3m_outperformance_label"], height=350)
    for i, (_, row) in enumerate(sv.head(max_cards).iterrows(), start=1):
        render_stock_card(row, i, daily_index, weekly_index, ind_table, show_charts=show_charts)

with tabs[4]:
    st.markdown('<div class="section-title">Industry Rank Dashboard</div>', unsafe_allow_html=True)
    if ind_table.empty:
        st.info("Industry data is not available.")
    else:
        leaders = ind_table.head(8)
        neutral_start = max(8, len(ind_table) // 2 - 3)
        neutral = ind_table.iloc[neutral_start:neutral_start + 6]
        laggards = ind_table.tail(6)
        a, b, c = st.columns(3)
        with a:
            st.markdown("#### Leaders - Top 8")
            render_dataframe(leaders, ["current_rank", "Industry", "stock_count", "stage2_count", "failed_stage2_count", "avg_combined_score", "rs_rank"], height=330)
        with b:
            st.markdown("#### Neutral - Middle 6")
            render_dataframe(neutral, ["current_rank", "Industry", "stock_count", "stage2_count", "failed_stage2_count", "avg_combined_score", "rs_rank"], height=330)
        with c:
            st.markdown("#### Laggards - Bottom 6")
            render_dataframe(laggards, ["current_rank", "Industry", "stock_count", "stage2_count", "failed_stage2_count", "avg_combined_score", "rs_rank"], height=330)
        st.markdown("#### Full industry rank table")
        render_dataframe(ind_table, ["current_rank", "Industry", "stock_count", "stage2_count", "failed_stage2_count", "avg_combined_score", "rs_rank", "rank_change"], height=520)

with tabs[5]:
    st.markdown('<div class="section-title">Chart Review</div>', unsafe_allow_html=True)
    select_df = combined.sort_values("current_rank", ascending=True, na_position="last").copy()
    select_df["_display"] = select_df.apply(lambda r: f"#{int(r['current_rank']) if pd.notna(r['current_rank']) else '-'} · {company_label(r)} · {public_stage_label(r)}", axis=1)
    options = select_df["_display"].tolist()
    selected = st.selectbox("Select stock", options=options)
    row = select_df[select_df["_display"].eq(selected)].iloc[0]
    render_stock_card(row, int(pd.to_numeric(row.get("current_rank"), errors="coerce") or 1), daily_index, weekly_index, ind_table, show_charts=True)

with tabs[6]:
    st.markdown('<div class="section-title">Public Output Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">This is the data style safe for public cards. It hides internal quality gates and failure reasons.</div>', unsafe_allow_html=True)
    public_preview = combined.sort_values("current_rank", ascending=True, na_position="last").copy()
    render_dataframe(public_preview, [
        "current_rank", "Company Name", "ticker", "Industry", "public_stage_label", "structure_score_public",
        "relative_strength_label", "volume_pattern_display", "nifty_3m_outperformance_label", "trend_template_pass",
    ], height=520)
    st.markdown("#### Interesting 20 by Stock Rank")
    render_dataframe(interesting_ranked, ["current_rank", "Company Name", "ticker", "Industry", "public_stage_label", "structure_score_public", "volume_pattern_display", "nifty_3m_outperformance_label"], height=420)

with tabs[7]:
    st.markdown('<div class="section-title">Raw Data / Debug</div>', unsafe_allow_html=True)
    raw_choice = st.selectbox("Dataset", ["combined + internal", "daily", "weekly", "industry", "changes", "moves", "history", "interesting_latest"])
    raw_map = {
        "combined + internal": combined,
        "daily": daily_df,
        "weekly": weekly_df,
        "industry": industry_df,
        "changes": changes_df,
        "moves": moves_df,
        "history": history_df,
        "interesting_latest": interesting_latest,
    }
    raw_df = raw_map[raw_choice]
    st.caption(f"Rows: {len(raw_df):,} · Columns: {len(raw_df.columns) if not raw_df.empty else 0}")
    st.dataframe(raw_df, use_container_width=True, hide_index=True, height=560)
    if not raw_df.empty:
        st.download_button(
            "Download selected dataset CSV",
            data=raw_df.to_csv(index=False).encode("utf-8"),
            file_name=f"stockgita_private_{raw_choice.replace(' ', '_').replace('+', 'plus')}.csv",
            mime="text/csv",
        )
