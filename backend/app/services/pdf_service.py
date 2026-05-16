"""
PDF generation service for XAI churn risk reports.

Layout (A4, top-to-bottom canvas):
  1. Dark header banner — RASSAY logo + report title
  2. Customer name + meta row
  3. AI Risk Score — large number, progress bar, risk narrative
  4. XAI Factors — each factor with plain-English sentence + impact bar
  5. Retention Recommendations — derived from top risk factors
  6. Financial strip — MRR, account age, churn status
  7. Footer — confidentiality notice
"""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.services import customer_service, xai_service

# ── Brand palette ─────────────────────────────────────────────────────────────
C_DARK   = colors.HexColor("#0f172a")   # slate-900  — header bg
C_CARD   = colors.HexColor("#f8fafc")   # slate-50   — alternating rows
C_BLUE   = colors.HexColor("#3b82f6")   # blue-500   — RASSAY accent
C_RED    = colors.HexColor("#e11d48")   # rose-600   — high / positive impact
C_AMBER  = colors.HexColor("#d97706")   # amber-600  — medium risk
C_GREEN  = colors.HexColor("#059669")   # emerald-600 — low / negative impact
C_TEXT   = colors.HexColor("#1e293b")   # slate-800  — body copy
C_MUTED  = colors.HexColor("#64748b")   # slate-500  — labels / captions
C_BORDER = colors.HexColor("#e2e8f0")   # slate-200  — dividers
C_WHITE  = colors.white

# ── Feature vocabulary ────────────────────────────────────────────────────────
_LABELS = {
    "mrr_value":           "Monthly Recurring Revenue",
    "account_age_months":  "Account Tenure",
    "support_tickets":     "Support Ticket Volume",
    "login_count":         "Login Frequency",
    "plan_type":           "Subscription Plan Tier",
    "active_users":        "Active User Count",
    "feature_usage_count": "Feature Adoption Rate",
    "nps_score":           "Customer Satisfaction (NPS)",
    "churn_probability":   "Historical Churn Signal",
}

_TIPS = {
    "login_count":          "Schedule a product re-engagement call and offer a guided feature walkthrough.",
    "support_tickets":      "Escalate to senior CSM and close all outstanding tickets within 48 hours.",
    "mrr_value":            "Review plan fit and discuss right-sizing or a renewal incentive.",
    "account_age_months":   "Prepare a tailored refresher aligned to the latest platform capabilities.",
    "nps_score":            "Initiate a structured feedback session and close the loop on prior concerns.",
    "plan_type":            "Offer a plan upgrade trial or feature unlock to increase perceived value.",
    "active_users":         "Identify internal champions and provide team adoption training resources.",
    "feature_usage_count":  "Run a targeted feature spotlight session with the primary stakeholder.",
}

_DEFAULT_RECS = [
    "Schedule a Customer Success review call within 7 days.",
    "Review account activity and identify product adoption gaps.",
    "Align with the account executive on renewal risk and escalation path.",
]

_RISK_NARRATIVE = {
    "High":   "This account is classified as HIGH RISK. Immediate retention intervention is recommended. "
              "Key signals indicate engagement and revenue instability that, without action, will likely "
              "result in churn within the next 30–60 days.",
    "Medium": "This account is classified as MEDIUM RISK. The Customer Success team should schedule a "
              "proactive check-in within the next 14 days to address emerging warning signals before "
              "they escalate.",
    "Low":    "This account is classified as LOW RISK. Engagement and revenue signals are broadly healthy. "
              "Continue standard account monitoring and maintain regular touchpoints.",
}


def _label(name: str) -> str:
    return _LABELS.get(name, name.replace("_", " ").title())


def _sentence(name: str, impact: float) -> str:
    lbl = _label(name)
    pct = abs(impact) * 100
    verb = "increased" if impact > 0 else "reduced"
    return f"{lbl} {verb} churn risk by {pct:.1f}%"


def _risk_color(level: str):
    return {"High": C_RED, "Medium": C_AMBER, "Low": C_GREEN}.get(level, C_MUTED)


