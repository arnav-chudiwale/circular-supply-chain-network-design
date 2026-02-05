import pandas as pd
import numpy as np

np.random.seed(42)

#Load store locations
stores_df = pd.read_csv('data/store_locations.csv')

print("Adding returns volume data")

#Flagship stores : 8000-12,000 returns per year
#Standard stores: 4000-7000 returns per year 

#Determine store type based on Location
flagship_stores = [
     'Union Square', 'The Grove', 'Stanford Shopping Center',
    'Century City', 'Fashion Valley', 'UTC', 'Irvine Spectrum',
    'Beverly Center', 'Tower Theatre', 'Pasadena', 'Third Street',
    'Fashion Island', 'South Coast Plaza', 'Santana Row'
]

stores_df['Store_Type'] = stores_df['Store_Name'].apply(
    lambda x: "Flagship" if any(fs in x for fs in flagship_stores) else "Standard"
)

#Annual sales per store
stores_df["Annual_Sales"] = np.where(
    stores_df["Store_Type"] == "Flagship",
    np.random.randint(8500, 12001, len(stores_df)),
    np.random.randint(4500, 7001, len(stores_df))
)

#Industry return rate for premium phones - 7-8%
#Source - Consumer electronics return rates 2024

stores_df["Return_Rate"] = np.random.uniform(0.07, 0.08, len(stores_df))

stores_df['Annual_Returns'] =(
    stores_df['Annual_Sales'] * stores_df['Return_Rate']
).astype(int)

#Summary Statistics
total_sales = stores_df["Annual_Sales"].sum()
total_returns = stores_df["Annual_Returns"].sum()
avg_return_rate = stores_df["Return_Rate"].mean()

print(f"\n Returns Volume:")
print(f" Total Annual Sales across stores: {total_sales} units")
print(f" Total Annual Returns: {total_returns} units")
print(f" Average Return Rate: {avg_return_rate:.2%}")
print(f" Flagship Stores: {(stores_df['Store_Type']=='Flagship').sum()}")
print(f" Standard Stores: {(stores_df['Store_Type']=='Standard').sum()}")

stores_df.to_csv('data/stores_with_returns.csv', index=False)
print("\n Saved to data/stores_with_returns.csv")
