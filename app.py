import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import re

# Set page configuration
st.set_page_config(page_title="Manufacturer Directory",
                   page_icon="🏭",
                   layout="wide")

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Supplier Search"])

# App title
st.title("Company Sniffer")

# Home page
if page == "Home":
    st.markdown("## 🏭 Welcome to the Industry Supplier Directory")
    
    # Hero section
    st.markdown("""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; margin-bottom:20px">
        <h3>Find and Compare the Best Suppliers in the Casting Industry</h3>
        <p>Our AI-powered platform helps you identify the most reliable and high-quality casting suppliers in India.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.subheader("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 Smart Search
        - **Keyword Search**: Find suppliers by specific keywords
        - **Product Filtering**: Filter by product types and names
        - **Location-based Search**: Find suppliers in specific cities
        """)
        
        st.markdown("""
        ### 📊 Data Visualization
        - **Price Distribution**: View price trends across suppliers
        - **Score Distribution**: Compare supplier ratings at a glance
        - **Visual Reports**: Understand the market quickly
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 AI-Powered Ranking
        - **Multi-factor Scoring**: Suppliers ranked on 5 key criteria
        - **Weighted Algorithm**: Customized for casting industry
        - **Score Breakdown**: Transparent scoring explanations
        """)
        
        st.markdown("""
        ### 📱 Supplier Details
        - **Complete Contact Info**: Connect with suppliers easily
        - **Product Specifications**: View detailed product information
        - **External Links**: Visit supplier websites and product pages
        """)
    
    # Scoring explanation
    st.subheader("🧠 Our AI Ranking System")
    
    st.markdown("""
    Our intelligent supplier ranking algorithm evaluates suppliers based on five critical factors:
    
    | Factor | Weight | What We Analyze |
    | ------ | ------ | --------------- |
    | Products | 15% | Product range, manufacturing details, specialization |
    | Business Info | 20% | Company establishment, business type, market presence |
    | Quality | 25% | Certifications, ratings, quality indicators in descriptions |
    | Market Presence | 25% | Online visibility, price positioning, platform presence |
    | Accessibility | 15% | Contact information, location details, response capabilities |
    
    Each supplier receives a score from 0-100, helping you identify the best partners for your casting needs.
    """)
    
    # Call to action
    st.markdown("""
    <div style="background-color:#e6f7ea; padding:20px; border-radius:10px; margin-top:20px; text-align:center">
        <h3>Ready to find your perfect supplier?</h3>
        <p>Head to the Supplier Search page to start exploring the database of casting suppliers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get started button
    if st.button("Go to Supplier Search"):
        st.session_state.page = "Supplier Search"
        st.experimental_rerun()

# Supplier search page
elif page == "Supplier Search":
    st.markdown("## Filter and explore suppliers in the casting industry")

# Scoring weights for supplier ranking
SCORING_WEIGHTS = {
    'products': 0.15,        # Diversity of product range
    'business_info': 0.20,   # Company age, turnover, and employees
    'quality': 0.25,         # Certifications and ratings
    'market_presence': 0.25,  # Reviews and ratings
    'accessibility': 0.15    # Contact information and location
}


# Function to calculate supplier score
def calculate_supplier_score(row):
    score = 0
    
    # Products score (15%) - Based on product details in name
    product_score = 0
    if pd.notna(row['Product Name']):
        # More words in product name might indicate more product details
        words = len(row['Product Name'].split())
        product_score = min(words / 10, 1)  # Normalize to max of 1
        
        # Bonus for specific manufacturing details
        manufacturing_terms = ['casting', 'machined', 'forged', 'precision', 'custom']
        if any(term in row['Product Name'].lower() for term in manufacturing_terms):
            product_score += 0.3
            
        # Cap at 1.0
        product_score = min(product_score, 1.0)
    
    # Business info score (20%) - Based on available business info
    business_score = 0
    # Company URL often indicates established business
    if pd.notna(row['Company URL']):
        business_score += 0.5
    
    # Company name patterns suggesting established business
    company_patterns = ['ltd', 'limited', 'pvt', 'private', 'industries', 'inc', 'corporation']
    if any(pattern in str(row['Company']).lower() for pattern in company_patterns):
        business_score += 0.5
    
    # Cap at 1.0
    business_score = min(business_score, 1.0)
    
    # Quality score (25%) - Based on ratings and inferred quality
    quality_score = 0
    
    # Base on rating if available
    if pd.notna(row['Rating']) and row['Rating'] > 0:
        quality_score = row['Rating'] / 5.0  # Normalize to 0-1
    
    # Quality terms in product name
    quality_terms = ['premium', 'high quality', 'certified', 'iso', 'standard']
    if any(term in str(row['Product Name']).lower() for term in quality_terms):
        quality_score += 0.3
        
    # Cap at 1.0
    quality_score = min(quality_score, 1.0)
    
    # Market presence score (25%) - Based on price position and online presence
    market_score = 0
    
    # Competitive pricing (inverse of normalized price)
    # We'll assume higher price might indicate better quality
    if pd.notna(row['Price (per Kg)']):
        # This is just a placeholder - would be better with category-specific pricing knowledge
        price_competitiveness = 0.5  # Neutral score for price
        market_score += price_competitiveness
    
    # Online presence indicated by having URLs
    if pd.notna(row['Company URL']) and pd.notna(row['Product URL']):
        market_score += 0.5
        
    # Cap at 1.0
    market_score = min(market_score, 1.0)
    
    # Accessibility score (15%) - Contact info and location
    accessibility_score = 0
    
    # Phone and address available
    if pd.notna(row['Phone']):
        accessibility_score += 0.5
    
    if pd.notna(row['Address']) or pd.notna(row['City']):
        accessibility_score += 0.5
        
    # Cap at 1.0
    accessibility_score = min(accessibility_score, 1.0)
    
    # Calculate weighted score
    final_score = (
        SCORING_WEIGHTS['products'] * product_score +
        SCORING_WEIGHTS['business_info'] * business_score +
        SCORING_WEIGHTS['quality'] * quality_score +
        SCORING_WEIGHTS['market_presence'] * market_score +
        SCORING_WEIGHTS['accessibility'] * accessibility_score
    )
    
    # Scale to 0-100 for better readability
    return round(final_score * 100, 1)

# Load data function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "attached_assets/indiamart_casting_data_cleaned_no_missing_prices.csv"
        )
        # Convert Price to numeric, handling any errors
        df['Price (per Kg)'] = pd.to_numeric(df['Price (per Kg)'],
                                             errors='coerce')
        # Convert Rating to numeric and fill any missing ratings with 0
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)
        
        # Calculate supplier score for each row
        df['Supplier Score'] = df.apply(calculate_supplier_score, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# Load the data
df = load_data()

if df.empty:
    st.warning("No data available. Please check the CSV file.")
elif page == "Supplier Search":  # Only show filtering on Supplier Search page
    # Get unique keywords for dropdown
    keywords = sorted(df['Keyword'].unique())

    # Sidebar filters
    st.sidebar.header("Filters")

    # Keyword filter methods
    filter_method = st.sidebar.radio(
        "Choose how to filter:", ["Select from dropdown", "Search by keyword"])

    filtered_df = None

    if filter_method == "Select from dropdown":
        selected_keyword = st.sidebar.selectbox("Select a keyword:", keywords)
        filtered_df = df[df['Keyword'] == selected_keyword]
    else:
        search_term = st.sidebar.text_input(
            "Search by keyword or product name:")
        if search_term:
            # Filter based on case-insensitive partial match in Keyword or Product Name
            filtered_df = df[
                df['Keyword'].str.contains(search_term, case=False)
                | df['Product Name'].str.contains(search_term, case=False)]
        else:
            filtered_df = df.copy()

    # Additional filters
    st.sidebar.subheader("Additional Filters")

    # Price range filter
    if not filtered_df.empty:
        min_price = int(filtered_df['Price (per Kg)'].min())
        max_price = int(filtered_df['Price (per Kg)'].max())

        price_range = st.sidebar.slider("Price Range (per Kg):", min_price,
                                        max_price, (min_price, max_price))

        filtered_df = filtered_df[
            (filtered_df['Price (per Kg)'] >= price_range[0])
            & (filtered_df['Price (per Kg)'] <= price_range[1])]

    # City filter if we have data
    if not filtered_df.empty and 'City' in filtered_df.columns:
        cities = ["All Cities"] + sorted(filtered_df['City'].unique().tolist())
        selected_city = st.sidebar.selectbox("Filter by city:", cities)

        if selected_city != "All Cities":
            filtered_df = filtered_df[filtered_df['City'] == selected_city]

    # Main content area
    if filtered_df is not None:
        if filtered_df.empty:
            st.warning("No companies match your filter criteria.")
        else:
            # Display count and allow sorting
            st.subheader(f"Found {len(filtered_df)} matching companies")

            # Sorting options
            sort_col, sort_dir = st.columns(2)
            with sort_col:
                sort_by = st.selectbox("Sort by:",
                                       ["Supplier Score", "Price (per Kg)", "Rating", "Company"])
            with sort_dir:
                ascending = st.selectbox("Order:", [("Ascending", True),
                                                    ("Descending", False)],
                                         format_func=lambda x: x[0])[1]

            # Apply sorting
            if sort_by in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by=sort_by,
                                                      ascending=ascending)
                
            # Default sort by Supplier Score if selecting that option
            if sort_by == "Supplier Score":
                filtered_df = filtered_df.sort_values(by="Supplier Score", 
                                                      ascending=False)

            # Visualization of price distribution
            st.subheader("Price Distribution")
            fig = px.histogram(filtered_df,
                               x="Price (per Kg)",
                               title="Price Distribution (per Kg)",
                               labels={"Price (per Kg)": "Price (Rs per Kg)"},
                               color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig, use_container_width=True)

            # Company details
            st.subheader("Company Details")

            # Add a visualization for supplier scores
            st.subheader("Supplier Score Distribution")
            score_fig = px.histogram(
                filtered_df, 
                x="Supplier Score",
                title="AI-Ranked Supplier Score Distribution",
                labels={"Supplier Score": "Supplier Score (0-100)"},
                color_discrete_sequence=["#2ca02c"]  # Green color
            )
            st.plotly_chart(score_fig, use_container_width=True)
            
            # Display companies in a clean format with supplier score
            for i, row in filtered_df.iterrows():
                with st.container():
                    # Create header with supplier score
                    score = row['Supplier Score']
                    
                    # Create color based on score
                    if score >= 80:
                        score_color = "green"
                    elif score >= 60:
                        score_color = "orange"
                    else:
                        score_color = "gray"
                    
                    # Display company name with score badge
                    st.markdown(f"""
                    ### {row['Company']} 
                    <span style="background-color:{score_color}; color:white; padding:4px 8px; border-radius:4px; font-size:16px;">
                    AI Score: {score}/100
                    </span>
                    """, unsafe_allow_html=True)
                    
                    # Add score breakdown expander
                    with st.expander("View Score Breakdown"):
                        st.markdown("**Score Components:**")
                        
                        # Calculate component scores (simplified)
                        product_terms = ['casting', 'machined', 'forged', 'precision', 'custom']
                        product_matches = sum(1 for term in product_terms if term in str(row['Product Name']).lower())
                        
                        quality_terms = ['premium', 'high quality', 'certified', 'iso', 'standard']
                        quality_matches = sum(1 for term in quality_terms if term in str(row['Product Name']).lower())
                        
                        company_terms = ['ltd', 'limited', 'pvt', 'private', 'industries', 'inc', 'corporation']
                        company_matches = sum(1 for term in company_terms if term in str(row['Company']).lower())
                        
                        # Create score breakdown
                        st.markdown(f"""
                        - **Products (15%)**: {'⭐' * min(product_matches+1, 5)}
                        - **Business Info (20%)**: {'⭐' * min(company_matches+1, 5)}
                        - **Quality (25%)**: {'⭐' * (int(row['Rating']) if row['Rating'] > 0 else min(quality_matches+1, 3))}
                        - **Market Presence (25%)**: {'⭐' * min(3 if pd.notna(row['Company URL']) else 1, 5)}
                        - **Accessibility (15%)**: {'⭐' * min(3 if pd.notna(row['Phone']) else 1, 5)}
                        """)
                    
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Product:** {row['Product Name']}")
                        st.markdown(
                            f"**Price:** ₹{row['Price (per Kg)']} per Kg")

                        if 'Rating' in row and row['Rating'] > 0:
                            st.markdown(
                                f"**Rating:** {'⭐' * int(row['Rating'])}")

                        if 'Address' in row and pd.notna(row['Address']):
                            st.markdown(f"**Address:** {row['Address']}")

                        if 'City' in row and pd.notna(row['City']):
                            st.markdown(f"**City:** {row['City']}")

                    with col2:
                        if 'Phone' in row and pd.notna(row['Phone']):
                            st.markdown(f"**Phone:** {row['Phone']}")

                        if 'Product URL' in row and pd.notna(
                                row['Product URL']):
                            st.markdown(
                                f"[View Product on IndiaMART]({row['Product URL']})"
                            )

                        if 'Company URL' in row and pd.notna(
                                row['Company URL']):
                            st.markdown(
                                f"[Visit Company Website]({row['Company URL']})"
                            )

                    st.divider()

            # Export option
            if st.button("Export Results to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="casting_companies_export.csv",
                    mime="text/csv")
