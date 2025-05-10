from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to fetch data from API

# Load Data
df = pd.read_csv("attached_assets/indiamart_casting_data_cleaned_no_missing_prices.csv")

# Define scoring weights
SCORING_WEIGHTS = {
    'products': 0.15,        
    'business_info': 0.20,   
    'quality': 0.25,         
    'market_presence': 0.25, 
    'accessibility': 0.15    
}

# Supplier score calculation
def calculate_supplier_score(row):
    score = 0
    product_score = 0
    if pd.notna(row['Product Name']):
        words = len(row['Product Name'].split())
        product_score = min(words / 10, 1)  
        manufacturing_terms = ['casting', 'machined', 'forged', 'precision', 'custom']
        if any(term in row['Product Name'].lower() for term in manufacturing_terms):
            product_score += 0.3
        product_score = min(product_score, 1.0)

    business_score = 0.5 if pd.notna(row['Company URL']) else 0
    company_patterns = ['ltd', 'private', 'inc']
    if any(pattern in str(row['Company']).lower() for pattern in company_patterns):
        business_score += 0.5
    business_score = min(business_score, 1.0)

    quality_score = row['Rating'] / 5.0 if pd.notna(row['Rating']) else 0
    quality_terms = ['premium', 'iso', 'certified']
    if any(term in str(row['Product Name']).lower() for term in quality_terms):
        quality_score += 0.3
    quality_score = min(quality_score, 1.0)

    market_score = 0.5 if pd.notna(row['Company URL']) and pd.notna(row['Product URL']) else 0
    market_score = min(market_score, 1.0)

    accessibility_score = 0.5 if pd.notna(row['Phone']) else 0
    if pd.notna(row['Address']) or pd.notna(row['City']):
        accessibility_score += 0.5
    accessibility_score = min(accessibility_score, 1.0)

    final_score = (
        SCORING_WEIGHTS['products'] * product_score +
        SCORING_WEIGHTS['business_info'] * business_score +
        SCORING_WEIGHTS['quality'] * quality_score +
        SCORING_WEIGHTS['market_presence'] * market_score +
        SCORING_WEIGHTS['accessibility'] * accessibility_score
    )

    return round(final_score * 100, 1)

df['Supplier Score'] = df.apply(calculate_supplier_score, axis=1)

@app.route('/suppliers', methods=['GET'])
def get_suppliers():
    keyword = request.args.get('keyword')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    city = request.args.get('city')
    sort_by = request.args.get('sort_by', 'Supplier Score')
    order = request.args.get('order', 'desc')

    filtered_df = df.copy()

    if keyword:
        filtered_df = filtered_df[filtered_df['Keyword'].str.contains(keyword, case=False, na=False)]
    
    if min_price is not None and max_price is not None:
        filtered_df = filtered_df[(filtered_df['Price (per Kg)'] >= min_price) & (filtered_df['Price (per Kg)'] <= max_price)]

    if city:
        filtered_df = filtered_df[filtered_df['City'] == city]

    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=(order == 'asc'))

    return jsonify(filtered_df.to_dict(orient='records'))

@app.route('/supplier/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    supplier = df.loc[supplier_id].to_dict()
    return jsonify(supplier)

if __name__ == '__main__':
    app.run(debug=True)
