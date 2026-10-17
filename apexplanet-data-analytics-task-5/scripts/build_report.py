"""
build_report.py
===============
ApexPlanet Data Analytics Internship - Task 5

Generates the two-page PDF deliverable:

    reports/Task5_Final_Report.pdf

The PDF is built programmatically with PyMuPDF (fitz). Page 1 holds the
executive summary, the KPI table and two supporting charts; page 2 holds the
top five insights, three business recommendations and a footer.

The chart images come from the Task 3 reports; if a file is missing the script
falls back to any PNG in the Task 3 / Task 4 chart folders.

Usage:
    python scripts/build_report.py
"""

import sys
from datetime import date
from pathlib import Path

import pymupdf

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
TASK_DIR = SCRIPT_DIR.parent
REPO_ROOT = TASK_DIR.parent
REPORTS_DIR = TASK_DIR / "reports"

TASK3_CHARTS = REPO_ROOT / "apexplanet-data-analytics-task-3" / "reports" / "charts"
TASK4_CHARTS = REPO_ROOT / "apexplanet-data-analytics-task-4" / "reports" / "charts"

# ---------------------------------------------------------------------------
# Layout constants (A4 in points)
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = 595.28, 841.89
MARGIN = 46
CONTENT_W = PAGE_W - 2 * MARGIN

REG = "helv"      # Helvetica
BOLD = "hebo"     # Helvetica-Bold
ITAL = "heit"     # Helvetica-Oblique

BLACK = (0.10, 0.10, 0.10)
GREY = (0.35, 0.35, 0.35)
ACCENT = (0.05, 0.25, 0.45)
GRID = (0.65, 0.65, 0.65)


# ---------------------------------------------------------------------------
# Small text helpers
# ---------------------------------------------------------------------------
def text_width(text, fontname, size):
    """Width of a string in points."""
    return pymupdf.get_text_length(text, fontname=fontname, fontsize=size)


def wrap_runs(runs, width, size):
    """Wrap a list of (text, fontname) runs into lines that fit `width`."""
    lines = []
    current = []
    current_w = 0.0
    for text, fontname in runs:
        words = text.split(" ")
        for idx, word in enumerate(words):
            chunk = word + (" " if idx < len(words) - 1 else "")
            w = text_width(chunk, fontname, size)
            if current and current_w + w > width:
                lines.append(current)
                current = []
                current_w = 0.0
            current.append((chunk, fontname))
            current_w += w
    if current:
        lines.append(current)
    return lines


def draw_runs(page, x, y, lines, size, leading, color=BLACK):
    """Draw pre-wrapped lines. y is the baseline of the first line."""
    for line in lines:
        cx = x
        for chunk, fontname in line:
            if chunk.strip():
                page.insert_text((cx, y), chunk, fontname=fontname,
                                 fontsize=size, color=color)
            cx += text_width(chunk, fontname, size)
        y += leading
    return y


def paragraph(page, x, y, width, runs, size=9.5, leading=12.6, color=BLACK):
    """Draw a wrapped paragraph; return the next baseline y."""
    lines = wrap_runs(runs, width, size)
    return draw_runs(page, x, y, lines, size, leading, color)


def heading(page, x, y, text, size=12.5):
    """Section heading with a thin accent underline; return next y."""
    page.insert_text((x, y), text, fontname=BOLD, fontsize=size, color=ACCENT)
    page.draw_line(pymupdf.Point(x, y + 4), pymupdf.Point(x + CONTENT_W, y + 4),
                   color=ACCENT, width=0.8)
    return y + 20


def centered(page, y, text, size, fontname=BOLD, color=BLACK):
    """Center a single line horizontally."""
    w = text_width(text, fontname, size)
    x = (PAGE_W - w) / 2
    page.insert_text((x, y), text, fontname=fontname, fontsize=size, color=color)
    return y


# ---------------------------------------------------------------------------
# Table helper
# ---------------------------------------------------------------------------
def draw_table(page, x, y, col_widths, rows, size=9, row_h=15.5,
               header_bg=(0.90, 0.93, 0.96)):
    """Draw a simple bordered table. Returns the next y below the table."""
    for i, row in enumerate(rows):
        row_top = y + i * row_h
        for j, cell in enumerate(row):
            cell_x0 = x + sum(col_widths[:j])
            cell_x1 = cell_x0 + col_widths[j]
            rect = pymupdf.Rect(cell_x0, row_top, cell_x1, row_top + row_h)
            if i == 0:
                page.draw_rect(rect, color=GRID, fill=header_bg, width=0.5)
            else:
                page.draw_rect(rect, color=GRID, width=0.5)
            fontname = BOLD if i == 0 else REG
            page.insert_text((cell_x0 + 6, row_top + row_h - 4.6), str(cell),
                             fontname=fontname, fontsize=size, color=BLACK)
    return y + len(rows) * row_h


