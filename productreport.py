import os
import pandas as pd
import sys

def product_report(data_file, product_name):
    # Create output directory
    output_dir = 'productreports'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load and clean data
    df = pd.read_csv(data_file, encoding='ISO-8859-1', low_memory=False)
    df.dropna(subset=['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Country'], inplace=True)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df['Month'] = df['InvoiceDate'].dt.month_name()
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df['InvoiceDate'].dt.hour
    df['Revenue'] = df['Quantity'] * df['UnitPrice']

    # Filter for the specific product
    product_data = df[df['Description'].str.lower() == product_name.lower()]
    if product_data.empty:
        print(f"No sales data found for product: {product_name}")
        return

    # 1. Quantity Sold by Country
    qty_by_country = product_data.groupby('Country')['Quantity'].sum().reset_index()
    qty_by_country.to_csv(os.path.join(output_dir, f'{product_name}_qty_by_country.csv'), index=False)

    # 2. Quantity Sold by Month
    qty_by_month = product_data.groupby('Month')['Quantity'].sum().reindex(
        [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]).dropna().reset_index()
    qty_by_month.to_csv(os.path.join(output_dir, f'{product_name}_qty_by_month.csv'), index=False)

    # 3. Quantity Sold by Time of Day
    qty_by_hour = product_data.groupby('Hour')['Quantity'].sum().reset_index()
    qty_by_hour.to_csv(os.path.join(output_dir, f'{product_name}_qty_by_hour.csv'), index=False)

    # 4. Quantity Sold by Day of Week
    qty_by_dayofweek = product_data.groupby('DayOfWeek')['Quantity'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ).dropna().reset_index()
    qty_by_dayofweek.to_csv(os.path.join(output_dir, f'{product_name}_qty_by_dayofweek.csv'), index=False)

    # 5. Total Quantity Sold
    total_qty = product_data['Quantity'].sum()
    # 6. Total Revenue Generated
    total_revenue = product_data['Revenue'].sum()
    # Save summary
    with open(os.path.join(output_dir, f'{product_name}_summary.txt'), 'w') as f:
        f.write(f"Product: {product_name}\n")
        f.write(f"Total Quantity Sold: {total_qty}\n")
        f.write(f"Total Revenue Generated: {total_revenue:.2f}\n")
    print(f"Product report for '{product_name}' saved in {output_dir}/")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 productreport.py <product_name>")
        sys.exit(1)
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    product_name = sys.argv[1]
    product_report(data_file, product_name)
