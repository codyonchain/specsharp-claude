from __future__ import annotations

import json
import math
from typing import Any, Dict, Optional
import html as html_module

from app.utils.formatting import format_currency


def _dealshield_is_currency_metric(metric_ref: Optional[str]) -> bool:
    if not metric_ref:
        return False
    ref = metric_ref.lower()
    if "dscr" in ref or "yield_on_cost" in ref:
        return False
    currency_hints = (
        "cost",
        "revenue",
        "price",
        "value",
        "amount",
        "budget",
        "income",
        "noi",
        "capex",
        "opex",
    )
    return any(hint in ref for hint in currency_hints)


def _dealshield_parse_numeric(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return None
        normalized = trimmed.replace("$", "").replace(",", "").replace("%", "")
        if not normalized:
            return None
        try:
            parsed = float(normalized)
        except Exception:
            return None
        return parsed if math.isfinite(parsed) else None
    try:
        parsed = float(value)
    except Exception:
        return None
    return parsed if math.isfinite(parsed) else None


def _dealshield_format_percent(value: float) -> str:
    return f"{value:,.1f}%"


def _dealshield_format_yield_on_cost(value: float) -> str:
    if value <= 1.5:
        return _dealshield_format_percent(value * 100)
    if value <= 150:
        return _dealshield_format_percent(value)
    return _dealshield_format_percent(value)


def _dealshield_format_value(value: Any, metric_ref: Optional[str]) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, str) and "not modeled" in value.lower():
        return "Not modeled"

    numeric = _dealshield_parse_numeric(value)
    if numeric is None:
        return "—"

    ref = metric_ref.lower() if isinstance(metric_ref, str) else ""
    if "yield_on_cost" in ref:
        return _dealshield_format_yield_on_cost(numeric)
    if "dscr" in ref:
        return f"{numeric:,.2f}"
    if _dealshield_is_currency_metric(metric_ref):
        return format_currency(numeric)
    decimals = 0 if numeric.is_integer() else 2
    return f"{numeric:,.{decimals}f}"


