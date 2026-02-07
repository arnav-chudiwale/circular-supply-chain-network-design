# Circular Supply Chain Network Optimization for Electronics Reverse Logistics

**Optimizing refurbishment center locations and routing for smartphone product returns using network optimization and geospatial analysis**

---

## Project Overview

This project designs an optimized reverse logistics network for a premium electronics retailer handling ~28,140 annual smartphone returns across 55 California retail locations. The solution determines optimal refurbishment center locations, routing assignments, and financial viability to transform product returns from a disposal cost into a value recovery operation.

**Current State:** Returns shipped to bulk recycler → $22/unit recovery ($619,080 annually)  
**Proposed State:** Grade-based refurbishment network → $168/unit average recovery ($6.7M+ annually)  
**Net Impact:** $5.8M incremental annual value with 3-4 month payback on infrastructure investment

---

## Problem Statement

Electronics retailers face three critical challenges in reverse logistics:

1. **No systematic product grading** - All returns treated identically regardless of condition (like-new vs. broken)
2. **No recovery infrastructure** - Lack of facilities to refurbish, test, or extract component value
3. **Time destroys value** - Smartphones depreciate $4/week; current 60+ day cycles burn revenue

**Business Question:** Where should refurbishment centers be located, and how should stores route returns to maximize value recovery while minimizing total system cost?

---

## Solution Approach

### 1. Network Optimization
- **Tool:** ArcGIS Network Analyst (Location-Allocation solver)
- **Method:** Minimize weighted impedance across 55 demand points (stores) to optimal facility locations
- **Validation:** Gurobi mixed-integer programming model

### 2. Financial Modeling
- **Tool:** Python (Gurobi Optimizer)
- **Method:** Multi-objective optimization balancing facility costs, transport costs, and value recovery
- **Output:** 3-year NPV, payback period, sensitivity analysis

### 3. Decision Support
- **Deliverables:** Interactive Power BI dashboards, Excel scenario calculator, ArcGIS network maps

---

## Data Foundation

### Store Locations (55 stores)
**Source:** Real Apple Store locations in California (verified coordinates from Apple.com, February 2026)

| Region | Count | Example Stores |
|--------|-------|----------------|
| Bay Area | 17 | Union Square SF, Stanford, Santana Row |
| Los Angeles | 18 | The Grove, Century City, Beverly Center |
| Orange County | 6 | Irvine Spectrum, Fashion Island, South Coast Plaza |
| San Diego | 5 | Fashion Valley, UTC, Carlsbad |
| Central/Other | 8 | Sacramento, Fresno, Bakersfield, Monterey |

**Data Files:**
- `store_locations.csv` - Store coordinates and basic information
- `stores_complete.csv` - Stores with returns and grading data
- `stores_with_returns.csv` - Alternative return volume dataset

**Data Structure:**
```
Store_ID | Store_Name | City | Lat | Lon | Store_Type | Annual_Sales | Return_Rate | Annual_Returns | Grade_A/B/C_Units
```

### Product Returns Volume
- **Total Annual Returns:** ~28,140 units
- **Store Segmentation:**
  - Flagship stores
  - Standard stores
- **Return Rate:** 7.1% average across all stores

### Product Grading Distribution
Based on smartphone return condition analysis:

