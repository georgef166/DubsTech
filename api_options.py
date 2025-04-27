from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/api/monthly/options')
def monthly_options():
    # Scan files for available months/years
    files = os.listdir('monthlyanalysisreports')
    options = set()
    for f in files:
        if '_' in f:
            parts = f.split('_')
            if len(parts) >= 3:
                month = parts[-2]
                year = parts[-1].split('.')[0]
                options.add((month, year))
    options = sorted(list(options), key=lambda x: (x[1], x[0]))
    return jsonify({'months': [m for m, y in options], 'years': [y for m, y in options]})

@app.route('/api/products/options')
def product_options():
    # Scan main data for unique products!
    df = pd.read_csv('Mode_Craft_Ecommerce_Data - Online_Retail.csv')
    products = sorted(df['Description'].dropna().unique().tolist())
    return jsonify({'products': products})

if __name__ == '__main__':
    app.run(debug=True)