def _dealshield_format_scalar(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return str(value)
    numeric = _dealshield_parse_numeric(value)
    if numeric is None:
        if isinstance(value, str) and "not modeled" in value.lower():
            return "Not modeled"
        return "—"
    decimals = 0 if numeric.is_integer() else 2
    return f"{numeric:,.{decimals}f}"


def _dealshield_format_assumption_percent(value: Any) -> str:
    numeric = _dealshield_parse_numeric(value)
    if numeric is None:
        return "—"
    percent_value = numeric * 100 if abs(numeric) <= 1.5 else numeric
    return f"{percent_value:,.1f}%"


def _dealshield_format_assumption_years(value: Any) -> str:
    numeric = _dealshield_parse_numeric(value)
    if numeric is None:
        return "—"
    return f"{numeric:,.1f} yrs" if not float(numeric).is_integer() else f"{int(numeric):,d} yrs"


def _dealshield_format_assumption_months(value: Any) -> str:
    numeric = _dealshield_parse_numeric(value)
    if numeric is None:
        return "—"
    return f"{int(round(numeric)):,d} mo"


def _dealshield_normalize_disclosures(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        text = str(item).strip() if item is not None else ""
        if not text:
            continue
        if text in output:
            continue
        output.append(text)
    return output


def _dealshield_render_assumptions(financing_assumptions: Any, disclosures: list[str]) -> str:
    assumption_items: list[tuple[str, str]] = []
    if isinstance(financing_assumptions, dict):
        debt_pct = financing_assumptions.get("debt_pct")
        if debt_pct is None:
            debt_pct = financing_assumptions.get("ltv")
        assumption_items.extend(
            [
                ("Debt %", _dealshield_format_assumption_percent(debt_pct)),
                ("Rate", _dealshield_format_assumption_percent(financing_assumptions.get("interest_rate_pct"))),
                ("Amortization", _dealshield_format_assumption_years(financing_assumptions.get("amort_years"))),
                ("Loan term", _dealshield_format_assumption_years(financing_assumptions.get("loan_term_years"))),
            ]
        )
        io_value = financing_assumptions.get("interest_only_months")
        if io_value is None:
            io_value = financing_assumptions.get("interest_only")
        if isinstance(io_value, bool):
            assumption_items.append(("Interest-only", "Yes" if io_value else "No"))
        else:
            assumption_items.append(("Interest-only", _dealshield_format_assumption_months(io_value)))

    assumption_items = [item for item in assumption_items if item[1] != "—"]
    if not assumption_items and not disclosures:
        return ""

    lines: list[str] = [
        "<div class=\"assumptions-block\">",
        "<div class=\"assumptions-title\">Assumptions</div>",
    ]
    if assumption_items:
        lines.append("<div class=\"assumptions-grid\">")
        for label, value in assumption_items:
            lines.append(
                "<div class=\"assumption-item\">"
                f"<span class=\"assumption-label\">{html_module.escape(label)}:</span> "
                f"<span>{html_module.escape(value)}</span>"
                "</div>"
            )
        lines.append("</div>")

    if disclosures:
        lines.append("<ul class=\"assumptions-disclosures\">")
        for disclosure in disclosures:
            lines.append(f"<li>{html_module.escape(disclosure)}</li>")
        lines.append("</ul>")

    lines.append("</div>")
    return "".join(lines)


def _dealshield_driver_refs(driver: Any) -> str:
    if not driver:
        return "—"
    if isinstance(driver, dict):
        metric_ref = driver.get("metric_ref")
        return str(metric_ref) if metric_ref else "—"
    if isinstance(driver, list):
        refs = []
        for entry in driver:
            if isinstance(entry, dict) and entry.get("metric_ref"):
                refs.append(str(entry.get("metric_ref")))
        return ", ".join(refs) if refs else "—"
    return str(driver)


def _dealshield_render_content_sections(view_model: Dict[str, Any]) -> str:
    content = view_model.get("content")
    if not isinstance(content, dict):
        return (
            "<section>"
            "<h2>DealShield Content</h2>"
            "<div class=\"content-note\">Content profile not available.</div>"
            "</section>"
        )

    resolved_drivers = content.get("resolved_drivers")
    driver_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(resolved_drivers, list):
        for resolved in resolved_drivers:
            if not isinstance(resolved, dict):
                continue
            tile_id = resolved.get("tile_id")
            if isinstance(tile_id, str) and tile_id:
                driver_map[tile_id] = resolved

    fastest_change = content.get("fastest_change")
    fastest_headline = "What would change this decision fastest?"
    fastest_drivers: list[Any] = []
    if isinstance(fastest_change, dict):
        headline = fastest_change.get("headline")
        if isinstance(headline, str) and headline.strip():
            fastest_headline = headline.strip()
        drivers = fastest_change.get("drivers")
        if isinstance(drivers, list):
            fastest_drivers = drivers

    fastest_items = []
    driver_label_by_tile: Dict[str, str] = {}
    for driver in fastest_drivers[:3]:
        if not isinstance(driver, dict):
            continue
        label = driver.get("label") or driver.get("id") or driver.get("tile_id") or "Driver"
        tile_id = driver.get("tile_id")
        if isinstance(tile_id, str) and tile_id:
            driver_label_by_tile[tile_id] = str(label)
        details = []
        if isinstance(tile_id, str) and tile_id:
            details.append(f"Tile: {tile_id}")
            resolved = driver_map.get(tile_id)
            if isinstance(resolved, dict):
                metric_ref = resolved.get("metric_ref")
                if metric_ref:
                    details.append(f"Metric: {metric_ref}")
                transform = resolved.get("transform")
                if transform:
                    details.append(f"Transform: {json.dumps(transform, sort_keys=True)}")
        detail_line = (
            f"<div class=\"content-subtle\">{html_module.escape(' | '.join(details))}</div>"
            if details
            else ""
        )
        fastest_items.append(
            f"<li><span class=\"content-label\">{html_module.escape(str(label))}</span>{detail_line}</li>"
        )
    if not fastest_items:
        fastest_items.append("<li>No drivers configured.</li>")

    mlw = content.get("most_likely_wrong")
    mlw_items = []
    if isinstance(mlw, list):
        for entry in mlw:
            if not isinstance(entry, dict):
                continue
            text = entry.get("text") or "No text."
            why = entry.get("why")
            why_line = (
                f"<div class=\"content-subtle\">{html_module.escape(str(why))}</div>" if why else ""
            )
            mlw_items.append(
                f"<li><span class=\"content-label\">{html_module.escape(str(text))}</span>{why_line}</li>"
            )
    if not mlw_items:
        mlw_items.append("<li>No entries configured.</li>")

    question_bank = content.get("question_bank")
    question_items = []
    if isinstance(question_bank, list):
        for entry in question_bank:
            if not isinstance(entry, dict):
                continue
            raw_driver_tile_id = entry.get("driver_tile_id")
            driver_tile_id = str(raw_driver_tile_id) if raw_driver_tile_id else ""
            driver_label = (
                driver_label_by_tile.get(driver_tile_id)
                or entry.get("label")
                or entry.get("id")
                or "Questions"
            )
            tile_tag = (
                f" <span class=\"content-inline-muted\">(tile: {html_module.escape(driver_tile_id)})</span>"
                if driver_tile_id
                else ""
            )
            questions = entry.get("questions")
            question_lines = []
            if isinstance(questions, list):
                for question in questions:
                    if isinstance(question, str) and question.strip():
                        question_lines.append(f"<li>{html_module.escape(question.strip())}</li>")
            if not question_lines:
                question_lines.append("<li>No questions configured.</li>")
            question_items.append(
                "<li>"
                f"<div class=\"content-label\">{html_module.escape(str(driver_label))}{tile_tag}</div>"
                "<ul class=\"content-sublist\">"
                + "".join(question_lines)
                + "</ul>"
                "</li>"
            )
    if not question_items:
        question_items.append("<li>No entries configured.</li>")

    red_flags_actions = content.get("red_flags_actions")
    red_flag_items = []
    if isinstance(red_flags_actions, list):
        for entry in red_flags_actions:
            if not isinstance(entry, dict):
                continue
            flag = entry.get("flag") or "Flag not set."
            action = entry.get("action") or "Action not set."
            red_flag_items.append(
                "<li>"
                f"<span class=\"content-label\">{html_module.escape(str(flag))}</span>"
                f"<div class=\"content-subtle\">Action: {html_module.escape(str(action))}</div>"
                "</li>"
            )
    if not red_flag_items:
        red_flag_items.append("<li>No entries configured.</li>")

    return (
        "<section>"
        f"<h2>{html_module.escape(fastest_headline)}</h2>"
        "<ul class=\"content-list\">"
        + "".join(fastest_items)
        + "</ul>"
        "</section>"
        "<section>"
        "<h2>Most likely wrong</h2>"
        "<ul class=\"content-list\">"
        + "".join(mlw_items)
        + "</ul>"
        "</section>"
        "<section>"
        "<h2>Question bank</h2>"
        "<ul class=\"content-list\">"
        + "".join(question_items)
        + "</ul>"
        "</section>"
        "<section>"
        "<h2>Red flags &amp; actions</h2>"
        "<ul class=\"content-list\">"
        + "".join(red_flag_items)
        + "</ul>"
        "</section>"
    )


def render_dealshield_html(view_model: Dict[str, Any]) -> str:
    profile_id = view_model.get("profile_id") or "unknown"
    context = view_model.get("context") if isinstance(view_model.get("context"), dict) else {}
    location = context.get("location")
    square_footage = context.get("square_footage")

    columns = view_model.get("columns")
    if not isinstance(columns, list):
        columns = []
    rows = view_model.get("rows")
    if not isinstance(rows, list):
        rows = []

    scenario_inputs = {}
    provenance = view_model.get("provenance")
    if isinstance(provenance, dict) and isinstance(provenance.get("scenario_inputs"), dict):
        scenario_inputs = provenance.get("scenario_inputs") or {}

    header_meta_parts = []
    if location:
        header_meta_parts.append(str(location))
    if square_footage is not None:
        try:
            header_meta_parts.append(f"{float(square_footage):,.0f} SF")
        except Exception:
            header_meta_parts.append(str(square_footage))
    header_meta = " • ".join(header_meta_parts)

    header_cells = ["<th>Scenario</th>"]
    for col in columns:
        label = col.get("label") if isinstance(col, dict) else None
        header_cells.append(f"<th>{html_module.escape(str(label or '—'))}</th>")
    header_row = "".join(header_cells)

    body_rows = []
    for row_index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        scenario_label = row.get("label") or row.get("scenario_id") or "—"
        row_cells = [f"<td class=\"scenario\">{html_module.escape(str(scenario_label))}</td>"]
        cells = row.get("cells") if isinstance(row.get("cells"), list) else []
        cell_by_tile: Dict[str, Dict[str, Any]] = {}
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            for key in ("tile_id", "col_id", "id"):
                cell_id = cell.get(key)
                if isinstance(cell_id, str) and cell_id:
                    cell_by_tile[cell_id] = cell
        for col in columns:
            if not isinstance(col, dict):
                row_cells.append("<td class=\"num\">—</td>")
                continue
            tile_id = col.get("tile_id") or col.get("id")
            metric_ref = col.get("metric_ref")
            cell = cell_by_tile.get(tile_id, {})
            value = cell.get("value") if isinstance(cell, dict) else None
            formatted = _dealshield_format_value(value, metric_ref)
            row_cells.append(f"<td class=\"num\">{html_module.escape(formatted)}</td>")
        row_class = "main-row-alt" if row_index % 2 else "main-row"
        body_rows.append(f"<tr class=\"{row_class}\">{''.join(row_cells)}</tr>")
    table_body = "\n".join(body_rows)

    provenance_rows = []
    if scenario_inputs:
        for row in rows:
            if not isinstance(row, dict):
                continue
            scenario_id = row.get("scenario_id")
            if not scenario_id:
                continue
            inputs = scenario_inputs.get(scenario_id)
            if not isinstance(inputs, dict):
                continue
            applied = inputs.get("applied_tile_ids")
            if isinstance(applied, list):
                applied_text = ", ".join(str(item) for item in applied) if applied else "—"
            else:
                applied_text = "—"
            cost_scalar = _dealshield_format_scalar(inputs.get("cost_scalar"))
            revenue_scalar = _dealshield_format_scalar(inputs.get("revenue_scalar"))
            driver_ref = _dealshield_driver_refs(inputs.get("driver"))
            scenario_label = row.get("label") or scenario_id
            provenance_rows.append(
                "<tr>"
                f"<td>{html_module.escape(str(scenario_label))}</td>"
                f"<td>{html_module.escape(applied_text)}</td>"
                f"<td class=\"num\">{html_module.escape(cost_scalar)}</td>"
                f"<td class=\"num\">{html_module.escape(revenue_scalar)}</td>"
                f"<td>{html_module.escape(str(driver_ref))}</td>"
                "</tr>"
            )

    provenance_table = ""
    if provenance_rows:
        provenance_table = (
            "<table class=\"provenance-table\">"
            "<thead><tr>"
            "<th>Scenario</th>"
            "<th>Applied Tiles</th>"
            "<th>Cost Scalar</th>"
            "<th>Revenue Scalar</th>"
            "<th>Driver metric (Ugly only)</th>"
            "</tr></thead>"
            "<tbody>"
            + "".join(provenance_rows)
            + "</tbody></table>"
        )
    else:
        metric_refs_used = []
        if isinstance(provenance, dict):
            metric_refs_used = provenance.get("metric_refs_used") or []
        ref_pills = []
        if isinstance(metric_refs_used, list):
            for ref in metric_refs_used:
                if ref is None:
                    continue
                ref_pills.append(f"<span class=\"ref-pill\">{html_module.escape(str(ref))}</span>")
        if not ref_pills:
            ref_pills.append("<span class=\"ref-pill ref-pill-empty\">—</span>")
        provenance_table = (
            "<div class=\"provenance-note\">Scenario inputs not available.</div>"
            "<div class=\"provenance-meta\">"
            "<span class=\"provenance-meta-label\">Metric refs used:</span>"
            f"<div class=\"provenance-ref-list\">{''.join(ref_pills)}</div>"
            "</div>"
        )

    financing_assumptions = view_model.get("financing_assumptions")
    if not isinstance(financing_assumptions, dict) and isinstance(provenance, dict):
        financing_assumptions = provenance.get("financing_assumptions")
    if not isinstance(financing_assumptions, dict):
        financing_assumptions = {}

    disclosures = _dealshield_normalize_disclosures(view_model.get("dealshield_disclosures"))
    if isinstance(provenance, dict):
        for item in _dealshield_normalize_disclosures(provenance.get("dealshield_disclosures")):
            if item not in disclosures:
                disclosures.append(item)
    assumptions_block = _dealshield_render_assumptions(financing_assumptions, disclosures)

    meta_block = f"<div class=\"meta\">{html_module.escape(header_meta)}</div>" if header_meta else ""
    content_sections = _dealshield_render_content_sections(view_model)

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>DealShield</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #111827; margin: 0; padding: 32px; }}
    h1 {{ margin: 0; font-size: 28px; letter-spacing: 0.3px; }}
    section {{ margin-top: 28px; }}
    h2 {{ margin: 0 0 10px; font-size: 19px; color: #1f2937; }}
    .subtitle {{ color: #4b5563; margin-top: 4px; font-size: 13px; }}
    .meta {{ color: #6b7280; font-size: 12px; margin-top: 4px; }}
    .table-wrap {{ margin-top: 22px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 7px 9px; text-align: left; }}
    th {{ background: #f8fafc; font-weight: 600; color: #111827; }}
    td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    td.scenario {{ font-weight: 600; }}
    .main-row-alt td {{ background: #f8fafc; }}
    .context-note {{ margin-top: 8px; color: #6b7280; font-size: 12px; }}
    .provenance-note {{ margin-top: 6px; color: #6b7280; font-size: 12px; }}
    .provenance-meta {{ margin-top: 4px; color: #4b5563; font-size: 12px; }}
    .provenance-meta-label {{ color: #374151; display: inline-block; margin-bottom: 6px; }}
    .provenance-ref-list {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .ref-pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; border: 1px solid #e5e7eb; background: #f8fafc; color: #374151; font-size: 11px; font-family: Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; line-height: 1.3; max-width: 100%; overflow-wrap: anywhere; }}
    .ref-pill-empty {{ font-family: 'Helvetica Neue', Arial, sans-serif; }}
    .provenance-table {{ font-size: 11px; }}
    .provenance-table th {{ font-size: 10px; }}
    .provenance-table td {{ padding: 6px 8px; }}
    .content-note {{ margin-top: 6px; color: #6b7280; font-size: 12px; }}
    .content-list {{ margin: 8px 0 0; padding-left: 20px; font-size: 12px; }}
    .content-list li {{ margin: 0 0 8px; }}
    .content-sublist {{ margin: 4px 0 0; padding-left: 18px; }}
    .content-subtle {{ color: #4b5563; font-size: 11px; margin-top: 2px; }}
    .content-label {{ font-weight: 600; color: #111827; }}
    .content-inline-muted {{ color: #9ca3af; font-size: 10px; font-weight: 500; font-family: Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }}
    .assumptions-block {{ margin-top: 8px; border: 1px solid #e5e7eb; background: #f8fafc; border-radius: 6px; padding: 8px 10px; }}
    .assumptions-title {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.6px; color: #6b7280; font-weight: 700; }}
    .assumptions-grid {{ margin-top: 6px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px 16px; font-size: 11px; color: #334155; }}
    .assumption-item {{ margin: 0; }}
    .assumption-label {{ font-weight: 600; color: #475569; }}
    .assumptions-disclosures {{ margin: 6px 0 0; padding-left: 18px; font-size: 11px; color: #475569; }}
    .assumptions-disclosures li {{ margin: 0 0 2px; }}
  </style>
</head>
<body>
  <header>
    <h1>DealShield</h1>
    <div class="subtitle">Profile: {html_module.escape(str(profile_id))}</div>
    {meta_block}
  </header>

  <section class="table-wrap">
    <table class="main-table">
      <thead><tr>{header_row}</tr></thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
    <div class="context-note">DSCR and Yield reflect the underwriting/debt terms in this run — see Provenance.</div>
    {assumptions_block}
  </section>

  <section>
    <h2>Provenance</h2>
    {provenance_table}
  </section>
  {content_sections}
</body>
</html>"""