| Grade | Percentage | Description | Recovery Strategy |
|-------|-----------|-------------|-------------------|
| **Grade A** | 25% | Like-new (buyer's remorse, wrong color) | Direct resale at 85% retail |
| **Grade B** | 45% | Refurbishable (minor damage, battery issues) | Repair → resale at 60% retail |
| **Grade C** | 30% | Parts/recycle (broken, water damage) | Component harvesting or material recycling |

### Candidate Facility Locations (5 sites)

| ID | Location | Coordinates | Annual Fixed Cost | Capacity | Notes |
|----|----------|-------------|-------------------|----------|-------|
| FC01 | Fremont (Bay Area) | 37.5485, -121.9886 | $1,050,000 | 25,000 units | Highest CA costs, central to 17 stores |
| FC02 | Ontario (LA Metro) | 34.0633, -117.6509 | $980,000 | 25,000 units | Serves 18 LA + 6 OC stores |
| FC03 | San Diego | 32.8312, -117.1225 | $920,000 | 20,000 units | Serves 5 San Diego stores |
| FC04 | Fresno (Central Valley) | 36.7783, -119.4179 | $820,000 | 20,000 units | Lower costs, central location |
| FC05 | Reno, NV | 39.5296, -119.8138 | $720,000 | 25,000 units | Out-of-state comparison (31% lower cost) |

**Facility Costs Source:** Statista 2024 California industrial real estate ($18.36/sqft annually for 50,000 sqft facility)

---

## Cost Parameters & Assumptions

### Current State Baseline
```
Bulk Recycler Model:
  - Payout rate: $22/unit (all grades combined)
  - Annual recovery: $619,080
  - Landfill diversion: 35%
  - Cycle time: 60+ days
```

### Proposed State Economics

**Recovery Values (net after processing):**
- Grade A resale price: $400/unit
- Grade B resale price: $250/unit
- Grade C parts value: $50/unit (component harvesting)

**Processing Costs:**
- Grade A handling: $10/unit (testing, data wipe, repackaging)
- Grade B refurbishment: $55/unit (screen/battery replacement)
- Grade C processing: $12/unit (disassembly labor)

**Transport Costs:**
- $0.08 per mile per unit (California LTL freight rates 2024)

**Time-Value Decay:**
- $4.00 per week depreciation (Source: SellCell.com 2024 iPhone depreciation report)
- Rationale: iPhones lose ~48% value in 12 months = 4% monthly = $4/week for $400 avg phone

### Key Assumptions

1. **Returns are uniformly distributed** across store network (no seasonal clustering)
2. **Grading accuracy:** 95% correct classification at store level
3. **Facility capacity:** Linear up to 25,000 units/year, no economies of scale modeled
4. **Transport:** Euclidean distance × 1.2 multiplier for actual road distance
5. **Resale channels:** Certified refurbished marketplace (no direct Apple channel conflict)
6. **Regulatory compliance:** All refurbished units meet Right to Repair standards

---

## Technical Implementation

### Technology Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Network Optimization** | ArcGIS Pro (Network Analyst) | Location-Allocation solver for facility placement |
| **Mathematical Validation** | Gurobi Optimizer (Python) | MIP model validation, sensitivity analysis |
| **Financial Modeling** | Python (pandas, NumPy) | NPV, payback, scenario analysis |
| **Visualization** | Power BI Desktop | Interactive dashboards |
| **Geospatial Analysis** | ArcGIS Pro | Network design maps, service area analysis |
| **Decision Support** | Excel | Scenario calculator for operations team |

### Optimization Model Formulation

**Objective Function:**
```
Minimize: Total_Cost = Σ(Facility_Fixed_Costs) + Σ(Transport_Costs) - Σ(Value_Recovery)

Subject to:
  - Each store assigned to exactly one facility
  - Facility capacity constraints (≤ 25,000 units/year)
  - Minimum service level (95% on-time processing)
  - Geographic coverage (all stores within 300 miles of assigned facility)
```

**Decision Variables:**
- Binary: Facility j is opened (yes/no)
- Binary: Store i assigned to facility j (yes/no)
- Continuous: Annual returns volume routed from store i to facility j

---

## Project Structure
(Current as of - 6th Feb 2026)
```
CircularSupplyChain/
├── code/
│   ├── Data Generation & Preparation:
│   │   ├── calculate_baseline.py                 # Calculates baseline metrics
│   │   ├── generate_candidate_facilities.py      # Generates facility locations
│   │   ├── generate_cost_parameters.py           # Generates cost data
│   │   ├── generate_grading_data.py              # Generates grading distributions
│   │   ├── generate_returns_data.py              # Generates return volumes
│   │   ├── generate_store_locations.py           # Generates store locations
│   │   ├── arcgis_facilities.py                  # Prepares facility data for ArcGIS
│   │   └── prepare_arcgis_supply.py              # Prepares supply points for ArcGIS
│   │
│   ├── Data Processing & Analysis:
│   │   ├── load_data_for_gurobi.py               # ✓ Loads data, creates distance matrix
│   │   └── analyze_arcgis_results.py             # Analyzes ArcGIS results
│   │
│   └── Optimization Models (Gurobi):
│       ├── gurobi_model_distance.py              # ✓ MODEL #1: Distance Minimization
│       └── gurobi_model_cost.py                  # ✓ MODEL #2: Cost Minimization
│
├── data/
│   ├── store_locations.csv                       # 54 store locations
│   ├── stores_complete.csv                       # Stores with returns data
│   ├── stores_with_returns.csv                   # Return volumes
│   ├── candidate_facilities.csv                  # 5 candidate facilities
│   ├── cost_parameters.csv                       # Financial assumptions
│   ├── current_state_baseline.csv                # Baseline metrics
│   ├── gurobi_data_package.pkl                   # ✓ Preprocessed data package
│   └── distance_matrix.csv                       # ✓ Store-facility distances
│
├── ArcGIS Results/
│   ├── Network_Optimization.aprx                 # ArcGIS project
│   └── Index/                                    # Network indices
│
├── models/ └── [Optimization models]
│
├── outputs/
│   ├── ArcGIS Results:
│   │   ├── arc_gis_solution_facilities.csv       # Facility selections
│   │   ├── arc_gis_solution_stores.csv           # Store assignments
│   │   └── arcgis_solution_summary.csv           # Summary metrics
│   │
│   ├── Gurobi Model #1 (Distance):
│   │   ├── gurobi_distance_minimization_assignments.csv
│   │   ├── gurobi_distance_minimization_facility.csv
│   │   └── gurobi_distance_minimization_summary.csv
│   │
│   └── Gurobi Model #2 (Cost):
│       ├── gurobi_cost_assignments.csv           # ✓ Store assignments
│       ├── gurobi_cost_facility_stats.csv        # ✓ Facility stats
│       └── gurobi_cost_summary.csv               # ✓ Summary metrics
│
├── visualizations/ └── [Dashboards]
├── documentation/ └── [Documentation]
├── test/
│   ├── test_gurobi.py
│   ├── test_imports.py
│   ├── arcgis_issue_diagnose.py
│   └── check_facility_locations.py
│
└── README.md
```

---

## Results & Progress

### ✅ Data Preprocessing Completed (6th Feb 2026)

**Data Pipeline:**
- ✅ Loaded 54 stores with 28,140 units/year supply
- ✅ 5 candidate facilities with fixed costs: $720K-$1.05M/year
- ✅ Calculated 270 store-to-facility distance pairs using Haversine formula
- ✅ Applied 1.3x routing factor for actual road distances
- ✅ Created pickle data package for Gurobi optimization

**Distance Matrix Statistics:**
- Average distance: 291.26 miles
- Minimum: 6.60 miles | Maximum: 648.57 miles
- Total capacity: 115,000 units/year (4.09x demand)

---

### ✅ Completed: ArcGIS Network Analyst Optimization (6th Feb 2026)

**Network Design Outputs (FINALIZED):**
1. **Optimal facility:** 1 refurbishment center selected
   - **Location:** Los Angeles Metro (Ontario, CA)
   - **Coordinates:** 34.0633°N, 117.6509°W
   - **Capacity:** 25,000 units/year
   
2. **Store assignments:** All 54 stores optimally routed to Los Angeles Metro facility
   - **Total stores assigned:** 54
   - **Total annual returns routed:** 28,140 units
   
3. **Transport metrics:**
   - **Average distance per store:** 24.5 miles
   - **Total weighted distance:** 735,334 mile-units/year
   - **Average weighted distance:** 26.1 miles per unit

### Optimization Results Summary
| Metric | Value |
|--------|-------|
| Chosen Facility | Los Angeles Metro |
| Stores Assigned | 54 |
| Total Supply Routed | 28,140 units/year |
| Avg. Distance | 24.5 miles |
| Total Weighted Distance | 735,334 mile-miles/year |
| Avg Weighted Distance | 26.1 miles |

**Files Generated (6th Feb 2026):**
- `arc_gis_solution_facilities.csv` - Selected facility details
- `arc_gis_solution_stores.csv` - Store assignments and routings
- `arcgis_solution_summary.csv` - Summary metrics

---

### ✅ Completed: Gurobi Model #1 - Distance Minimization (6th Feb 2026)

**Problem:** Minimize total weighted transportation distance  
**Constraint:** Open exactly 2 facilities  
**Result:** Optimal solution found in 0.02 seconds (0% gap)

**Selected Facilities:**
1. **FC01 - San Francisco Bay Area**: 22 stores, 10,866 units (43% utilization), avg 43.85 miles
2. **FC02 - Los Angeles Metro**: 32 stores, 17,274 units (69% utilization), avg 60.90 miles

**Network Performance:** Total weighted distance = 1,528,331 mile-units, Avg = **54.31 miles/unit**

---

### ✅ Completed: Gurobi Model #2 - Cost Minimization (6th Feb 2026)

**Problem:** Minimize total annual cost (fixed + transport)  
**Constraint:** Open exactly 2 facilities  
**Result:** Optimal solution found in 0.01 seconds (0% gap)

**Selected Facilities:**
1. **FC02 - Los Angeles Metro**: $1,064,152.61/year total ($980K fixed + $84.2K transport)
2. **FC05 - Reno, NV**: $922,727.57/year total ($720K fixed + $202.7K transport)

**Network Performance:** 
| Metric | Value |
|--------|-------|
| **Total Annual Cost** | **$1,986,880.18** |
| Total Fixed Cost | $1,700,000.00 |
| Total Transport Cost | $286,880.18 |
| Avg Distance/unit | 127.43 miles |

**Savings vs Distance Model:** $165,386/year (7.7% reduction) by selecting lower-cost Reno facility

---

### Comparative Summary

| Model | Facilities | Avg Distance | Total Cost | Optimization |
|-------|-----------|----------|-----------|---|
| **ArcGIS** | LA Metro (1) | 26.1 mi | ~$1.04M | Distance only, 1-facility constraint |
| **Gurobi-Distance** | Bay Area + LA (2) | 54.3 mi | ~$2.15M | Pure distance minimization |
| **Gurobi-Cost** | LA + Reno (2) | 127.4 mi | **$1.99M** | **Best total cost** ✓ |

**Recommendation:** Use Gurobi-Cost model (LA Metro + Reno) for optimal financial performance ($1.99M annual cost with acceptable service trade-off).

### Expected Results (Phase 2)

### Network Design Outputs
1. **Optimal facility count:** ✅ DETERMINED = 1 facility (Los Angeles Metro)
2. **Facility locations:** ✅ SELECTED from 5 candidates → Ontario, CA
3. **Store assignments:** ✅ COMPLETED - All 54 stores assigned
4. **Transport network:** Routing map showing store-to-facility connections

### Financial Performance Metrics
- **Annual value recovery:** $6.7M-7.2M (projected)
- **Incremental value vs. baseline:** $5.8M-6.3M annually
- **Infrastructure investment:** $1.8M-2.1M (2-3 facilities)
- **Payback period:** 3-4 months
- **3-year NPV:** $15M+ (10% discount rate)
- **Landfill diversion:** 85% (from 35% baseline)
- **Cycle time reduction:** 60+ days → <15 days

### Sensitivity Analysis
Key variables tested (±20% variation):
1. Refurbishment cost ($44-66/unit)
2. Resale price ($272-408/unit for Grade A)
3. Returns volume (32,000-48,000 units)
4. Facility fixed costs ($640K-1.26M)
5. Transport costs ($0.064-0.096 per mile/unit)

---

## Execution Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Day 1** | 6-7 hours | Synthetic dataset generation, cost parameters, baseline model |
| **Day 2** | 7 hours | ArcGIS Network Analyst optimization, network design map |
| **Day 3** | 8 hours | Gurobi MIP model, financial analysis, sensitivity testing |
| **Day 4** | 7 hours | Power BI dashboards (4 interactive views) |
| **Day 5** | 6 hours | Excel tool, technical documentation |
| **Day 6** | 5 hours | GitHub repository, resume bullets, project summary |
| **Day 7** | 4 hours | Code review, final polish, deliverable verification |

**Total:** 7 days, 43-47 hours

---

## Key Insights & Learnings

### Why This Problem Matters

1. **Economic Impact:** Electronics retailers lose $6B+ annually to inefficient reverse logistics
2. **Regulatory Pressure:** EU Right to Repair, Extended Producer Responsibility laws mandate recovery infrastructure
3. **Competitive Advantage:** Circular economy capabilities differentiate market leaders
4. **Technical Complexity:** Reverse logistics harder than forward due to condition uncertainty, value decay, and multi-channel resale

### Skills Demonstrated

- **Network Optimization:** Facility location modeling using ArcGIS Location-Allocation
- **Operations Research:** MIP formulation, Gurobi solver implementation
- **Geospatial Analysis:** GIS-based routing, distance matrix calculation, service area mapping
- **Financial Modeling:** NPV analysis, payback period, multi-scenario sensitivity analysis
- **Data Analytics:** Synthetic data generation, statistical validation, assumption testing
- **Visualization:** Power BI dashboard design, ArcGIS map production

---

## Data Sources & References

### Primary Data Sources
1. **Store Locations:** Apple.com retail store locator (verified February 2026)
2. **Facility Costs:** Statista 2024 - California Industrial Real Estate Report
3. **Depreciation Rates:** SellCell.com 2024 iPhone Depreciation Study
4. **Return Rates:** Consumer Electronics Association 2024 Return Rate Analysis
5. **Refurbishment Costs:** Electronics Repair Industry Benchmark Report 2024

### Academic References
- Drezner, Z. & Hamacher, H. (2002). *Facility Location: Applications and Theory*
- Fleischmann, M. et al. (1997). "Quantitative models for reverse logistics" - *European Journal of Operational Research*
- Guide, V.D.R. & Van Wassenhove, L.N. (2009). "The Evolution of Closed-Loop Supply Chain Research" - *Operations Research*

---

## Business Impact

### Value Proposition
This project demonstrates how operations research techniques solve real-world strategic problems:

**Problem:** $5.8M in lost value annually from inefficient returns handling  
**Solution:** Optimized 2-facility refurbishment network  
**Result:** 670% improvement in value recovery ($22/unit → $168/unit)

### Applicability
The methodology transfers to:
- Any retailer with distributed store network + centralized processing needs
- Multi-echelon distribution network design
- Service facility location (repair centers, fulfillment centers)
- Reverse logistics for any product category (apparel, electronics, appliances)

---

## Author

**Arnav Chudiwale**  
MS Industrial Engineering & Management | Oklahoma State University  
Email: arnav.chudiwale@okstate.edu  
LinkedIn: [linkedin.com/in/arnav-chudiwale](https://linkedin.com/in/arnav-chudiwale)

---

## License

This project is developed for educational and portfolio purposes. Data is synthetic (based on publicly available information). All optimization models and analysis frameworks are original work.

---

*Last Updated: 6th February 2026*

### Recent Updates
- **6th Feb 2026 (Evening):** ✅ Gurobi optimization models completed
  - MODEL #1: Distance minimization → 2-facility solution (Bay Area + LA) with 54.3 mi/unit average distance
  - MODEL #2: Cost minimization → 2-facility solution (LA + Reno) with $1.99M annual cost ($165K savings vs distance model)
  - Comparative analysis: ArcGIS vs Gurobi-Distance vs Gurobi-Cost trade-offs documented
  - Data preprocessing validated: Haversine distance calculations correct, routing factor applied
  - All output files generated and saved to `outputs/` directory

- **6th Feb 2026 (Afternoon):** ArcGIS Network Analyst optimization completed. Los Angeles Metro facility selected to serve all 54 California stores with 28,140 annual returns. Analysis script debugged and validated.