def _wrapped_lines(c_obj, text: str, font: str, size: float, max_w: float) -> list[str]:
    """Split text into lines that fit within max_w at the given font/size."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if c_obj.stringWidth(candidate, font, size) <= max_w:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _draw_text(c_obj, text: str, x: float, y: float, font: str, size: float,
               color, max_w: float | None = None, line_h: float = 12) -> float:
    """Draw possibly-wrapped text; return new y after last line."""
    c_obj.setFillColor(color)
    c_obj.setFont(font, size)
    if max_w is None:
        c_obj.drawString(x, y, text)
        return y
    for line in _wrapped_lines(c_obj, text, font, size, max_w):
        c_obj.drawString(x, y, line)
        y -= line_h
    return y


def generate_pdf(company_id: str, db: Session) -> bytes:
    customer = customer_service.get_customer_detail(company_id, db)
    if not customer:
        raise ValueError(f"Customer {company_id} not found")

    xai_data = xai_service.get_xai_explanation(company_id, db)
    factors  = xai_data.factors[:5]

    buf = io.BytesIO()
    W, H = A4
    c   = canvas.Canvas(buf, pagesize=A4)

    ML = 20 * mm          # left margin
    MR = W - 20 * mm      # right edge
    CW = MR - ML          # content width

    # ── 1. Header banner ─────────────────────────────────────────────────────
    BH = 20 * mm
    c.setFillColor(C_DARK)
    c.rect(0, H - BH, W, BH, fill=1, stroke=0)

    # RASSAY wordmark
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(ML, H - BH + 7 * mm, "RASSAY")
    c.setFillColor(C_BLUE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(ML + 21 * mm, H - BH + 7 * mm, "AI")

    # Report sub-title
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica", 8)
    c.drawRightString(MR, H - BH + 7 * mm, "XAI Churn Risk Intelligence Report  ·  Confidential")

    y = H - BH - 9 * mm

    # ── 2. Customer overview ──────────────────────────────────────────────────
    company_name = customer.company_name or company_id
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(ML, y, company_name)
    y -= 6.5 * mm

    meta = (
        f"ID: {company_id}   ·   Plan: {customer.plan_type or 'N/A'}"
        f"   ·   Owner: {customer.account_owner or 'Unassigned'}"
    )
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(ML, y, meta)
    y -= 4.5 * mm

    c.setFont("Helvetica", 8)
    c.drawString(ML, y, f"Report generated: {datetime.utcnow().strftime('%B %d, %Y  at  %H:%M UTC')}")
    y -= 7 * mm

    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.5)
    c.line(ML, y, MR, y)
    y -= 8 * mm

    # ── 3. Risk score ─────────────────────────────────────────────────────────
    risk_pct = round((customer.risk_score or 0) * 100)
    level    = customer.risk_level or "Low"
    r_col    = _risk_color(level)

    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(ML, y, "AI RISK PROBABILITY")
    y -= 6 * mm

    # Large numeral
    c.setFillColor(r_col)
    c.setFont("Helvetica-Bold", 52)
    c.drawString(ML, y - 11 * mm, f"{risk_pct}%")

    # Risk level pill — positioned to the right of the number
    pill_x = ML + 30 * mm
    pill_y = y - 8 * mm
    pill_w = 26 * mm
    pill_h = 8 * mm
    c.setFillColor(r_col)
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 3 * mm, fill=1, stroke=0)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(pill_x + pill_w / 2, pill_y + 2.5 * mm, f"{level.upper()} RISK")

    y -= 16 * mm

    # Progress bar
    c.setFillColor(C_BORDER)
    c.roundRect(ML, y, CW, 4 * mm, 2 * mm, fill=1, stroke=0)
    filled_w = max(CW * risk_pct / 100, 3)
    c.setFillColor(r_col)
    c.roundRect(ML, y, filled_w, 4 * mm, 2 * mm, fill=1, stroke=0)
    y -= 6 * mm

    # Narrative
    narrative = _RISK_NARRATIVE.get(level, "")
    y = _draw_text(c, narrative, ML, y, "Helvetica", 9, C_TEXT, max_w=CW, line_h=12) - 8 * mm

    c.setStrokeColor(C_BORDER)
    c.line(ML, y, MR, y)
    y -= 8 * mm

    # ── 4. XAI factors ───────────────────────────────────────────────────────
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(ML, y, "EXPLAINABLE AI  —  SHAP RISK FACTORS")
    y -= 4 * mm
    c.setFont("Helvetica", 7.5)
    c.drawString(ML, y, "Ranked by absolute impact on predicted churn probability.")
    y -= 7 * mm

    if not factors:
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(ML, y, "Insufficient telemetry data for XAI analysis.")
        y -= 12 * mm
    else:
        max_abs = max(abs(f.impact_value) for f in factors) or 1.0
        ROW_H   = 19 * mm

        for idx, factor in enumerate(factors):
            impact   = factor.impact_value
            f_col    = C_RED if impact > 0 else C_GREEN
            pct_str  = f"{'+' if impact > 0 else ''}{impact * 100:.1f}%"
            sentence = f'"{_sentence(factor.feature_name, impact)}"'

            # Alternating row background
            if idx % 2 == 0:
                c.setFillColor(C_CARD)
                c.rect(ML - 3, y - ROW_H + 4 * mm, CW + 6, ROW_H, fill=1, stroke=0)

            # Circle index
            cx = ML + 3.5 * mm
            cy = y - ROW_H / 2 + 7 * mm
            c.setFillColor(C_DARK)
            c.circle(cx, cy, 3.5 * mm, fill=1, stroke=0)
            c.setFillColor(C_WHITE)
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx, cy - 1.2 * mm, str(idx + 1))

            text_x = ML + 9 * mm

            # Feature label + impact %
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(text_x, y - 4 * mm, _label(factor.feature_name))
            c.setFillColor(f_col)
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(MR, y - 4 * mm, pct_str)

            # Plain-English sentence
            c.setFillColor(C_MUTED)
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(text_x, y - 9 * mm, sentence)

            # Thin impact bar
            bar_y  = y - 14 * mm
            bar_tw = 55 * mm
            c.setFillColor(C_BORDER)
            c.roundRect(text_x, bar_y, bar_tw, 2.5 * mm, 1.2 * mm, fill=1, stroke=0)
            filled = max(bar_tw * abs(impact) / max_abs, 2)
            c.setFillColor(f_col)
            c.roundRect(text_x, bar_y, filled, 2.5 * mm, 1.2 * mm, fill=1, stroke=0)

            y -= ROW_H

    y -= 4 * mm
    c.setStrokeColor(C_BORDER)
    c.line(ML, y, MR, y)
    y -= 8 * mm

    # ── 5. Retention recommendations ─────────────────────────────────────────
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(ML, y, "RETENTION RECOMMENDATIONS")
    y -= 8 * mm

    top_risk_features = [f.feature_name for f in factors if f.impact_value > 0][:3]
    recs = [_TIPS[f] for f in top_risk_features if f in _TIPS]
    for default in _DEFAULT_RECS:
        if len(recs) >= 3:
            break
        if default not in recs:
            recs.append(default)
    recs = recs[:3]

    for rec in recs:
        c.setFillColor(C_BLUE)
        c.circle(ML + 2 * mm, y + 1.5 * mm, 1.3 * mm, fill=1, stroke=0)
        y = _draw_text(c, rec, ML + 6 * mm, y, "Helvetica", 9, C_TEXT,
                       max_w=CW - 6 * mm, line_h=11) - 5 * mm

    # ── 6. Financial strip ────────────────────────────────────────────────────
    if customer.mrr_value:
        y -= 3 * mm
        strip_h = 15 * mm
        c.setFillColor(colors.HexColor("#f1f5f9"))
        c.roundRect(ML, y - strip_h + 4 * mm, CW, strip_h, 3, fill=1, stroke=0)

        def _strip_cell(label: str, value: str, cell_x: float) -> None:
            c.setFillColor(C_MUTED)
            c.setFont("Helvetica-Bold", 7)
            c.drawString(cell_x, y - 1 * mm, label)
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(cell_x, y - 7 * mm, value)

        _strip_cell("MRR AT RISK", f"${customer.mrr_value:,.0f}", ML + 5 * mm)
        _strip_cell("ACCOUNT AGE", f"{customer.account_age_months or 0} months", ML + 55 * mm)
        status_txt = "Churned" if (customer.churn_status or 0) == 1 else "Active"
        _strip_cell("CHURN STATUS", status_txt, ML + 110 * mm)

        y -= strip_h + 3 * mm

    # ── 7. Footer ─────────────────────────────────────────────────────────────
    footer_y = 10 * mm
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.4)
    c.line(ML, footer_y + 5 * mm, MR, footer_y + 5 * mm)
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(ML, footer_y, "Confidential — For internal use only. Generated by RASSAY AI Platform.")
    c.drawRightString(MR, footer_y, f"© {datetime.utcnow().year} RASSAY  ·  {company_id}")

    c.save()
    buf.seek(0)
    return buf.read()
