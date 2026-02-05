import pandas as pd 

print("CALCULATING CURRENT STATE BASELINE")

stores_df = pd.read_csv('data/stores_complete.csv')
params_df = pd.read_csv('data/cost_parameters.csv')

bulk_payout = params_df['bulk_recycler_payout_per_unit'].iloc[0]
total_returns = stores_df['Annual_Returns'].sum()

current_recovery = total_returns * bulk_payout

print(f" \n Current State (Bulk Recycling Model): ")
print(f" Total Annual Returns: {total_returns:,} units")
print(f" Bulk Recycler Payout: ${bulk_payout} per unit")
print(f" Annul Recovery Value: ${current_recovery:,.2f}")
print(f" Landfill diversion: ~35% (industry average)")
print(f" Cycle time: 60+ days (warehouse consolidation + transport)")

baseline_df = pd.DataFrame([{
    'total_returns': total_returns,
    'bulk_payout_per_unit': bulk_payout,
    'annual_recovery': current_recovery,
    'recovery_per_unit': bulk_payout,
    'landfill_diversion_pct': 0.35,
    'avg_cycle_time_days': 60
}])

baseline_df.to_csv('data/current_state_baseline.csv', index = False)
print("\n Baseline metrics saved to data/current_state_baseline.csv")

