"""Generate a synthetic commercial invoice PDF for the extraction golden-case test.

This is a CLEAN, digital-text invoice for a chemical shipment — useful as a happy-path smoke test for
the extraction agent, NOT a substitute for real (often scanned/photographed) documents. See
tests/fixtures/README.md.

Run from apps/api:
    uv run python tests/fixtures/generate_sample_invoice.py

Writes tests/fixtures/sample_invoice.pdf (gitignored).
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).parent / "sample_invoice.pdf"

# Goods are HS chapter 28/29/38 chemicals, the v1 target domain.
LINE_ITEMS = [
    # description, qty, unit, unit price (USD), amount (USD), country of origin
    (
        "Sodium Hydroxide (Caustic Soda) Flakes 99% min",
        "500",
        "bags x 25kg",
        "21.50",
        "10,750.00",
        "China",
    ),
    (
        "Citric Acid Monohydrate BP/USP grade",
        "200",
        "bags x 25kg",
        "33.00",
        "6,600.00",
        "China",
    ),
    (
        "Titanium Dioxide Rutile R-2196",
        "100",
        "bags x 25kg",
        "62.00",
        "6,200.00",
        "China",
    ),
    (
        "Soda Ash Dense (Sodium Carbonate)",
        "300",
        "bags x 25kg",
        "18.00",
        "5,400.00",
        "China",
    ),
]
TOTAL_USD = "28,950.00"


def build() -> None:
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    small = styles["Normal"].clone("small")
    small.fontSize = 8
    title = styles["Title"].clone("inv_title")
    title.fontSize = 18

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title="Commercial Invoice",
    )

    story = []
    story.append(Paragraph("COMMERCIAL INVOICE", title))
    story.append(Spacer(1, 6 * mm))

    # Seller / buyer / invoice meta as a 2-column header block.
    header = Table(
        [
            [
                Paragraph(
                    "<b>Seller / Exporter</b><br/>"
                    "Jiangsu Huaxin Chemical Co., Ltd<br/>"
                    "No. 88 Yangtze Road, Nanjing, Jiangsu, China<br/>"
                    "Tel: +86 25 8412 7700",
                    normal,
                ),
                Paragraph(
                    "<b>Invoice No.:</b> HX-2026-0517<br/>"
                    "<b>Date:</b> 17 May 2026<br/>"
                    "<b>Incoterm:</b> CIF Apapa, Lagos<br/>"
                    "<b>Currency:</b> USD",
                    normal,
                ),
            ],
            [
                Paragraph(
                    "<b>Buyer / Consignee</b><br/>"
                    "Lagos Allied Importers Ltd<br/>"
                    "14 Creek Road, Apapa, Lagos, Nigeria<br/>"
                    "RC 1184502",
                    normal,
                ),
                Paragraph(
                    "<b>Port of Loading:</b> Shanghai, China<br/>"
                    "<b>Port of Discharge:</b> Apapa, Lagos<br/>"
                    "<b>Vessel:</b> MV Ocean Trader / V.226W<br/>"
                    "<b>Payment:</b> 30% T/T deposit, 70% against B/L",
                    normal,
                ),
            ],
        ],
        colWidths=[90 * mm, 84 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 6 * mm))

    # Goods table.
    rows = [
        [
            "Description of Goods",
            "Qty",
            "Unit",
            "Unit Price\n(USD)",
            "Amount\n(USD)",
            "Origin",
        ]
    ]
    for desc, qty, unit, price, amount, origin in LINE_ITEMS:
        rows.append([Paragraph(desc, small), qty, unit, price, amount, origin])
    rows.append(["", "", "", "TOTAL CIF", TOTAL_USD, ""])

    goods = Table(
        rows, colWidths=[66 * mm, 14 * mm, 24 * mm, 24 * mm, 28 * mm, 18 * mm]
    )
    goods.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ALIGN", (3, 1), (4, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEABOVE", (3, -1), (4, -1), 0.75, colors.black),
                ("FONTNAME", (3, -1), (4, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(goods)
    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph(
            "Total amount in words: US Dollars Twenty-Eight Thousand Nine Hundred and Fifty Only.",
            normal,
        )
    )
    story.append(Spacer(1, 10 * mm))
    story.append(
        Paragraph(
            "We certify that this invoice is true and correct.<br/><br/>"
            "For Jiangsu Huaxin Chemical Co., Ltd<br/><br/>______________________<br/>"
            "Authorised Signature",
            normal,
        )
    )

    doc.build(story)


if __name__ == "__main__":
    build()
    print(f"Wrote {OUTPUT}")
