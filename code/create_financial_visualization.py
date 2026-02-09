"""
Financial Visualization for LinkedIn Post
Creates a clean, professional visualization of:
1. 3-Year Cash Flow Model
2. Scenario Stress Test (Conservative, Base, Optimistic)
3. Key Assumptions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# Set style for clean, professional look
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'

# =============================================================================
# LOAD DATA
# =============================================================================

cash_flows = pd.read_csv('outputs/financial_cash_flows.csv')
scenarios = pd.read_csv('outputs/financial_scenarios.csv')
summary = pd.read_csv('outputs/financial_summary.csv')

# Extract key metrics
capex = summary['Total_Capex'].iloc[0]
npv_3year = summary['NPV_3Year'].iloc[0]
payback_years = summary['Payback_Period_Years'].iloc[0]
roi_pct = summary['ROI_Percentage'].iloc[0]
discount_rate = summary['Discount_Rate'].iloc[0]
facilities = summary['Facilities_Opened'].iloc[0]

# =============================================================================
# CREATE FIGURE
# =============================================================================

fig = plt.figure(figsize=(16, 10), facecolor='white')
gs = GridSpec(2, 3, figure=fig, height_ratios=[1.2, 1], width_ratios=[1.5, 1, 1],
              hspace=0.35, wspace=0.3)

# Color palette
colors = {
    'capex': '#E74C3C',      # Red for investment
    'revenue': '#27AE60',     # Green for revenue
    'costs': '#F39C12',       # Orange for costs
    'net_cash': '#3498DB',    # Blue for net cash flow
    'conservative': '#95A5A6', # Gray
    'base': '#3498DB',        # Blue
    'optimistic': '#27AE60',  # Green
    'accent': '#2C3E50'       # Dark blue for text
}

# =============================================================================
# PANEL 1: CASH FLOW WATERFALL (Top Left - spans 2 columns)
# =============================================================================

ax1 = fig.add_subplot(gs[0, :2])

years = ['Year 0\n(Investment)', 'Year 1', 'Year 2', 'Year 3']
net_cash_flows = cash_flows['Net_Cash_Flow'].values

# Create bar positions
x = np.arange(len(years))
bar_width = 0.6

# Plot bars with conditional colors
bar_colors = [colors['capex'] if v < 0 else colors['net_cash'] for v in net_cash_flows]
bars = ax1.bar(x, net_cash_flows/1e6, width=bar_width, color=bar_colors, 
               edgecolor='white', linewidth=2, zorder=3)

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, net_cash_flows)):
    height = bar.get_height()
    label_y = height + 0.15 if height > 0 else height - 0.35
    ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
             f'${val/1e6:.2f}M', ha='center', va='bottom' if height > 0 else 'top',
             fontsize=12, fontweight='bold', color=colors['accent'])

# Add cumulative line
cumulative = np.cumsum(net_cash_flows)
ax1.plot(x, cumulative/1e6, 'o-', color=colors['accent'], linewidth=2.5, 
         markersize=8, zorder=4, label='Cumulative Cash Flow')

# Add cumulative values
for i, (xi, val) in enumerate(zip(x, cumulative)):
    offset = 0.5 if val > 0 else -0.5
    ax1.annotate(f'${val/1e6:.2f}M', (xi, val/1e6), 
                 textcoords="offset points", xytext=(0, 15 if val > 0 else -20),
                 ha='center', fontsize=9, color=colors['accent'], style='italic')

# Styling
ax1.axhline(y=0, color='gray', linestyle='-', linewidth=1, zorder=1)
ax1.set_xlabel('')
ax1.set_ylabel('Cash Flow ($ Millions)', fontweight='bold')
ax1.set_title('3-Year Cash Flow Model', fontsize=16, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(years, fontsize=11)
ax1.set_ylim(-3, 5.5)
ax1.legend(loc='upper left', fontsize=10)

# Add payback indicator
payback_months = payback_years * 12
ax1.axvline(x=payback_years, color=colors['revenue'], linestyle='--', linewidth=2, alpha=0.7)
ax1.annotate(f'Payback: {payback_months:.0f} months', 
             xy=(payback_years, 4.5), fontsize=11, fontweight='bold',
             color=colors['revenue'], ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=colors['revenue']))

# =============================================================================
# PANEL 2: KEY METRICS (Top Right)
# =============================================================================

ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')

# Key metrics box
metrics_text = f"""
┌────────────────────────────────┐
│     KEY FINANCIAL METRICS      │
├────────────────────────────────┤
│                                │
│  Investment:     $2.25M        │
│                                │
│  3-Year NPV:     $7.95M        │
│                                │
│  Payback:        7 months      │
│                                │
│  ROI:            448%          │
│  (149% annualized)             │
│                                │
│  Discount Rate:  10%           │
│                                │
└────────────────────────────────┘
"""

ax2.text(0.5, 0.65, metrics_text, transform=ax2.transAxes, fontsize=12,
         verticalalignment='center', horizontalalignment='center',
         fontfamily='monospace', color=colors['accent'],
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#ECF0F1', edgecolor=colors['base'], linewidth=2))

# Facilities info
facilities_text = "Facilities: Fresno, CA + Reno, NV"
ax2.text(0.5, 0.18, facilities_text, transform=ax2.transAxes, fontsize=11,
         verticalalignment='center', horizontalalignment='center',
         fontweight='bold', color=colors['accent'])

# =============================================================================
# PANEL 3: SCENARIO STRESS TEST (Bottom Left)
# =============================================================================

ax3 = fig.add_subplot(gs[1, 0])

# Reorder scenarios for visual impact
scenario_order = ['Conservative', 'Base Case', 'Optimistic']
scenario_npvs = []
for s in scenario_order:
    npv = scenarios[scenarios['Scenario'] == s]['NPV'].values[0]
    scenario_npvs.append(npv)

scenario_colors = [colors['conservative'], colors['base'], colors['optimistic']]

bars3 = ax3.barh(scenario_order, [n/1e6 for n in scenario_npvs], 
                  color=scenario_colors, edgecolor='white', linewidth=2, height=0.6)

# Add value labels
for bar, npv in zip(bars3, scenario_npvs):
    width = bar.get_width()
    ax3.text(width + 0.3, bar.get_y() + bar.get_height()/2,
             f'${npv/1e6:.2f}M', va='center', ha='left',
             fontsize=12, fontweight='bold', color=colors['accent'])

ax3.set_xlabel('NPV ($ Millions)', fontweight='bold')
ax3.set_title('Scenario Stress Test', fontsize=14, fontweight='bold', pad=10)
ax3.set_xlim(0, 12)

# Add vertical line for investment
ax3.axvline(x=2.25, color=colors['capex'], linestyle='--', linewidth=2, alpha=0.7)
ax3.text(2.25, 2.7, 'Investment\n$2.25M', ha='center', fontsize=9, color=colors['capex'])

# =============================================================================
# PANEL 4: SCENARIO DETAILS TABLE (Bottom Center)
# =============================================================================

ax4 = fig.add_subplot(gs[1, 1])
ax4.axis('off')

# Create scenario details table
table_data = [
    ['Scenario', 'Growth', 'Inflation', 'Price'],
    ['Conservative', '0%', '4%', '-10%'],
    ['Base Case', '3%', '2%', '0%'],
    ['Optimistic', '5%', '1%', '+10%']
]

table = ax4.table(cellText=table_data, loc='center', cellLoc='center',
                  colWidths=[0.35, 0.22, 0.22, 0.21])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 2)

# Style header row
for j in range(4):
    table[(0, j)].set_facecolor(colors['base'])
    table[(0, j)].set_text_props(color='white', fontweight='bold')

# Style data rows
row_colors = ['#F8F9FA', 'white', '#F8F9FA']
for i in range(1, 4):
    for j in range(4):
        table[(i, j)].set_facecolor(row_colors[i-1])

ax4.set_title('Scenario Assumptions', fontsize=14, fontweight='bold', pad=10, y=0.85)

# =============================================================================
# PANEL 5: MODEL ASSUMPTIONS (Bottom Right)
# =============================================================================

ax5 = fig.add_subplot(gs[1, 2])
ax5.axis('off')

assumptions_text = """
MODEL ASSUMPTIONS

