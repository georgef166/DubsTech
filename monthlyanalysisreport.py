import pandas as pd
import os
import uuid

# Create 'monthlyanalysisreports' directory if it doesn't exist
if not os.path.exists('monthlyanalysisreports'):
    os.makedirs('monthlyanalysisreports')

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
        df.loc[:, 'Metric'] = metric_name
        df.loc[:, 'Rank'] = df['Value'].rank(ascending=False, method='min').astype(int)
        df = df[['Description', 'Metric', 'Value', 'Rank']]
    else:
        # For non-ranked data (e.g., customers, days, hours, regions)
        if 'Description' not in df.columns:
            df = df.reset_index().rename(columns={df.index.name: 'Description'})
        if 'Value' not in df.columns:
            df = df.rename(columns={df.columns[1]: 'Value'})
        df.loc[:, 'Metric'] = metric_name
        df.loc[:, 'Rank'] = df['Value'].rank(ascending=False, method='min').astype(int)
        df = df[['Description', 'Metric', 'Value', 'Rank']]
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df


def generate_monthly_analysis(data_file, selected_year, selected_month, top_n=5):
    '''
    Generates a detailed monthly analysis report for a selected year and month, including:
    - Top/bottom selling products (by quantity & revenue)
    - Top customers
    - Most popular days and times
    - Top regions
    - Actionable revenue suggestions
    - Summary statistics
    '''
    try:
        df = pd.read_csv(data_file, encoding='ISO-8859-1', low_memory=False, dtype={'InvoiceNo': str})
    except FileNotFoundError:
        print(f"Data file {data_file} not found.")
        return None

    df.dropna(subset=['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Country'], inplace=True)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

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

    all_data = []

    # Top/bottom selling products (by quantity)
    top_products_qty = monthly_data.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(top_n)
    all_data.append(save_to_csv(top_products_qty, f'monthlyanalysisreports/top_products_qty_{selected_month}_{selected_year}.csv', 'Quantity Sold'))
    least_products_qty = monthly_data.groupby('Description')['Quantity'].sum().sort_values(ascending=True).head(top_n)
    all_data.append(save_to_csv(least_products_qty, f'monthlyanalysisreports/least_products_qty_{selected_month}_{selected_year}.csv', 'Quantity Sold'))

    # Top/bottom products by revenue
    top_products_revenue = monthly_data.groupby('Description')['Revenue'].sum().sort_values(ascending=False).head(top_n)
    all_data.append(save_to_csv(top_products_revenue, f'monthlyanalysisreports/top_products_revenue_{selected_month}_{selected_year}.csv', 'Revenue'))
    least_products_revenue = monthly_data.groupby('Description')['Revenue'].sum().sort_values(ascending=True).head(top_n)
    all_data.append(save_to_csv(least_products_revenue, f'monthlyanalysisreports/least_products_revenue_{selected_month}_{selected_year}.csv', 'Revenue'))

    # Top customers by revenue
    top_customers = monthly_data.groupby('CustomerID')['Revenue'].sum().sort_values(ascending=False).head(top_n)
    all_data.append(save_to_csv(top_customers, f'monthlyanalysisreports/top_customers_{selected_month}_{selected_year}.csv', 'Revenue', rank_column=False))

    # Most popular days of the week
    popular_days = monthly_data['DayOfWeek'].value_counts()
    all_data.append(save_to_csv(popular_days, f'monthlyanalysisreports/popular_days_{selected_month}_{selected_year}.csv', 'Purchase Count', rank_column=False))

    # Most popular times for purchase (by weekday and hour)
    times_by_day = monthly_data.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Purchase Count')
    times_by_day = times_by_day.sort_values(['DayOfWeek', 'Hour'])
    times_by_day_file = f'monthlyanalysisreports/popular_times_by_day_{selected_month}_{selected_year}.csv'
    times_by_day.to_csv(times_by_day_file, index=False)
    print(f"Data saved to {times_by_day_file}")

    # Regions that earned the most money
    top_regions = monthly_data.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(top_n)
    all_data.append(save_to_csv(top_regions, f'monthlyanalysisreports/top_regions_{selected_month}_{selected_year}.csv', 'Revenue', rank_column=False))

    # Summary statistics
    summary = {
        'Total Orders': monthly_data['InvoiceNo'].nunique(),
        'Total Revenue': monthly_data['Revenue'].sum(),
        'Total Customers': monthly_data['CustomerID'].nunique(),
        'Total Products Sold': monthly_data['Quantity'].sum(),
        'Unique Products': monthly_data['Description'].nunique(),
        'Countries': monthly_data['Country'].nunique(),
    }
    with open(f'monthlyanalysisreports/summary_stats_{selected_month}_{selected_year}.txt', 'w') as f:
        for k, v in summary.items():
            f.write(f"{k}: {v}\n")
    print(f"Summary statistics saved to monthlyanalysisreports/summary_stats_{selected_month}_{selected_year}.txt")

    # Combine all data into single CSV
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_filename = f'monthlyanalysisreports/monthly_analysis_report_{selected_month}_{selected_year}.csv'
    combined_df.to_csv(combined_filename, index=False)
    print(f"Combined monthly analysis report saved to {combined_filename}")

    # Save revenue suggestions (data-driven)
    suggestions = [
        f"Promote top-selling products (e.g., {top_products_qty.index[0]}) with bundles and discounts.",
        f"Target marketing campaigns on high-traffic days (e.g., {popular_days.index[0]}) and peak hours (see {times_by_day_file}).",
        f"Focus advertising efforts on high-revenue regions (e.g., {top_regions.index[0]}).",
        "Implement loyalty programs for top-spending customers to encourage repeat purchases.",
        "Reassess low-performing products: consider discontinuation or creative remarketing strategies.",
        "Consider time-limited offers during less popular hours to boost off-peak sales."
    ]
    with open(f'monthlyanalysisreports/revenue_suggestions_{selected_month}_{selected_year}.txt', 'w') as f:
        f.write("Ways the store can increase revenue:\n")
        for suggestion in suggestions:
            f.write(f"- {suggestion}\n")
    print(f"Revenue suggestions saved to monthlyanalysisreports/revenue_suggestions_{selected_month}_{selected_year}.txt")

    return combined_filename

# Example usage
if __name__ == "__main__":
    # Replace with your actual data file path
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    generate_monthly_analysis(data_file, 2011, 'December', top_n=5)