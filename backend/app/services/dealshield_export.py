from __future__ import annotations

import json
from typing import Any, Dict, Optional
import html as html_module

from app.utils.formatting import format_currency


def _dealshield_is_currency_metric(metric_ref: Optional[str]) -> bool:
    if not metric_ref:
        return False
    ref = metric_ref.lower()
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


def _dealshield_format_value(value: Any, metric_ref: Optional[str]) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return str(value)
    try:
        numeric = float(value)
    except Exception:
        return str(value)
    if _dealshield_is_currency_metric(metric_ref):
        return format_currency(numeric)
    decimals = 0 if numeric.is_integer() else 2
    return f"{numeric:,.{decimals}f}"


def _dealshield_format_scalar(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return str(value)
    try:
        numeric = float(value)
    except Exception:
        return str(value)
    decimals = 0 if numeric.is_integer() else 2
    return f"{numeric:,.{decimals}f}"


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
    for driver in fastest_drivers[:3]:
        if not isinstance(driver, dict):
            continue
        label = driver.get("label") or driver.get("id") or driver.get("tile_id") or "Driver"
        tile_id = driver.get("tile_id")
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
            driver_tile_id = entry.get("driver_tile_id") or "unknown"
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
                f"<div class=\"content-subtle\">Driver tile: {html_module.escape(str(driver_tile_id))}</div>"
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
    for row in rows:
        if not isinstance(row, dict):
            continue
        scenario_label = row.get("label") or row.get("scenario_id") or "—"
        row_cells = [f"<td class=\"scenario\">{html_module.escape(str(scenario_label))}</td>"]
        cells = row.get("cells") if isinstance(row.get("cells"), list) else []
        cell_by_tile = {
            cell.get("tile_id"): cell
            for cell in cells
            if isinstance(cell, dict) and cell.get("tile_id")
        }
        for col in columns:
            if not isinstance(col, dict):
                row_cells.append("<td class=\"num\">—</td>")
                continue
            tile_id = col.get("tile_id")
            metric_ref = col.get("metric_ref")
            cell = cell_by_tile.get(tile_id, {})
            value = cell.get("value") if isinstance(cell, dict) else None
            formatted = _dealshield_format_value(value, metric_ref)
            row_cells.append(f"<td class=\"num\">{html_module.escape(formatted)}</td>")
        body_rows.append(f"<tr>{''.join(row_cells)}</tr>")
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
            "<th>Driver Metric</th>"
            "</tr></thead>"
            "<tbody>"
            + "".join(provenance_rows)
            + "</tbody></table>"
        )
    else:
        metric_refs_used = []
        if isinstance(provenance, dict):
            metric_refs_used = provenance.get("metric_refs_used") or []
        refs_text = ", ".join(str(ref) for ref in metric_refs_used) if metric_refs_used else "—"
        provenance_table = (
            "<div class=\"provenance-note\">Scenario inputs not available.</div>"
            f"<div class=\"provenance-meta\">Metric refs used: {html_module.escape(refs_text)}</div>"
        )

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
    h2 {{ margin: 24px 0 8px; font-size: 18px; color: #1f2937; }}
    .subtitle {{ color: #4b5563; margin-top: 4px; font-size: 13px; }}
    .meta {{ color: #6b7280; font-size: 12px; margin-top: 4px; }}
    .table-wrap {{ margin-top: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }}
    th {{ background: #f9fafb; font-weight: 600; color: #111827; }}
    td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    td.scenario {{ font-weight: 600; }}
    .provenance-note {{ margin-top: 6px; color: #6b7280; font-size: 12px; }}
    .provenance-meta {{ margin-top: 4px; color: #4b5563; font-size: 12px; }}
    .provenance-table th {{ font-size: 11px; }}
    .content-note {{ margin-top: 6px; color: #6b7280; font-size: 12px; }}
    .content-list {{ margin: 8px 0 0; padding-left: 20px; font-size: 12px; }}
    .content-list li {{ margin: 0 0 8px; }}
    .content-sublist {{ margin: 4px 0 0; padding-left: 18px; }}
    .content-subtle {{ color: #4b5563; font-size: 11px; margin-top: 2px; }}
    .content-label {{ font-weight: 600; color: #111827; }}
  </style>
</head>
<body>
  <header>
    <h1>DealShield</h1>
    <div class="subtitle">Profile: {html_module.escape(str(profile_id))}</div>
    {meta_block}
  </header>

  <section class="table-wrap">
    <table>
      <thead><tr>{header_row}</tr></thead>
      <tbody>
        {table_body}
      </tbody>
    </table>
  </section>

  <section>
    <h2>Provenance</h2>
    {provenance_table}
  </section>
  {content_sections}
</body>
</html>"""
