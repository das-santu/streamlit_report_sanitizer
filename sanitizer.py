from openpyxl.utils import get_column_letter
from openpyxl.styles import Border, Side
from openpyxl import Workbook
import pandas as pd
import re
import os


# Define a function to clean and sanitize data
def sanitize_excel(file_path):

    # Read the raw data
    df = pd.read_excel(file_path, header=None)

    # Drop rows that are completely empty or contain NaN
    df_cleaned = df.dropna(how='all')

    # Find the index of the row matching "SUPPLIER NAME"
    match_index = df_cleaned[df_cleaned.iloc[:, 0].str.contains(r"SUPPLIER NAME.*$", na=False)].index
    if not match_index.empty:
        # Trim the DataFrame to include only rows before the match
        df_cleaned = df_cleaned.loc[:match_index[0]-1]

    # breakpoint()

    # Remove rows with unwanted patterns (e.g., headers, footers, markers)
    unwanted_patterns = r"BARIK MEDICAL|SABANG.*$|Phone.*$|GSTIN.*$|STOCK & SALES.*$|ITEM DESCRIPTION|QTY.|TOTAL|Page No.*$|Continue|[-]{5,}"  # Add more patterns if needed
    df_cleaned = df_cleaned[~df_cleaned.iloc[:, 0].str.contains(unwanted_patterns, na=False)]

    # Strip leading/trailing whitespace
    df_cleaned.iloc[:, 0] = df_cleaned.iloc[:, 0].str.strip()

    # Remove rows that are now empty after cleaning
    df_cleaned = df_cleaned[df_cleaned.iloc[:, 0] != ""]

    # Split rows into multiple columns dynamically
    split_rows = []
    regex_pattern = r"(\d\*\S+$|\d*ML$)"  # Regex to match the specific condition

    for row in df_cleaned[0]:
        split_data = re.split(r'\s{2,}', row)  # Split on two or more spaces
        extra_columns = len(split_data) - 11  # Calculate extra columns if any

        if extra_columns > 0:
            # Concatenate Column1 with the next (extra_columns + 1) columns
            concat_columns = " ".join(split_data[:extra_columns + 1])
            remaining_columns = split_data[extra_columns + 1:9]  # Columns 4 through 9
            last_two = split_data[-2:]  # Last two columns
            normalized_row = [concat_columns] + remaining_columns + last_two
        else:
            normalized_row = split_data  # If exactly 11 columns

        if len(split_data) == 10:
            if " " in split_data[9]:  # If fewer than 11 columns
                split_col10 = split_data[9].split(" ")
                normalized_row = split_data[:9] + split_col10
            elif re.search(regex_pattern, split_data[0]):
                match = re.search(regex_pattern, split_data[0])
                match_value = match.group(0)  # Extract the matched value
                split_data.insert(1, match_value)  # Insert the matched value as a new column
                split_data[0] = split_data[0].replace(match_value, "").strip()  # Remove the matched value from Column1
            elif "." in split_data[2]:
                split_data.insert(1, "")  # Insert the matched value as a new column

        split_rows.append(normalized_row)

    # Create a new DataFrame with the normalized data
    df_normalized = pd.DataFrame(split_rows)

    # Add a placeholder for the new column (before Column3)
    df_normalized.insert(2, "Company Name", "")  # Add the new column

    # Initialize variables for processing company names
    company_name = None

    # Process each row to handle single-column rows as company names
    for index, row in df_normalized.iterrows():
        non_empty_columns = row[row != ""].count()  # Count non-empty columns
        if non_empty_columns == 1:  # Single-column row
            company_name = row[0]  # Update the company name
            df_normalized.drop(index, inplace=True)  # Remove this row
        elif non_empty_columns == 2:  # Single-column row
            company_name = " ".join(row[:2])  # Update the company name
            df_normalized.drop(index, inplace=True)  # Remove this row
        elif non_empty_columns == 3:  # Single-column row
            company_name = " ".join(row[:3])  # Update the company name
            df_normalized.drop(index, inplace=True)  # Remove this row
        elif company_name:  # Assign the company name to the "Company Name" column
            df_normalized.at[index, "Company Name"] = company_name

    # Reset the index and return the cleaned DataFrame
    df_normalized.reset_index(drop=True, inplace=True)

    # Use the updated function to save the DataFrame
    check_create_dir("sanitized")
    output_file = "sanitized/sanitized_report.xlsx"
    save_with_auto_fit(df_normalized, output_file)

    return output_file


# Save the cleaned data to a new Excel file with auto-fit columns
def save_with_auto_fit(df, output_file):

    # Define your custom header
    custom_header = ["ITEM DESCRIPTION", "QUANTITY", "COMPANY NAME", "OPENING QTY", "OPENING VALUE", "RECEIPT QTY", "RECEIPT VALUE", "ISSUE QTY", "ISSUE VALUE", "CLOSING QTY", "CLOSING VALUE", "DUMP QTY"]  # Adjust as per your data
    df.columns = custom_header[:df.shape[1]]  # Match header length to number of columns

    with pd.ExcelWriter(output_file, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, index=False, header=True, sheet_name="Sanitized_Data")
        workbook = writer.book
        worksheet = writer.sheets["Sanitized_Data"]

        # Define a thin border style
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # Auto-fit columns and apply borders
        for col_num, column_cells in enumerate(worksheet.columns, start=1):
            max_length = 0
            column_letter = get_column_letter(col_num)
            for cell in column_cells:
                try:
                    # Apply the border to the cell
                    cell.border = thin_border
                    # Get the length of the cell value
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            # Set the column width slightly larger than the max length
            worksheet.column_dimensions[column_letter].width = max_length + 2

    print(f"Sanitized report saved to {output_file}")


def check_create_dir(dir_name):
    if os.listdir(dir_name):
        files = [f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))]
        for file in files:
            file_path = os.path.join(dir_name, file)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    elif not os.path.exists(dir_name):
        os.mkdir(dir_name)