import pandas as pd

print("="*70)
print("DEFINING CANDIDATE REFURBISHMENT CENTER LOCATIONS")
print("="*70)

# Strategic locations based on store density + cost analysis
candidate_facilities = [
    {
        'Facility_ID': 'FC01',
        'Name': 'San Francisco Bay Area',
        'City': 'Fremont',
        'Latitude': 37.5485,
        'Longitude': -121.9886,
        'Capacity_Units_Annual': 25000,
        'Annual_Fixed_Cost': 1050000,  # Highest CA costs
        'Notes': 'Central to 17 Bay Area stores, high labor costs'
    },
    {
        'Facility_ID': 'FC02',
        'Name': 'Los Angeles Metro',
        'City': 'Ontario',
        'Latitude': 34.0633,
        'Longitude': -117.6509,
        'Capacity_Units_Annual': 25000,
        'Annual_Fixed_Cost': 980000,
        'Notes': 'Serves 18 LA stores + Orange County'
    },
    {
        'Facility_ID': 'FC03',
        'Name': 'San Diego',
        'City': 'San Diego',
        'Latitude': 32.8312,
        'Longitude': -117.1225,
        'Capacity_Units_Annual': 20000,
        'Annual_Fixed_Cost': 920000,
        'Notes': 'Serves 5 San Diego stores'
    },
    {
        'Facility_ID': 'FC04',
        'Name': 'Central Valley',
        'City': 'Fresno',
        'Latitude': 36.7783,
        'Longitude': -119.4179,
        'Capacity_Units_Annual': 20000,
        'Annual_Fixed_Cost': 820000,  # Lower inland costs
        'Notes': 'Lower costs, central location'
    },
    {
        'Facility_ID': 'FC05',
        'Name': 'Reno, NV (Out-of-State)',
        'City': 'Reno',
        'Latitude': 39.5296,
        'Longitude': -119.8138,
        'Capacity_Units_Annual': 25000,
        'Annual_Fixed_Cost': 720000,  # Lowest (no CA taxes)
        'Notes': 'Comparison: 31% lower cost than Bay Area'
    }
]

facilities_df = pd.DataFrame(candidate_facilities)

print(f"\n✓ Defined {len(facilities_df)} candidate facilities:")
print("-" * 70)
for _, row in facilities_df.iterrows():
    print(f"  {row['Facility_ID']}: {row['Name']}")
    print(f"    Annual cost: ${row['Annual_Fixed_Cost']:,}")
    print(f"    Capacity: {row['Capacity_Units_Annual']:,} units/year")
    print(f"    {row['Notes']}")
    print()

facilities_df.to_csv('data/candidate_facilities.csv', index=False)
print("✓ Saved to: data/candidate_facilities.csv")