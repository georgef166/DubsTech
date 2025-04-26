import pandas as pd
import os
import uuid

# Create 'reports' directory if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')

def save_to_csv(df, filename, metric_name, rank_column=True):
    '''Helper function to save a dataframe to a CSV file with specific format'''
    # Convert Series to DataFrame if necessary
    if isinstance(df, pd.Series):
        df = df.to_frame().reset_index()
        # Rename columns appropriately
        df.columns = ['Description', 'Value'] if len(df.columns) == 2 else df.columns
    
    # If rank_column is True, ensure proper column structure
    if rank_column:
        # Ensure 'Description' and 'Value' columns exist
        if 'Description' not in df.columns or 'Value' not in df.columns:
            df = df.rename(columns={df.columns[0]: 'Description', df.columns[1]: 'Value'})
        df['Metric'] = metric_name
        df['Rank'] = df['Value'].rank(ascending=False, method='min').astype(int)
        df = df[['Description', 'Metric', 'Value', 'Rank']]
    else:
        # For non-ranked data (e.g., customers, days, hours, regions)
        if 'Description' not in df.columns:
            df = df.reset_index().rename(columns={df.index.name: 'Description'})
        if 'Value' not in df.columns:
            df = df.rename(columns={df.columns[1]: 'Value'})
        df['Metric'] = metric_name
        df['Rank'] = df['Value'].rank(ascending=False, method='min').astype(int)
        df = df[['Description', 'Metric', 'Value', 'Rank']]
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df

def generate_monthly_analysis(data_file, selected_year, selected_month):
    '''Generates monthly analysis report and saves to CSV for a selected year and month'''
    # Load and clean data
    try:
        df = pd.read_csv(data_file, encoding='ISO-8859-1', low_memory=False, dtype={'InvoiceNo': str})
    except FileNotFoundError:
        print(f"Data file {data_file} not found.")
        return None
    
    df.dropna(subset=['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Country'], inplace=True)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # Create new columns
    try:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    except Exception as e:
        print(f"Error parsing InvoiceDate: {e}")
        return None
    
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.month_name()
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df['InvoiceDate'].dt.hour
    
    # Filter for selected month and year
    monthly_data = df[(df['Year'] == selected_year) & (df['Month'] == selected_month)]
    
    if monthly_data.empty:
        print(f"No data available for {selected_month}/{selected_year}")
        return None
    
    # Initialize list to store all dataframes for final CSV
    all_data = []
    
    # Products that sold the most (by quantity)
    top_products_qty = monthly_data.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(5)
    all_data.append(save_to_csv(top_products_qty, f'reports/top_products_qty_{selected_month}_{selected_year}.csv', 
                               'Quantity Sold'))
    
    # Products that sold the least (by quantity)
    least_products_qty = monthly_data.groupby('Description')['Quantity'].sum().sort_values(ascending=True).head(5)
    all_data.append(save_to_csv(least_products_qty, f'reports/least_products_qty_{selected_month}_{selected_year}.csv', 
                               'Quantity Sold'))
    
    # Products that generated the most revenue
    top_products_revenue = monthly_data.groupby('Description')['Revenue'].sum().sort_values(ascending=False).head(5)
    all_data.append(save_to_csv(top_products_revenue, f'reports/top_products_revenue_{selected_month}_{selected_year}.csv', 
                               'Revenue'))
    
    # Products that generated the least revenue
    least_products_revenue = monthly_data.groupby('Description')['Revenue'].sum().sort_values(ascending=True).head(5)
    all_data.append(save_to_csv(least_products_revenue, f'reports/least_products_revenue_{selected_month}_{selected_year}.csv', 
                               'Revenue'))
    
    # Customers who bought the most (by revenue)
    top_customers = monthly_data.groupby('CustomerID')['Revenue'].sum().sort_values(ascending=False).head(5)
    all_data.append(save_to_csv(top_customers, f'reports/top_customers_{selected_month}_{selected_year}.csv', 
                               'Revenue', rank_column=False))
    
    # Most popular days of the week
    popular_days = monthly_data['DayOfWeek'].value_counts()
    all_data.append(save_to_csv(popular_days, f'reports/popular_days_{selected_month}_{selected_year}.csv', 
                               'Purchase Count', rank_column=False))
    
    # Most popular times for purchase
    popular_hours = monthly_data['Hour'].value_counts().sort_index()
    all_data.append(save_to_csv(popular_hours, f'reports/popular_hours_{selected_month}_{selected_year}.csv', 
                               'Purchase Count', rank_column=False))
    
    # Regions that earned the most money
    top_regions = monthly_data.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(5)
    all_data.append(save_to_csv(top_regions, f'reports/top_regions_{selected_month}_{selected_year}.csv', 
                               'Revenue', rank_column=False))
    
    # Combine all data into single CSV
    combined_df = pd.concat(all_data, ignore_index=True)
    artifact_id = str(uuid.uuid4())
    combined_filename = f'reports/monthly_analysis_report_{selected_month}_{selected_year}.csv'
    combined_df.to_csv(combined_filename, index=False)
    print(f"Combined monthly analysis report saved to {combined_filename}")
    
    # Save revenue suggestions
    suggestions = [
        f"Promote top-selling products with bundles and discounts to boost sales further.",
        f"Target marketing campaigns on high-traffic days (e.g., {popular_days.index[0]}) and peak hours (e.g., {popular_hours.index[0]}:00).",
        f"Focus advertising efforts on high-revenue regions (e.g., {top_regions.index[0]} and {top_regions.index[1]}).",
        "Implement loyalty programs for top-spending customers to encourage repeat purchases.",
        "Reassess low-performing products: consider discontinuation or creative remarketing strategies."
    ]
    with open(f'reports/revenue_suggestions_{selected_month}_{selected_year}.txt', 'w') as f:
        f.write("Ways the store can increase revenue:\n")
        for suggestion in suggestions:
            f.write(f"- {suggestion}\n")
    print(f"Revenue suggestions saved to reports/revenue_suggestions_{selected_month}_{selected_year}.txt")
    
    return combined_filename

# Example usage
if __name__ == "__main__":
    # Replace with your actual data file path
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    generate_monthly_analysis(data_file, 2011, 'December')