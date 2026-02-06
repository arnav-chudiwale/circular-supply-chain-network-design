import pandas as pd

print("="*70)
print("DEEP DIAGNOSTIC: WHY ARCGIS IS CHOOSING ONLY 1 FACILITY")
print("="*70)

# Load data
stores = pd.read_csv('data/stores_complete.csv')
facilities = pd.read_csv('data/candidate_facilities.csv')

total_demand = stores['Annual_Returns'].sum()
print(f"\n📊 DEMAND ANALYSIS:")
print(f"  Total demand: {total_demand:,} units/year")
print(f"  Number of stores: {len(stores)}")
print(f"  Average per store: {total_demand/len(stores):,.0f} units")

print(f"\n🏭 FACILITY CAPACITY ANALYSIS:")
print("-" * 70)
for _, fac in facilities.iterrows():
    capacity = fac['Capacity_Units_Annual']
    pct_of_demand = (capacity / total_demand) * 100
    print(f"{fac['Facility_ID']}: {fac['Name']}")
    print(f"  Capacity: {capacity:,} units/year ({pct_of_demand:.1f}% of total demand)")
    
max_capacity = facilities['Capacity_Units_Annual'].max()
total_capacity = facilities['Capacity_Units_Annual'].sum()

print(f"\n🎯 CAPACITY CONSTRAINT ANALYSIS:")
print(f"  Largest single facility: {max_capacity:,} units")
print(f"  Total demand: {total_demand:,} units")
print(f"  Total available capacity: {total_capacity:,} units")

if max_capacity >= total_demand:
    print(f"\n⚠️ PROBLEM FOUND!")
    print(f"  Single facility CAN handle all demand!")
    print(f"  Largest facility: {max_capacity:,} >= Total demand: {total_demand:,}")
    print(f"  Excess capacity: {max_capacity - total_demand:,} units")
    print(f"\n  → ArcGIS sees no need to open multiple facilities!")
    print(f"  → Distance doesn't improve by opening more facilities")
    print(f"\n  SOLUTION: Reduce facility capacities to force multiple sites")
    
    # Calculate required capacity
    recommended_capacity = int(total_demand / 3)  # Force at least 3 facilities
    print(f"\n💡 RECOMMENDED FIX:")
    print(f"  Set max capacity per facility: {recommended_capacity:,} units")
    print(f"  This forces opening 3+ facilities to meet demand")
    
elif total_capacity < total_demand:
    print(f"\n⚠️ INFEASIBLE PROBLEM!")
    print(f"  Total capacity: {total_capacity:,} < Total demand: {total_demand:,}")
    print(f"  Shortage: {total_demand - total_capacity:,} units")
    print(f"\n  SOLUTION: Increase facility capacities")
    
else:
    print(f"\n✓ Capacity constraints look reasonable")
    print(f"  Need to investigate other issues...")

# Check geographic distribution
print(f"\n🗺️ GEOGRAPHIC DISTRIBUTION CHECK:")
stores_by_city = stores.groupby('City')['Annual_Returns'].agg(['count', 'sum'])
stores_by_city = stores_by_city.sort_values('sum', ascending=False)

print("\nTop 5 cities by demand:")
for city, row in stores_by_city.head(5).iterrows():
    print(f"  {city}: {row['count']} stores, {row['sum']:,} units/year")

# Check if demand is highly concentrated
top5_demand = stores_by_city.head(5)['sum'].sum()
concentration = (top5_demand / total_demand) * 100
print(f"\nDemand concentration: {concentration:.1f}% in top 5 cities")

if concentration > 80:
    print("  → Demand is highly concentrated")
    print("  → One central facility might serve most stores efficiently")
    print("  → This could explain why ArcGIS chooses only 1 facility")

print("\n" + "="*70)
