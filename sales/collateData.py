import pandas as pd

# Read the first CSV file into a DataFrame
df1 = pd.read_csv('../hubspot_closedDeals2022.csv')

# Read the second CSV file into another DataFrame
df2 = pd.read_csv('data.csv')

# Get the number of rows in both DataFrames
num_rows_df1 = len(df1)
num_rows_df2 = len(df2)

# Check if both DataFrames have the same number of rows
if num_rows_df1 != num_rows_df2:
    raise ValueError("Both DataFrames should have the same number of rows.")

# Append each column in df2 to the end of its corresponding row index in df1 + 1
for col_name in df2.columns:
    df1[col_name] = df2[col_name].values

# Save the updated DataFrame to a new CSV file
print(df1.head)