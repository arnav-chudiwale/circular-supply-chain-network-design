import pandas as pd 

print(f" PREPARING FACILITIES FILES FOR ARCGIS")

#read base facilities
facilities_df = pd.read_csv("data/candidate_facilities.csv")

# Add fields that ArcGIS Network Analyst expects
facilities_df['FacilityType'] = 'Candidate' #ArcGIS will change it to 'Chosen' when selected
facilities_df['Capacity'] = facilities_df['Capacity_Units_Annual']
facilities_df['Name'] = facilities_df["Name"]
facilities_df["X"] = facilities_df["Longitude"] 
facilities_df["Y"] = facilities_df["Latitude"]

# X = Longitude, Y = Latitude in ArcGIS

# Creating clean version for ArcGIS
arcgis_facilities = facilities_df[[
    'Facility_ID',
    'Name',
    'City',
    'Y', # Latitude (ArcGIS expects Y before X)
    'X', #Longitude
    'Capacity', 
    'Annual_Fixed_Cost',
    'FacilityType'
]]

arcgis_facilities.to_csv("data/arcgis_facilities.csv", index=False)

print("\n Created ARCGIS ready facilities file")
print(f" {len(arcgis_facilities)} candidate facilities")
print("\n Facility List:")
print(arcgis_facilities[["Facility_ID", "Name", "Capacity", "Annual_Fixed_Cost"]])

print("\n Saved to data/arcgis_facilities.csv")
