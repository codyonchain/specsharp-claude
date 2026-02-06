from __future__ import annotations

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
</body>
</html>"""
