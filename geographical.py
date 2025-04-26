import pandas as pd
import os
from monthlyanalysisreport import save_to_csv

def geographical_analysis(data_file):
    # Load data
    try:
        df = pd.read_csv(data_file, encoding='ISO-8859-1', low_memory=False, dtype={'InvoiceNo': str})
    except FileNotFoundError:
        print(f"Data file {data_file} not found.")
        return None

    # Data cleaning: drop missing and filter positive sales
    df.dropna(subset=['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Country'], inplace=True)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Calculate sales value per row
    df['Sales'] = df['Quantity'] * df['UnitPrice']

    # Aggregate sales by country
    country_sales = df.groupby('Country')['Sales'].sum().sort_values(ascending=False)
    country_sales_df = country_sales.reset_index().rename(columns={'Country': 'Description', 'Sales': 'Value'})

    # Prepare output folder
    output_folder = 'geographical'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Top-performing regions (top 10)
    top_regions_df = country_sales_df.head(10)
    top_file = os.path.join(output_folder, 'top_performing_regions.csv')
    save_to_csv(top_regions_df, top_file, metric_name='Total Sales by Country', rank_column=True)

    # Potential areas for expansion (bottom 10)
    expansion_df = country_sales_df.tail(10)
    expansion_file = os.path.join(output_folder, 'potential_expansion_areas.csv')
    save_to_csv(expansion_df, expansion_file, metric_name='Total Sales by Country', rank_column=True)

    print("Top-performing regions:")
    print(top_regions_df)
    print("\nPotential areas for expansion (lower sales):")
    print(expansion_df)

if __name__ == "__main__":
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    geographical_analysis(data_file)
