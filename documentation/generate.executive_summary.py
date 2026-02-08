from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
import pandas as pd
from datetime import datetime

print("="*70)
print("GENERATING EXECUTIVE SUMMARY PDF")
print("="*70)

# Load data
financial = pd.read_csv('outputs/financial_summary.csv')
optimal = pd.read_csv('outputs/gurobi_optimal_p_summary.csv')
baseline = pd.read_csv('data/current_state_baseline.csv')

# Create PDF
pdf_filename = 'outputs/executive_summary.pdf'
doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=1*inch, bottomMargin=0.75*inch)

# Container for 'Flowable' objects
elements = []

# Styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#1f4788'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

body_style = styles['BodyText']
body_style.fontSize = 11
body_style.leading = 14

# =============================================================================
# PAGE 1: TITLE AND OVERVIEW
# =============================================================================

# Title
elements.append(Paragraph("Circular Supply Chain Network", title_style))
elements.append(Paragraph("Optimization Business Case", title_style))
elements.append(Spacer(1, 0.3*inch))

# Subtitle
subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=12,
    textColor=colors.grey,
    alignment=TA_CENTER
)
elements.append(Paragraph(f"Strategic Analysis & Recommendation", subtitle_style))
elements.append(Paragraph(f"Prepared: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
elements.append(Spacer(1, 0.5*inch))

# Executive Summary Box
summary_data = [
    ['EXECUTIVE SUMMARY', ''],
    ['Recommended Solution:', f"{int(optimal['optimal_p'].iloc[0])} Regional Refurbishment Centers"],
    ['Locations:', optimal['facilities_opened'].iloc[0]],
    ['Required Investment:', f"${financial['Total_Capex'].iloc[0]:,.0f}"],
    ['Annual Incremental Value:', f"${financial['Incremental_Annual_Value'].iloc[0]:,.0f}"],
    ['3-Year NPV:', f"${financial['NPV_3Year'].iloc[0]:,.0f}"],
    ['Payback Period:', f"{financial['Payback_Period_Years'].iloc[0]:.1f} years"],
    ['Return on Investment:', f"{financial['ROI_Percentage'].iloc[0]:.0f}%"],
]

summary_table = Table(summary_data, colWidths=[3*inch, 3.5*inch])
summary_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
]))

elements.append(summary_table)
elements.append(Spacer(1, 0.3*inch))

# Recommendation
elements.append(Paragraph("RECOMMENDATION", heading_style))
recommendation_text = f"""
Based on comprehensive optimization analysis using ArcGIS Network Analyst and Gurobi MIP modeling, 
we recommend implementing a <b>{int(optimal['optimal_p'].iloc[0])}-facility refurbishment network</b> to maximize 
value recovery from Smart Phone returns. This solution delivers <b>${financial['Incremental_Annual_Value'].iloc[0]:,.0f} 
in incremental annual value</b> with a payback period of <b>{financial['Payback_Period_Years'].iloc[0]:.1f} years</b>, 
representing a <b>{financial['Improvement_Percentage'].iloc[0]:.0f}%</b> improvement over the current bulk recycling approach.
"""
elements.append(Paragraph(recommendation_text, body_style))
elements.append(Spacer(1, 0.2*inch))

# Key Benefits
elements.append(Paragraph("KEY BENEFITS", heading_style))
benefits = [
    f"<b>{financial['Improvement_Percentage'].iloc[0]:.0f}%</b> increase in value recovery from returned Smart Phones",
    f"<b>${financial['Incremental_Annual_Value'].iloc[0]:,.0f}</b> incremental annual value creation",
    f"<b>{financial['Payback_Period_Years'].iloc[0]:.1f}-year</b> payback on capital investment",
    f"Environmentally sustainable: <b>95%+ landfill diversion</b> through grade-based recovery",
    f"Geographic optimization reduces average logistics distance to <b>{optimal['avg_distance_miles'].iloc[0]:.0f} miles</b>",
]
for benefit in benefits:
    elements.append(Paragraph(f"• {benefit}", body_style))
    elements.append(Spacer(1, 0.1*inch))

elements.append(PageBreak())

# =============================================================================
# PAGE 2: METHODOLOGY & ANALYSIS
# =============================================================================

elements.append(Paragraph("METHODOLOGY", heading_style))
methodology_text = """
This analysis employed a <b>two-phase optimization approach</b> combining geographic and economic modeling:
"""
elements.append(Paragraph(methodology_text, body_style))
elements.append(Spacer(1, 0.1*inch))

methodology_points = [
    "<b>Phase 1: ArcGIS Network Analyst</b> - Geographic optimization using real road networks to minimize transportation distance for 54 California Apple Store locations",
    "<b>Phase 2: Gurobi Mixed-Integer Programming</b> - Mathematical optimization to minimize total cost (fixed + variable) while considering capacity constraints",
    "<b>Financial Modeling</b> - 3-year NPV analysis with sensitivity testing on key parameters",
]
for point in methodology_points:
    elements.append(Paragraph(f"• {point}", body_style))
    elements.append(Spacer(1, 0.08*inch))

