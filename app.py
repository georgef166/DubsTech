from flask import Flask, render_template, request, jsonify
import os
import pandas as pd

app = Flask(__name__)

# --- Utility Functions ---
def load_csv(filepath):
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return pd.DataFrame()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/geographical')
def geographical():
    # For demo: load top regions and expansion areas
    top_regions = load_csv('geographical/top_performing_regions.csv').to_dict(orient='records')
    expansion = load_csv('geographical/potential_expansion_areas.csv').to_dict(orient='records')
    return render_template('geographical.html', top_regions=top_regions, expansion=expansion)

@app.route('/monthly')
def monthly():
    # For demo: just render the page, CSVs loaded dynamically
    return render_template('monthly.html')

@app.route('/product')
def product():
    # For demo: just render the page, CSVs loaded dynamically
    return render_template('product.html')

# --- API for CSV Data ---
@app.route('/api/monthly/<report_type>')
def api_monthly_report(report_type):
    month = request.args.get('month')
    year = request.args.get('year', type=int)
    if not month or not year:
        return jsonify({'error': 'Month and year required'}), 400
    # Load data and preprocess
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    if not os.path.exists(data_file):
        return jsonify({'error': 'Data file missing'}), 500
    df = pd.read_csv(data_file, parse_dates=['InvoiceDate'], low_memory=False)
    df = df.dropna(subset=['InvoiceDate','Quantity','UnitPrice','Description'])
    df['Month'] = df['InvoiceDate'].dt.month_name()
    df['Year'] = df['InvoiceDate'].dt.year
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df['InvoiceDate'].dt.hour
    # Filter by selected month/year
    sel = df[(df['Month']==month) & (df['Year']==year)]
    if sel.empty:
        return jsonify({'error': 'No data for this period'}), 404
    # Compute report based on type
    if report_type == 'top_products_qty':
        out = sel.groupby('Description')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=False)
        return out.to_json(orient='records')
    elif report_type == 'least_products_qty':
        out = sel.groupby('Description')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=True)
        return out.to_json(orient='records')
    elif report_type == 'top_products_revenue':
        out = sel.groupby('Description')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
        return out.to_json(orient='records')
    elif report_type == 'least_products_revenue':
        out = sel.groupby('Description')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=True)
        return out.to_json(orient='records')
    elif report_type == 'top_customers':
        out = sel.groupby('CustomerID')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
        return out.to_json(orient='records')
    elif report_type == 'popular_days':
        out = sel.groupby('DayOfWeek')['InvoiceNo'].count().reset_index(name='Count')
        return out.to_json(orient='records')
    elif report_type == 'popular_times_by_day':
        out = sel.groupby('Hour')['InvoiceNo'].count().reset_index(name='Count')
        return out.to_json(orient='records')
    elif report_type == 'top_regions':
        out = sel.groupby('Country')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
        return out.to_json(orient='records')
    elif report_type == 'summary_stats':
        total_qty = int(sel['Quantity'].sum())
        total_rev = float(sel['Revenue'].sum())
        trans = int(sel['InvoiceNo'].nunique())
        txt = f"Period: {month} {year}\nTotal Transactions: {trans}\nTotal Quantity Sold: {total_qty}\nTotal Revenue: {total_rev:.2f}"
        return jsonify({'text': txt})
    elif report_type == 'revenue_suggestions':
        # Simple suggestion: top product by revenue
        top = sel.groupby('Description')['Revenue'].sum().idxmax()
        txt = f"Focus on marketing '{top}', it generated the highest revenue this period."  
        return jsonify({'text': txt})
    else:
        return jsonify({'error': 'Invalid report type'}), 400

@app.route('/api/monthly/options')
def monthly_options():
    # Dynamically list months/years present in data
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    if not os.path.exists(data_file):
        return jsonify({'error': 'Data file missing'}), 500
    df = pd.read_csv(data_file, parse_dates=['InvoiceDate'], low_memory=False)
    df = df.dropna(subset=['InvoiceDate'])
    df['Month'] = df['InvoiceDate'].dt.month_name()
    df['Year'] = df['InvoiceDate'].dt.year
    # Unique combos
    combos = df[['Month','Year']].drop_duplicates()
    # Sort by year then month order
    import calendar
    month_order = {m:i for i,m in enumerate(calendar.month_name)}
    combos['month_order'] = combos['Month'].map(month_order)
    combos = combos.sort_values(['Year','month_order'])
    raw_opts = combos[['Month','Year']].to_dict(orient='records')
    options = [{'month': o['Month'], 'year': int(o['Year'])} for o in raw_opts]
    return jsonify({'options': options})

@app.route('/api/product/<product_file>')
def api_product_report(product_file):
    filepath = f'productreports/{product_file}'
    # auto-generate missing report if not present
    if not os.path.exists(filepath):
        try:
            # extract product name (before suffix)
            product_name = product_file.rsplit('_', 3)[0]
            subprocess.run(['python3', 'productreport.py', product_name], check=True)
        except Exception:
            return jsonify({'error': 'Failed to generate report'}), 404
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found after generation'}), 404
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
        return df.to_json(orient='records')
    else:
        with open(filepath, 'r') as f:
            return jsonify({'text': f.read()})

from flask import request
import subprocess
@app.route('/api/product/generate', methods=['POST'])
def generate_product_report():
    product = request.json.get('product')
    if not product:
        return jsonify({'error': 'No product specified'}), 400
    # Call productreport.py as a subprocess
    try:
        subprocess.run(['python3', 'productreport.py', product], check=True)
        return jsonify({'status': 'Report generation started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/options')
def product_options():
    data_file = 'Mode_Craft_Ecommerce_Data - Online_Retail.csv'
    products = []
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        products = sorted(df['Description'].dropna().unique().tolist())
    return jsonify({'products': products})

if __name__ == '__main__':
    # ensure required output folders exist
    import os
    for d in ['monthlyanalysisreports', 'geographical', 'productreports']:
        os.makedirs(d, exist_ok=True)
    # generate initial geographical CSVs
    from geographical import geographical_analysis
    geographical_analysis('Mode_Craft_Ecommerce_Data - Online_Retail.csv')
    # generate initial monthly analysis reports for default year/month
    from monthlyanalysisreport import generate_monthly_analysis
    generate_monthly_analysis('Mode_Craft_Ecommerce_Data - Online_Retail.csv', 2011, 'December')
    # generate initial product report for first available product
    from productreport import product_report
    try:
        df_desc = pd.read_csv('Mode_Craft_Ecommerce_Data - Online_Retail.csv', usecols=['Description'], encoding='ISO-8859-1', low_memory=False)
        first_prod = df_desc['Description'].dropna().iloc[0]
        product_report('Mode_Craft_Ecommerce_Data - Online_Retail.csv', first_prod)
    except Exception:
        pass
    app.run(debug=True)