Revenue Recovery (per unit):
• Grade A (25%): $400 resale
• Grade B (45%): $250 refurb
• Grade C (30%): $50 parts

Operating Costs:
• Grade A handling: $10/unit
• Grade B refurbishment: $55/unit
• Grade C processing: $12/unit
• Annual facility fixed costs:
  Fresno: $820K | Reno: $720K

Base Volume: 28,140 returns/year
Baseline Recovery: $22/unit (bulk)
"""

ax5.text(0.05, 0.95, assumptions_text, transform=ax5.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='left',
         fontfamily='sans-serif', color=colors['accent'],
         linespacing=1.4)

# =============================================================================
# FINAL STYLING
# =============================================================================

# Add main title
fig.suptitle('Reverse Logistics Network: Financial Business Case', 
             fontsize=20, fontweight='bold', y=0.98, color=colors['accent'])

# Add subtitle
fig.text(0.5, 0.93, 'Smartphone Refurbishment Network | 55 California Stores | Fresno + Reno Facilities',
         ha='center', fontsize=12, color='gray', style='italic')

# Add footer
fig.text(0.02, 0.01, 'Analysis Date: February 2026 | Discount Rate: 10% | 3-Year Horizon',
         fontsize=9, color='gray', style='italic')
fig.text(0.98, 0.01, 'Data Source: Gurobi Optimization Model',
         fontsize=9, color='gray', style='italic', ha='right')

plt.tight_layout(rect=[0, 0.03, 1, 0.92])

# Save the figure
plt.savefig('visualizations/financial_cash_flow_model.png', dpi=300, 
            bbox_inches='tight', facecolor='white', edgecolor='none')

print("✅ Visualization saved to: visualizations/financial_cash_flow_model.png")

# Also save a version optimized for LinkedIn (slightly different aspect ratio)
fig2 = plt.figure(figsize=(14, 9), facecolor='white')
gs2 = GridSpec(2, 3, figure=fig2, height_ratios=[1.2, 1], width_ratios=[1.5, 1, 1],
               hspace=0.35, wspace=0.3)

# Recreate all panels for LinkedIn version
# Panel 1: Cash Flow
ax1 = fig2.add_subplot(gs2[0, :2])
bar_colors = [colors['capex'] if v < 0 else colors['net_cash'] for v in net_cash_flows]
bars = ax1.bar(x, net_cash_flows/1e6, width=bar_width, color=bar_colors, 
               edgecolor='white', linewidth=2, zorder=3)
for i, (bar, val) in enumerate(zip(bars, net_cash_flows)):
    height = bar.get_height()
    label_y = height + 0.15 if height > 0 else height - 0.35
    ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
             f'${val/1e6:.2f}M', ha='center', va='bottom' if height > 0 else 'top',
             fontsize=12, fontweight='bold', color=colors['accent'])
cumulative = np.cumsum(net_cash_flows)
ax1.plot(x, cumulative/1e6, 'o-', color=colors['accent'], linewidth=2.5, 
         markersize=8, zorder=4, label='Cumulative Cash Flow')
for i, (xi, val) in enumerate(zip(x, cumulative)):
    ax1.annotate(f'${val/1e6:.2f}M', (xi, val/1e6), 
                 textcoords="offset points", xytext=(0, 15 if val > 0 else -20),
                 ha='center', fontsize=9, color=colors['accent'], style='italic')
ax1.axhline(y=0, color='gray', linestyle='-', linewidth=1, zorder=1)
ax1.set_ylabel('Cash Flow ($ Millions)', fontweight='bold')
ax1.set_title('3-Year Cash Flow Model', fontsize=16, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(years, fontsize=11)
ax1.set_ylim(-3, 5.5)
ax1.legend(loc='upper left', fontsize=10)
ax1.axvline(x=payback_years, color=colors['revenue'], linestyle='--', linewidth=2, alpha=0.7)
ax1.annotate(f'Payback: {payback_months:.0f} months', 
             xy=(payback_years, 4.5), fontsize=11, fontweight='bold',
             color=colors['revenue'], ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=colors['revenue']))

# Panel 2: Key Metrics
ax2 = fig2.add_subplot(gs2[0, 2])
ax2.axis('off')
ax2.text(0.5, 0.65, metrics_text, transform=ax2.transAxes, fontsize=12,
         verticalalignment='center', horizontalalignment='center',
         fontfamily='monospace', color=colors['accent'],
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#ECF0F1', edgecolor=colors['base'], linewidth=2))
ax2.text(0.5, 0.18, facilities_text, transform=ax2.transAxes, fontsize=11,
         verticalalignment='center', horizontalalignment='center',
         fontweight='bold', color=colors['accent'])

# Panel 3: Scenario Stress Test
ax3 = fig2.add_subplot(gs2[1, 0])
bars3 = ax3.barh(scenario_order, [n/1e6 for n in scenario_npvs], 
                  color=scenario_colors, edgecolor='white', linewidth=2, height=0.6)
for bar, npv in zip(bars3, scenario_npvs):
    width = bar.get_width()
    ax3.text(width + 0.3, bar.get_y() + bar.get_height()/2,
             f'${npv/1e6:.2f}M', va='center', ha='left',
             fontsize=12, fontweight='bold', color=colors['accent'])
ax3.set_xlabel('NPV ($ Millions)', fontweight='bold')
ax3.set_title('Scenario Stress Test', fontsize=14, fontweight='bold', pad=10)
ax3.set_xlim(0, 12)
ax3.axvline(x=2.25, color=colors['capex'], linestyle='--', linewidth=2, alpha=0.7)
ax3.text(2.25, 2.7, 'Investment\n$2.25M', ha='center', fontsize=9, color=colors['capex'])

# Panel 4: Scenario Details
ax4 = fig2.add_subplot(gs2[1, 1])
ax4.axis('off')
table = ax4.table(cellText=table_data, loc='center', cellLoc='center',
                  colWidths=[0.35, 0.22, 0.22, 0.21])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 2)
for j in range(4):
    table[(0, j)].set_facecolor(colors['base'])
    table[(0, j)].set_text_props(color='white', fontweight='bold')
for i in range(1, 4):
    for j in range(4):
        table[(i, j)].set_facecolor(row_colors[i-1])
ax4.set_title('Scenario Assumptions', fontsize=14, fontweight='bold', pad=10, y=0.85)

# Panel 5: Model Assumptions
ax5 = fig2.add_subplot(gs2[1, 2])
ax5.axis('off')
ax5.text(0.05, 0.95, assumptions_text, transform=ax5.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='left',
         fontfamily='sans-serif', color=colors['accent'],
         linespacing=1.4)

# Final styling
fig2.suptitle('Reverse Logistics Network: Financial Business Case', 
              fontsize=20, fontweight='bold', y=0.98, color=colors['accent'])
fig2.text(0.5, 0.93, 'Smartphone Refurbishment Network | 55 California Stores | Fresno + Reno Facilities',
          ha='center', fontsize=12, color='gray', style='italic')
fig2.text(0.02, 0.01, 'Analysis Date: February 2026 | Discount Rate: 10% | 3-Year Horizon',
          fontsize=9, color='gray', style='italic')
fig2.text(0.98, 0.01, 'Data Source: Gurobi Optimization Model',
          fontsize=9, color='gray', style='italic', ha='right')

plt.tight_layout(rect=[0, 0.03, 1, 0.92])
plt.savefig('visualizations/financial_linkedin_post.png', dpi=300, 
            bbox_inches='tight', facecolor='white', edgecolor='none')

print("✅ LinkedIn version saved to: visualizations/financial_linkedin_post.png")
print("\n📊 Both visualizations created successfully!")
