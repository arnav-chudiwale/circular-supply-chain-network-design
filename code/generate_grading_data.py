import pandas as pd
import numpy as np

np.random.seed(42)

stores_df = pd.read_csv('data/stores_with_returns.csv')

print("Generating product grade distribution")

GRADE_DISTRIBUTION = {
    "Grade_A": 0.25, #Like New 
    "Grade_B": 0.45, # refurbishable
    "Grade_C": 0.30 #Recyclable
}

stores_df['Grade_A_Units'] = (stores_df['Annual_Returns'] * GRADE_DISTRIBUTION['Grade_A']).astype(int)
stores_df['Grade_B_Units'] = (stores_df['Annual_Returns'] * GRADE_DISTRIBUTION['Grade_B']).astype(int)
stores_df['Grade_C_Units'] = (stores_df['Annual_Returns'] * GRADE_DISTRIBUTION['Grade_C']).astype(int)

total = stores_df["Annual_Returns"].sum()
a = stores_df["Grade_A_Units"].sum()
b = stores_df["Grade_B_Units"].sum()
c = stores_df["Grade_C_Units"].sum()

print("\n Product Grade Distribution Summary:")
print(f" Total Returned Units: {total:,} ")
print(f" Grade A Units (Like New): {a:,} ({a/total:.1%})")
print(f" Grade B Units (Refurbishable): {b:,} ({b/total:.1%})")
print(f" Grade C Units (Recyclable): {c:,} ({c/total:.1%})")

stores_df.to_csv('data/stores_complete.csv', index =False)
print("\n Saved to data/stores_complete.csv")