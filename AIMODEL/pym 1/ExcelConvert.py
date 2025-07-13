import pandas as pd

# Read the Excel file
df = pd.read_excel("DATA_FINAL.xlsx")
print(df.columns.tolist())

# Combine city and state into a single identifier (optional)
df['City_State'] = df['CITY'] + ", " + df['STATE']

# Group by city and state (or the combined column) and aggregate other columns
grouped_df = df.groupby(['CITY', 'STATE'], as_index=False).agg({
    'TOURIST SPOT': lambda x: ', '.join(x.dropna().unique()),  # Combine unique values
    'TYPE OF ATTRACTION': lambda x: ', '.join(x.dropna().unique()),
    'SEASON': lambda x: ', '.join(x.dropna().unique()),
    'ACTIVITIES': lambda x: ', '.join(x.dropna().unique())
})

# Save the output to a new Excel file
grouped_df.to_excel("transformed_excel.xlsx", index=False)

print("Excel transformation complete!")