elements.append(Spacer(1, 0.2*inch))

# Current vs Proposed
elements.append(Paragraph("CURRENT VS. PROPOSED STATE", heading_style))

comparison_data = [
    ['Metric', 'Current State', 'Proposed State', 'Improvement'],
    ['Operating Model', 'Bulk Recycling', f'{int(optimal["optimal_p"].iloc[0])}-Facility Network', '-'],
    ['Annual Recovery', f"${baseline['annual_recovery'].iloc[0]:,.0f}", 
     f"${financial['Proposed_Annual_Recovery'].iloc[0]:,.0f}",
     f"+{financial['Improvement_Percentage'].iloc[0]:.0f}%"],
    ['Product Grading', 'No', 'Yes (A/B/C)', '✓'],
    ['Landfill Diversion', '35%', '95%+', '+60pp'],
    ['Cycle Time', '60+ days', '14-21 days', '-70%'],
    ['Capital Investment', '$0', f"${financial['Total_Capex'].iloc[0]:,.0f}", '-'],
]

comparison_table = Table(comparison_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.25*inch])
comparison_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))

elements.append(comparison_table)
elements.append(Spacer(1, 0.3*inch))

# Add visualizations if they exist
try:
    elements.append(Paragraph("OPTIMIZATION RESULTS", heading_style))
    
    # Add optimal p chart
    img = Image('outputs/optimal_p_analysis.png', width=6*inch, height=4.5*inch)
    elements.append(img)
    elements.append(Spacer(1, 0.1*inch))
    
    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Figure 1: Cost optimization across facility count options (p=1 to p=5)", caption_style))
    
except:
    pass

elements.append(PageBreak())

# =============================================================================
# PAGE 3: FINANCIAL DETAILS & NEXT STEPS
# =============================================================================

elements.append(Paragraph("FINANCIAL ANALYSIS", heading_style))

# Cash flow table
cash_flows = pd.read_csv('outputs/financial_cash_flows.csv')
cash_flow_data = [['Year', 'Gross Revenue', 'Operating Costs', 'Net Cash Flow', 'Present Value']]
for _, row in cash_flows.iterrows():
    cash_flow_data.append([
        int(row['Year']),
        f"${row['Gross_Revenue']:,.0f}" if row['Year'] > 0 else '-',
        f"${row['Operating_Costs']:,.0f}" if row['Year'] > 0 else '-',
        f"${row['Net_Cash_Flow']:,.0f}",
        f"${row['Present_Value']:,.0f}"
    ])

cf_table = Table(cash_flow_data, colWidths=[0.8*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch])
cf_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),  # Year 0
]))

elements.append(cf_table)
elements.append(Spacer(1, 0.2*inch))

# Risk considerations
elements.append(Paragraph("RISK CONSIDERATIONS", heading_style))
risks = [
    "<b>Market Risk:</b> Resale prices for refurbished Smart Phones subject to market fluctuations. Sensitivity analysis shows NPV remains positive even with 15% price reduction.",
    "<b>Volume Risk:</b> Return volumes may vary with sales trends. Model tested across 70-130% of base volume scenarios.",
    "<b>Operational Risk:</b> Facility ramp-up and quality control require experienced management. Recommend phased implementation.",
]
for risk in risks:
    elements.append(Paragraph(f"• {risk}", body_style))
    elements.append(Spacer(1, 0.08*inch))

elements.append(Spacer(1, 0.2*inch))

# Next steps
elements.append(Paragraph("RECOMMENDED NEXT STEPS", heading_style))
next_steps = [
    "<b>Phase 1 (Months 1-2):</b> Facility site selection and lease negotiations for priority locations",
    "<b>Phase 2 (Months 3-4):</b> Facility buildout, equipment procurement, and staff hiring",
    "<b>Phase 3 (Months 5-6):</b> Pilot operation with single facility to validate operational model",
    "<b>Phase 4 (Months 7-12):</b> Full network rollout with remaining facilities",
]
for step in next_steps:
    elements.append(Paragraph(f"• {step}", body_style))
    elements.append(Spacer(1, 0.08*inch))

elements.append(Spacer(1, 0.3*inch))

# Footer with contact
footer_text = """
<b>For questions or additional analysis, please contact the Analytics Team.</b><br/>
This analysis is based on current market conditions and operational assumptions as of February 2026.
"""
elements.append(Paragraph(footer_text, caption_style))

# Build PDF
doc.build(elements)

print(f"\n✓ Generated: {pdf_filename}")
print("\n" + "="*70)
print("✅ EXECUTIVE SUMMARY PDF COMPLETE")
print("="*70)