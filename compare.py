file2 = "/Users/elnoelakwa/Downloads/ReportViewers_export_20250430.csv"
file1=  "/Users/elnoelakwa/Downloads/ReportViewers_0303.csv"

import pandas as pd
import re

# look for distinct valukes in 1 and 2nd columns in both files
# print the values not in both files in a list

def get_distinct_values(file1, file2):
    # Read the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Get distinct values from the first two columns of each file
    distinct_values_file1 = set(df1.iloc[:, 1].unique())
    distinct_values_file2 = set(df2.iloc[:, 1].unique())

    # Find values that are in file1 but not in file2
    not_in_file2 = distinct_values_file1 - distinct_values_file2

    # Find values that are in file2 but not in file1
    not_in_file1 = distinct_values_file2 - distinct_values_file1

    return not_in_file2, not_in_file1

not_in_file2, not_in_file1 = get_distinct_values(file1, file2)

# main
if __name__ == "__main__":
    print("Values in file1 but not in file2:")
    for value in not_in_file2:
        print(value)

