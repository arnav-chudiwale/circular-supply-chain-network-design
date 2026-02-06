import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

print("="*70)
print("DIAGNOSING FACILITY LOCATION ISSUE")
print("="*70)

# Read original facilities
original = pd.read_csv('data/candidate_facilities.csv')
print("\nORIGINAL CANDIDATE FACILITIES:")
print(original[['Facility_ID', 'Name', 'City', 'Latitude', 'Longitude']])

# Calculate distances between all facilities (in decimal degrees, approximate)
coords = original[['Latitude', 'Longitude']].values
distances = cdist(coords, coords, metric='euclidean')

print("\n" + "="*70)
print("DISTANCE MATRIX (Decimal Degrees - rough approximation)")
print("="*70)
print("Facilities:", original['Facility_ID'].tolist())
print()

for i, fac_id in enumerate(original['Facility_ID']):
    print(f"{fac_id}: ", end="")
    for j in range(len(original)):
        if i == j:
            print("  --   ", end="")
        else:
            # Convert to approximate miles (1 degree ≈ 69 miles)
            miles = distances[i,j] * 69
            print(f"{miles:6.1f} ", end="")
    print()

# Check for facilities that are too close
print("\n" + "="*70)
print("CLUSTERING ANALYSIS")
print("="*70)

min_distance_miles = 50  # Facilities should be at least 50 miles apart
problems = []

for i in range(len(original)):
    for j in range(i+1, len(original)):
        miles = distances[i,j] * 69
        if miles < min_distance_miles:
            problems.append({
                'Facility_1': original.iloc[i]['Name'],
                'Facility_2': original.iloc[j]['Name'],
                'Distance_Miles': round(miles, 1)
            })

if problems:
    print(f"\n⚠️ FOUND {len(problems)} FACILITY PAIRS TOO CLOSE:")
    for p in problems:
        print(f"  {p['Facility_1']} ↔ {p['Facility_2']}: {p['Distance_Miles']} miles")
    print("\n→ This might cause ArcGIS to see them as redundant!")
else:
    print("✓ All facilities are adequately separated (>50 miles)")

# Check geographic diversity
print("\n" + "="*70)
print("GEOGRAPHIC SPREAD")
print("="*70)
print(f"Latitude range: {original['Latitude'].min():.2f}° to {original['Latitude'].max():.2f}°")
print(f"Longitude range: {original['Longitude'].min():.2f}° to {original['Longitude'].max():.2f}°")
print(f"North-South span: ~{(original['Latitude'].max() - original['Latitude'].min()) * 69:.0f} miles")
print(f"East-West span: ~{(original['Longitude'].max() - original['Longitude'].min()) * 54:.0f} miles")

lat_range = original['Latitude'].max() - original['Latitude'].min()
lon_range = original['Longitude'].max() - original['Longitude'].min()

if lat_range < 2.0 or lon_range < 2.0:
    print("\n⚠️ WARNING: Facilities are geographically clustered!")
    print("Consider adding more dispersed locations (Central Valley, far north, etc.)")