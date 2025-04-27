# DubsTech

## Overview

DubsTech is an interactive data visualization web application that analyzes e-commerce sales data.
It offers insights into monthly trends, geographical patterns, and product popularity, along with a dark mode toggle and automatic report generation.

## Getting Started

### Prerequisites

- Python 3
- Flask
- Pandas
- Regular Expressions

### Installation

```bash
# Clone the repository
 git clone https://github.com/your-username/DubsTech.git
 cd DubsTech

# Install dependencies (if applicable)
# For Node.js projects:
 npm install
# For Python projects:
 pip install -r requirements.txt
```

### Running the Application

```bash
# If using a simple HTTP server:
 python3 -m http.server 8000 --directory .
# If using Flask:
 export FLASK_APP=app.py
 flask run
```

Open your browser and navigate to `http://localhost:5000` (http://127.0.0.1:5000 or appropriate).

## Pages

### Index Page
The landing page provides an overview of the available analyses and navigation to each detailed report.
Users can toggle dark mode for better readability and view a summary of sales trends.

![Index Page Screenshot](readmeimages/homepage.png)

### Monthly Page
The monthly page displays trends over time, including:
- Sales Quantity
- Sales Revenue
- Days
- Regions

![Monthly Page Screenshot](readmeimages/monthlyanalysis.png)

### Geographical Page
The geographical page showcases sales distribution by region, including:
- Top Performing Regions
- Areas for Expansion
- Interactive Region Chart

![Geographical Page Screenshot](readmeimages/geographicalanalysis.png)

### Product Page
The product page breaks down:
- Top-selling products
- Sales by product category
- Trends in product demand over time

![Product Page Screenshot](readmeimages/productanalysis.png)


## Dark Mode & App Usage
Dark mode is available across all pages for easier viewing in low-light environments.

### Index Page

![Index Page Screenshot](readmeimages/darkhome.png)

### Monthly Page

![Monthly Page Screenshot](readmeimages/darkmonthly.png)

### Geographical Page

![Geographical Page Screenshot](readmeimages/darkgeographical.png)

### Product Page

![Product Page Screenshot](readmeimages/darkproduct.png)


## Features
- 📊 Interactive Visualizations: View trends by month, region, and product.
- 🌙 Dark Mode Toggle: Switch between light and dark themes seamlessly.
- 📍 Geographical Insights: Explore city-wise and regional sales data.
- -🛍️ Product Analytics: Identify top-selling items and product trends.
- 📄 Custom Report Generation: Select graphs to generate reports or export a complete PDF report.
- ⚡ Responsive Design: Optimized for both desktop and mobile viewing.
- 🧩 Modular Codebase: Easy to extend and maintain.
