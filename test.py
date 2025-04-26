import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# ------------------------
# Data Loading and Cleaning
# ------------------------

def load_data(filepath):
    df = pd.read_csv(filepath, encoding='ISO-8859-1', dtype={'InvoiceNo': str})
    df.dropna(subset=['CustomerID'], inplace=True)
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    return df

# ------------------------
# Monthly Data Extraction
# ------------------------

def filter_month(df, year, month):
    return df[(df['InvoiceDate'].dt.year == year) & (df['InvoiceDate'].dt.month == month)]

# ------------------------
# Report Generation Functions
# ------------------------

def top_bottom_products(df):
    product_sales = df.groupby('Description').agg({'Quantity':'sum', 'TotalPrice':'sum'}).sort_values('Quantity', ascending=False)
    top_products = product_sales.head(5)
    bottom_products = product_sales[product_sales['Quantity'] > 0].tail(5)
    top_revenue = product_sales.sort_values('TotalPrice', ascending=False).head(5)
    bottom_revenue = product_sales[product_sales['TotalPrice'] > 0].sort_values('TotalPrice').head(5)
    return top_products, bottom_products, top_revenue, bottom_revenue

def top_customers(df):
    return df.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).head(5)

def popular_days(df):
    return df['InvoiceDate'].dt.day_name().value_counts()

def popular_hours(df):
    return df['InvoiceDate'].dt.hour.value_counts().sort_index()

def top_regions(df):
    return df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)

def generate_suggestions():
    suggestions = [
        "- Promote top-selling products with bundles and discounts.",
        "- Target marketing efforts on peak purchase days and times.",
        "- Focus on high-revenue regions for personalized advertising.",
        "- Offer loyalty rewards to top customers to boost repeat sales.",
        "- Improve or re-market poorly performing products creatively."
    ]
    return suggestions

# ------------------------
# Visualization Functions (with Saving)
# ------------------------

def save_and_show_plot(fig, filename, year, month):
    output_dir = 'plots'
    os.makedirs(output_dir, exist_ok=True)
    full_filename = f"{filename}_{year}_{str(month).zfill(2)}.png"
    filepath = os.path.join(output_dir, full_filename)
    fig.savefig(filepath, bbox_inches='tight')
    plt.show()

def plot_purchase_times(hours, year, month):
    fig = plt.figure(figsize=(12,6))
    sns.barplot(x=hours.index, y=hours.values, hue=hours.index, palette='viridis', legend=False)
    plt.title('Popular Purchase Times (Hour of Day)')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Purchases')
    plt.xticks(range(24))
    save_and_show_plot(fig, 'purchase_times', year, month)

def plot_weekday_sales(days, year, month):
    fig = plt.figure(figsize=(12,6))
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sales = days.reindex(days_order)
    sns.barplot(x=sales.index, y=sales.values, hue=sales.index, palette='coolwarm', legend=False)
    plt.title('Purchases by Day of Week')
    plt.xlabel('Day of Week')
    plt.ylabel('Number of Purchases')
    save_and_show_plot(fig, 'weekday_sales', year, month)

def plot_monthly_sales(df, year, month):
    monthly_sales = df.groupby(df['InvoiceDate'].dt.month)['TotalPrice'].sum()
    months_order = range(1, 13)
    fig = plt.figure(figsize=(12,6))
    sns.barplot(x=list(months_order), y=[monthly_sales.get(i, 0) for i in months_order], hue=list(months_order), palette='mako', legend=False)
    plt.title('Monthly Sales')
    plt.xlabel('Month')
    plt.ylabel('Total Revenue')
    save_and_show_plot(fig, 'monthly_sales', year, month)

def plot_top_regions(regions, year, month):
    fig = plt.figure(figsize=(12,6))
    sns.barplot(x=regions.head(10).index, y=regions.head(10).values, hue=regions.head(10).index, palette='crest', legend=False)
    plt.title('Top Regions by Revenue')
    plt.xlabel('Country')
    plt.ylabel('Total Revenue')
    plt.xticks(rotation=45)
    save_and_show_plot(fig, 'top_regions', year, month)

# ------------------------
# Main Analysis Flow
# ------------------------

def main():
    # Default year and month
    year = 2011
    month = 9

    # Allow command line args
    if len(sys.argv) >= 3:
        try:
            year = int(sys.argv[1])
            month = int(sys.argv[2])
        except ValueError:
            print("Invalid input for year/month. Using default values.")

    # Load data
    df = load_data('Mode_Craft_Ecommerce_Data - Online_Retail.csv')
    
    # Select month/year
    monthly_df = filter_month(df, year, month)

    if monthly_df.empty:
        print(f"No data found for {month}/{year}. Please try another month.")
        return

    print(f"\n=== Monthly Analysis Report for {month}/{year} ===\n")

    # Generate reports
    top_products, bottom_products, top_revenue, bottom_revenue = top_bottom_products(monthly_df)
    customers = top_customers(monthly_df)
    days = popular_days(monthly_df)
    hours = popular_hours(monthly_df)
    regions = top_regions(monthly_df)
    suggestions = generate_suggestions()

    # Display tables
    print("Top 5 Products by Quantity Sold:")
    print(top_products[['Quantity']].reset_index().to_markdown())
    print("\nBottom 5 Products by Quantity Sold:")
    print(bottom_products[['Quantity']].reset_index().to_markdown())

    print("\nTop 5 Products by Revenue Generated:")
    print(top_revenue[['TotalPrice']].rename(columns={'TotalPrice':'Revenue'}).reset_index().to_markdown())
    print("\nBottom 5 Products by Revenue Generated:")
    print(bottom_revenue[['TotalPrice']].rename(columns={'TotalPrice':'Revenue'}).reset_index().to_markdown())

    print("\nTop 5 Customers by Revenue:")
    print(customers.reset_index().rename(columns={'TotalPrice':'Revenue'}).to_markdown())

    print("\nMost Popular Days of the Week:")
    print(days.reset_index().rename(columns={'index':'Purchases', 'InvoiceDate':'count'}).to_markdown())

    print("\nMost Popular Purchase Times (Hour of Day):")
    print(hours.reset_index().rename(columns={'index':'Purchases', 'InvoiceDate':'count'}).to_markdown())

    print("\nTop 5 Regions by Revenue:")
    print(regions.head(5).reset_index().rename(columns={'TotalPrice':'Revenue'}).to_markdown())

    print("\nSuggestions to Increase Revenue:")
    for suggestion in suggestions:
        print(suggestion)

    # Create and save plots
    plot_purchase_times(hours, year, month)
    plot_weekday_sales(days, year, month)
    plot_monthly_sales(monthly_df, year, month)
    plot_top_regions(regions, year, month)

if __name__ == "__main__":
    main()