# ---------------------------------------------------------------------------
# Chart lookup / embedding
# ---------------------------------------------------------------------------
def find_chart(preferred_name):
    """Return the preferred chart if it exists, else any PNG fallback."""
    for folder in (TASK3_CHARTS, TASK4_CHARTS):
        candidate = folder / preferred_name
        if candidate.is_file():
            return candidate
    for folder in (TASK3_CHARTS, TASK4_CHARTS):
        if folder.is_dir():
            pngs = sorted(folder.glob("*.png"))
            if pngs:
                return pngs[0]
    return None


def embed_image(page, x, y, width, path, max_height=200):
    """Embed a PNG scaled to width, preserving aspect ratio. Returns next y."""
    if path is None:
        return y
    pix = pymupdf.Pixmap(str(path))
    aspect = pix.height / pix.width
    height = min(width * aspect, max_height)
    rect = pymupdf.Rect(x, y, x + width, y + height)
    page.insert_image(rect, filename=str(path), keep_proportion=True)
    return y + height


# ---------------------------------------------------------------------------
# Page 1
# ---------------------------------------------------------------------------
EXEC_SUMMARY = (
    "Over the four-year period from January 2014 to December 2017 the Superstore "
    "recorded $2,297,200.86 in total sales and $286,397.02 in profit across 5,009 "
    "orders placed by 793 customers, a 12.47% profit margin. The average order was "
    "worth $458.61 and carried a 15.62% discount, and profitability turns negative "
    "once discounts pass the 20% mark. Technology is the strongest category by "
    "profit ($145,454.95), the West is the largest region by sales ($725,457.82) "
    "while the Central region is the weakest on margin at 7.92%. Demand is strongly "
    "seasonal, peaking every November and December, with November 2017 alone "
    "reaching $118,447.83. The results point to three practical levers: disciplined "
    "discounting, seasonal planning and segment-specific marketing."
)

KPI_ROWS = [
    ["KPI", "Value"],
    ["Total Sales", "$2,297,200.86"],
    ["Total Profit", "$286,397.02"],
    ["Profit Margin", "12.47%"],
    ["Orders", "5,009"],
    ["Customers", "793"],
    ["Products", "1,862"],
    ["Average Order Value", "$458.61"],
    ["Average Discount", "15.62%"],
]


def build_page_1(page):
    y = MARGIN + 8
    centered(page, y, "Superstore Sales Analysis - Executive Summary", 17)
    y += 16
    centered(page, y, "ApexPlanet Data Analytics Internship - Task 5 Final Report",
             9.5, fontname=REG, color=GREY)
    y += 8
    page.draw_line(pymupdf.Point(MARGIN, y), pymupdf.Point(PAGE_W - MARGIN, y),
                   color=ACCENT, width=1.0)
    y += 22

    y = heading(page, MARGIN, y, "Executive Summary")
    y = paragraph(page, MARGIN, y + 2, CONTENT_W, [(EXEC_SUMMARY, REG)],
                  size=9.5, leading=12.6)
    y += 10

    y = heading(page, MARGIN, y, "Key Performance Indicators")
    y = draw_table(page, MARGIN, y + 2, [CONTENT_W * 0.5, CONTENT_W * 0.5],
                   KPI_ROWS, size=9.5, row_h=17)
    y += 18

    y = heading(page, MARGIN, y, "Supporting Charts")
    chart1 = find_chart("01_monthly_sales_line.png")
    chart2 = find_chart("02_sales_by_category_bar.png")
    gap = 16
    col_w = (CONTENT_W - gap) / 2
    top = y + 2
    next1 = embed_image(page, MARGIN, top, col_w, chart1, max_height=200)
    next2 = embed_image(page, MARGIN + col_w + gap, top, col_w, chart2, max_height=200)
    caption_y = max(next1, next2) + 12
    page.insert_text((MARGIN, caption_y), "Figure 1 - Monthly sales trend (2014-2017)",
                     fontname=ITAL, fontsize=8, color=GREY)
    page.insert_text((MARGIN + col_w + gap, caption_y),
                     "Figure 2 - Total sales by category",
                     fontname=ITAL, fontsize=8, color=GREY)


