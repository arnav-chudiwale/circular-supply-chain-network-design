import pandas as pd 

print("PREPARING SUPPLY POINTS FILE FOR ARCGIS")

#reads stores
stores_df = pd.read_csv('data/stores_complete.csv')

# Creating arcgis formatted supply points
#"weight" field = supply volume from the stores to the facilities(ArcGIS uses this for optimization)

arcgis_supply = pd.DataFrame({
    'StoreID': stores_df['Store_ID'],
    'Store_Name': stores_df["Store_Name"],
    "City": stores_df["City"],
    'Y': stores_df["Lat"],
    "X": stores_df["Lon"],
    "Weight": stores_df["Annual_Returns"],
    "GroupName": "All" #ArcGIS parameter (we're not segmenting)
})

arcgis_supply.to_csv("data/arcgis_supply_points.csv", index = False)

print("\n Created ARCGIS-ready supply points file")
print(f" {len(arcgis_supply)} supply points (stores) to refurb facilities")
print(f" Total weight (supply volume from all stores: {arcgis_supply['Weight'].sum():,} units annually")
print("\n Top 5 stores by supply volume:")
print(arcgis_supply.nlargest(5, 'Weight')[['StoreID', 'Store_Name', 'Weight']])

print("\n Saved to data/arcgis_supply_points.csv")