# ---------------------------------------------------------------------------
# Page 2
# ---------------------------------------------------------------------------
INSIGHTS = [
    ("Seasonality is strong.",
     "Sales peak every November and December; November 2017 hit $118,447.83 and the "
     "seasonal strength score is 0.805 (trend strength 0.279), so demand is far from "
     "flat across the year."),
    ("Discounting destroys margin.",
     "Profit turns negative above a 20% discount and at 41%+ the margin is -77.40%, "
     "losing $99,558.59 in total; discounted lines average -$6.66 profit versus "
     "+$66.90 at full price (p ~ 4.4e-55)."),
    ("Technology is the profit engine.",
     "Technology delivered $145,454.95 of profit, while Furniture's $741,999.80 of "
     "sales produced only $18,451.27 - high revenue with thin return."),
    ("Customer value is concentrated.",
     "264 Champions (33.3% of customers) spend $5,024.46 each versus $1,645.11 for "
     "Discount seekers; even the top spender, Sean Miller, is unprofitable at "
     "-$1,980.74."),
    ("Growth and margin live in different regions.",
     "The West is the largest region by sales ($725,457.82) while the Central region "
     "is the weakest on margin at just 7.92%, so a single national playbook misallocates effort."),
]

RECOMMENDATIONS = [
    ("Cap routine discounts and reprice the 21%+ bands.",
     "Reserve deep discounts for genuine clearance only, since every point of discount "
     "past 20% erodes margin directly (41%+ loses money at a -77.40% margin)."),
    ("Plan stock, staffing and targets around the Nov/Dec peak.",
     "Budget against the seasonal curve instead of a flat run-rate; this also sharpens "
     "forecasting, which is currently limited (3-month moving-average backtest MAPE 50.58%)."),
    ("Run segment-specific plays.",
     "Loyalty rewards for Champions, cross-sell for the Steady core (34.4% of customers), "
     "bundle pricing instead of percentage-off for Discount seekers, and one low-cost "
     "reactivation email for the 88 Dormant customers."),
]


def build_page_2(page):
    y = MARGIN + 8
    centered(page, y, "Insights, Recommendations & Next Steps", 15)
    y += 9
    page.draw_line(pymupdf.Point(MARGIN, y), pymupdf.Point(PAGE_W - MARGIN, y),
                   color=ACCENT, width=1.0)
    y += 22

    y = heading(page, MARGIN, y, "Top 5 Insights")
    for i, (label, body) in enumerate(INSIGHTS, start=1):
        runs = [(f"{i}. {label} ", BOLD), (body, REG)]
        y = paragraph(page, MARGIN, y + 2, CONTENT_W, runs, size=9.5, leading=12.6)
        y += 7

    y += 4
    y = heading(page, MARGIN, y, "Business Recommendations")
    for i, (label, body) in enumerate(RECOMMENDATIONS, start=1):
        runs = [(f"{i}. {label} ", BOLD), (body, REG)]
        y = paragraph(page, MARGIN, y + 2, CONTENT_W, runs, size=9.5, leading=12.6)
        y += 7

    # Footer (two short lines so nothing runs off the page)
    footer_y = PAGE_H - MARGIN + 6
    page.draw_line(pymupdf.Point(MARGIN, footer_y - 18),
                   pymupdf.Point(PAGE_W - MARGIN, footer_y - 18),
                   color=GRID, width=0.6)
    footer_line1 = ("Data source: data/superstore_cleaned.csv "
                    "(9,994 rows, Jan 2014 - Dec 2017)")
    footer_line2 = (f"Generated {date.today().isoformat()} by "
                    "scripts/automate_pipeline.py  |  ApexPlanet Data Analytics "
                    "Internship - Task 5 Final Report")
    page.insert_text((MARGIN, footer_y - 7), footer_line1, fontname=REG,
                     fontsize=8, color=GREY)
    page.insert_text((MARGIN, footer_y + 3), footer_line2, fontname=REG,
                     fontsize=8, color=GREY)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv=None):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "Task5_Final_Report.pdf"

    doc = pymupdf.open()
    page1 = doc.new_page(width=PAGE_W, height=PAGE_H)
    build_page_1(page1)
    page2 = doc.new_page(width=PAGE_W, height=PAGE_H)
    build_page_2(page2)

    doc.set_metadata({
        "title": "Superstore Sales Analysis - Executive Summary",
        "author": "ApexPlanet Data Analytics Internship",
        "subject": "Task 5 Final Report",
    })
    doc.save(str(out_path), deflate=True)
    pages = doc.page_count
    doc.close()

    size = out_path.stat().st_size
    print(f"Report written : {out_path}")
    print(f"Pages          : {pages}")
    print(f"Size           : {size} bytes")
    if pages != 2:
        print("WARNING: expected exactly 2 pages", file=sys.stderr)
        return 1
    print("REPORT OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
