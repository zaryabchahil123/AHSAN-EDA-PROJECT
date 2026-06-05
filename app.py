import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import sys

# Append local path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import filters
import charts

# Page Config
st.set_page_config(
    page_title="OEWS May 2025 Employment & Wage Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS
st.markdown("""
    <style>
    /* Main body background */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Title container styling */
    .title-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #2F6EB4 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
    }
    .title-container h1 {
        color: white !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        font-size: 2.5rem;
    }
    .title-container p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card borders and shadow */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #E5E7EB;
        padding: 1.25rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #E5E7EB;
    }
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 10px;
    }
    
    /* Tabs styling */
    div.stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    div.stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stTabs [data-baseweb="tab"]:hover {
        background-color: #F3F4F6;
        border-color: #D1D5DB;
    }
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2F6EB4;
        color: white;
        border-color: #2F6EB4;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Load Data with spinner and caching
@st.cache_data(show_spinner=False)
def get_dataset():
    # If the clean CSV exists, it loads instantly.
    # Otherwise, it runs the 1-2 min Excel processing.
    return filters.load_data()

# Show clean loading indicator on first run
if not os.path.exists(filters.CACHE_CSV_PATH):
    with st.spinner("⏳ Parsing Excel raw dataset (data/all_data_M_2025.xlsx)... This first load can take up to 2 minutes. Future loads will be instantaneous."):
        df = get_dataset()
else:
    df = get_dataset()

# Handle empty dataset cases
if df is None or df.empty:
    st.error("Error: Could not load the dataset. Please ensure 'data/all_data_M_2025.xlsx' is present.")
    st.stop()

# Get global min/max for sliders
max_emp_val = int(df['TOT_EMP'].max()) if pd.notna(df['TOT_EMP'].max()) else 10000000
max_wage_val = float(df['H_MEAN'].max()) if pd.notna(df['H_MEAN'].max()) else 150.0

# 2. Filter Resets & Session State Setup
if 'area_type_filter' not in st.session_state:
    st.session_state.area_type_filter = 'All'
if 'state_filter' not in st.session_state:
    st.session_state.state_filter = []
if 'search_filter' not in st.session_state:
    st.session_state.search_filter = ''
if 'emp_range_filter' not in st.session_state:
    st.session_state.emp_range_filter = (0, max_emp_val)
if 'wage_range_filter' not in st.session_state:
    st.session_state.wage_range_filter = (0.0, max_wage_val)

def reset_all_filters():
    st.session_state.area_type_filter = 'All'
    st.session_state.state_filter = []
    st.session_state.search_filter = ''
    st.session_state.emp_range_filter = (0, max_emp_val)
    st.session_state.wage_range_filter = (0.0, max_wage_val)

# 3. Sidebar Navigation & Interactive Filters
st.sidebar.image("https://www.bls.gov/images/bls_emblem.gif", width=80)
st.sidebar.markdown("### 📊 Interactive Controls")

# Reset button
st.sidebar.button("🔄 Reset / Clear Filters", on_click=reset_all_filters)
st.sidebar.markdown("---")

# Filter inputs
area_types = ['All'] + sorted(df['AREA_TYPE_NAME'].unique().tolist())
selected_area_type = st.sidebar.selectbox(
    "Area Type Category Filter",
    options=area_types,
    key='area_type_filter'
)

states_list = sorted(df['PRIM_STATE'].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "State Filter (Multi-select)",
    options=states_list,
    key='state_filter',
    help="Select one or more states to view data. Leave empty for all states."
)

st_search = st.sidebar.text_input(
    "Search Filter (Keyword)",
    key='search_filter',
    placeholder="Search occupation/industry..."
)

selected_emp_range = st.sidebar.slider(
    "Employment Range Slider",
    min_value=0,
    max_value=max_emp_val,
    key='emp_range_filter',
    step=1000
)

selected_wage_range = st.sidebar.slider(
    "Hourly Mean Wage Slider ($)",
    min_value=0.0,
    max_value=max_wage_val,
    key='wage_range_filter',
    step=1.0
)

# Apply filters using filters.py
active_filters = {
    'area_type': selected_area_type,
    'states': selected_states if len(selected_states) > 0 else 'All',
    'emp_range': selected_emp_range,
    'wage_range': selected_wage_range,
    'search_query': st_search
}

filtered_df = filters.apply_filters(df, active_filters)

# 4. Main Panel Layout
st.markdown("""
    <div class="title-container">
        <h1>OEWS May 2025 Employment & Wage Dashboard</h1>
        <p>Interactive dashboard analyzing the Bureau of Labor Statistics (BLS) Occupational Employment and Wage Statistics (OEWS) May 2025 dataset.</p>
    </div>
""", unsafe_allow_html=True)

# 5. KPI Cards
total_records = len(df)
filtered_records = len(filtered_df)

if not filtered_df.empty:
    avg_hourly = filtered_df['H_MEAN'].mean()
    avg_annual = filtered_df['A_MEAN'].mean()
    unique_areas = filtered_df['AREA_TITLE'].nunique()
    
    # Calculate top occupations and industry for KPIs
    top_paying_idx = filtered_df['H_MEAN'].idxmax() if filtered_df['H_MEAN'].notna().any() else None
    top_paying_job = filtered_df.loc[top_paying_idx, 'OCC_TITLE'] if top_paying_idx else "N/A"
    top_paying_wage = filtered_df.loc[top_paying_idx, 'H_MEAN'] if top_paying_idx else 0.0
else:
    avg_hourly = 0.0
    avg_annual = 0.0
    unique_areas = 0
    top_paying_job = "N/A"
    top_paying_wage = 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Records Loaded / Filtered",
        value=f"{filtered_records:,}",
        delta=f"Total: {total_records:,}",
        delta_color="off"
    )
with kpi2:
    st.metric(
        label="Average Hourly Wage",
        value=f"${avg_hourly:.2f}" if avg_hourly > 0 else "N/A",
        help="Mean of hourly wages for filtered records"
    )
with kpi3:
    st.metric(
        label="Average Annual Wage",
        value=f"${avg_annual:,.2f}" if avg_annual > 0 else "N/A",
        help="Mean of annual wages for filtered records"
    )
with kpi4:
    st.metric(
        label="Highest Paying Occupation",
        value=top_paying_job[:22] + "..." if len(top_paying_job) > 22 else top_paying_job,
        delta=f"${top_paying_wage:.2f}/hr" if top_paying_wage > 0 else "N/A"
    )

st.markdown("<br>", unsafe_allow_html=True)

# 6. Organized Tabs
tab_overview, tab_emp, tab_wage, tab_matrix, tab_table, tab_dictionary = st.tabs([
    "📍 Overview & KPI Stats", 
    "📈 Employment Trends", 
    "💸 Wage & Pay Spread", 
    "🔄 Correlation & Matrix", 
    "🔍 Data Explorer",
    "📖 Data Dictionary"
])

# Tab 1: Overview & KPI Stats
with tab_overview:
    st.markdown("### Dashboard Overview")
    st.markdown("""
        This dashboard presents interactive analytics on employment structures, wage percentiles, and market concentration patterns across the United States.
        Use the sidebar controls on the left to filter the visualization dynamically.
    """)
    
    col_overview_left, col_overview_right = st.columns([3, 2])
    with col_overview_left:
        # Chart 9: Count Plot
        st.markdown("##### Record Counts across Area Categories")
        fig9 = charts.create_count_plot(filtered_df)
        st.pyplot(fig9)
    with col_overview_right:
        st.markdown("##### Filters Active State Summary")
        st.info(f"""
            - **Selected Area Type:** `{selected_area_type}`
            - **Filtered States:** `{', '.join(selected_states) if len(selected_states) > 0 else 'All States'}`
            - **Search Keyword:** `"{st_search}"`
            - **Employment Bounds:** `{selected_emp_range[0]:,}` to `{selected_emp_range[1]:,}`
            - **Hourly Mean Bounds:** `${selected_wage_range[0]:.2f}` to `${selected_wage_range[1]:.2f}`
        """)
        st.markdown("##### Notable Insight")
        if not filtered_df.empty:
            top_emp_row = filtered_df[filtered_df['OCC_TITLE'] != 'All Occupations'].nlargest(1, 'TOT_EMP')
            if not top_emp_row.empty:
                st.success(f"""
                    **Largest Occupation Category:**  
                    *{top_emp_row.iloc[0]['OCC_TITLE']}*  
                    Total Employment: **{int(top_emp_row.iloc[0]['TOT_EMP']):,}** workers.
                """)
        else:
            st.warning("No records match the current filters.")

# Tab 2: Employment Trends
with tab_emp:
    st.markdown("### Employment Share and Sector Hierarchies")
    
    col_emp_left, col_emp_right = st.columns(2)
    with col_emp_left:
        # Chart 1: Pie Chart
        st.markdown("##### Proportional Employment Share")
        fig1 = charts.create_pie_chart(filtered_df)
        st.pyplot(fig1)
    with col_emp_right:
        # Chart 8: Area Chart
        st.markdown("##### Cumulative Employment of Top Sectors")
        fig8 = charts.create_area_chart(filtered_df)
        st.pyplot(fig8)

# Tab 3: Wage & Pay Spread
with tab_wage:
    st.markdown("### Wage Distribution and Pay Scale Ranges")
    
    col_wage1, col_wage2 = st.columns(2)
    with col_wage1:
        # Chart 2: Histogram
        st.markdown("##### Wage Density Distribution")
        fig2 = charts.create_histogram(filtered_df)
        st.pyplot(fig2)
    with col_wage2:
        # Chart 6: Box Plot
        st.markdown("##### Wage Spread by Area Category")
        fig6 = charts.create_box_plot(filtered_df)
        st.pyplot(fig6)
        
    st.markdown("---")
    
    col_wage3, col_wage4 = st.columns(2)
    with col_wage3:
        # Chart 10: Violin Plot
        st.markdown("##### Probability Density (Violin) of Hourly Wages")
        fig10 = charts.create_violin_plot(filtered_df)
        st.pyplot(fig10)
    with col_wage4:
        # Chart 3: Line Chart
        st.markdown("##### Wage Percentile Hierarchies")
        fig3 = charts.create_line_chart(filtered_df)
        st.pyplot(fig3)

# Tab 4: Correlation & Matrix
with tab_matrix:
    st.markdown("### Statistical Correlations and Scatter Trends")
    
    col_mat_left, col_mat_right = st.columns(2)
    with col_mat_left:
        # Chart 7: Heatmap
        st.markdown("##### Correlation Matrix of Numeric Metrics")
        fig7 = charts.create_heatmap(filtered_df)
        st.pyplot(fig7)
    with col_mat_right:
        # Chart 5: Scatter Plot
        st.markdown("##### Wage vs. Employment Scatter Relation")
        fig5 = charts.create_scatter_plot(filtered_df)
        st.pyplot(fig5)
        
    st.markdown("---")
    st.markdown("#### 🌟 Bonus Visualization: Location Quotient Analysis")
    # Bonus Chart
    fig_bubble = charts.create_bubble_chart(filtered_df)
    st.pyplot(fig_bubble)

# Tab 5: Data Explorer
with tab_table:
    st.markdown("### Searchable Data Explorer")
    st.markdown("Inspect, sort, and search the filtered dataset records in real time.")
    
    if filtered_df.empty:
        st.warning("No records match the current filters.")
    else:
        # We select relevant columns to keep table clean and professional
        display_cols = [
            'AREA_TITLE', 'AREA_TYPE_NAME', 'PRIM_STATE', 'OCC_TITLE', 
            'NAICS_TITLE', 'TOT_EMP', 'H_MEAN', 'A_MEAN', 'LOC_QUOTIENT'
        ]
        # Clean naming
        df_table = filtered_df[display_cols].rename(columns={
            'AREA_TITLE': 'Area Name',
            'AREA_TYPE_NAME': 'Area Category',
            'PRIM_STATE': 'State',
            'OCC_TITLE': 'Occupation Title',
            'NAICS_TITLE': 'Industry Title',
            'TOT_EMP': 'Total Employment',
            'H_MEAN': 'Hourly Mean Wage ($)',
            'A_MEAN': 'Annual Mean Wage ($)',
            'LOC_QUOTIENT': 'Location Quotient'
        })
        
        # Paginated display using Streamlit's native dataframe widget (allows sorting, downloading)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(df_table):,} records matching filters.")

# Tab 6: Data Dictionary
with tab_dictionary:
    st.markdown("### Data Dictionary & Metadata")
    st.markdown("Descriptions of the columns included in the BLS OEWS May 2025 dataset.")
    
    try:
        df_desc = pd.read_excel('data/all_data_M_2025.xlsx', sheet_name='Field Descriptions')
        # Clean up column names and empty rows
        df_desc.columns = ['Field Name', 'Description', 'Extra']
        df_desc = df_desc.dropna(subset=['Field Name', 'Description'])
        # Filter rows that look like actual dictionary fields
        df_dict = df_desc[df_desc['Field Name'].str.islower() & (df_desc['Field Name'].str.len() < 25)]
        
        st.table(df_dict[['Field Name', 'Description']].reset_index(drop=True))
    except Exception as e:
        # Standard Fallback Dictionary
        st.markdown("""
            | Field Name | Description |
            |---|---|
            | **AREA** | U.S. (99), state FIPS code, Metropolitan Statistical Area (MSA) code, or OEWS-specific nonmetropolitan area code |
            | **AREA_TITLE** | Area name |
            | **AREA_TYPE** | Area type: 1= U.S.; 2= State; 3= U.S. Territory; 4= Metropolitan Statistical Area (MSA); 6= Nonmetropolitan Area |
            | **PRIM_STATE** | The primary state for the given area |
            | **NAICS** | North American Industry Classification System (NAICS) code for the given industry |
            | **NAICS_TITLE** | NAICS title for the given industry |
            | **OCC_CODE** | Standard Occupational Classification (SOC) code |
            | **OCC_TITLE** | SOC title for the occupation |
            | **TOT_EMP** | Estimated total employment |
            | **H_MEAN** | Mean hourly wage |
            | **A_MEAN** | Mean annual wage |
            | **LOC_QUOTIENT** | The location quotient representing the ratio of an occupation's share of employment in a given area to that in the U.S. as a whole |
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; font-size: 0.85rem; padding: 10px 0;'>"
    "Developed for Exploratory Data Analysis Course Project Submission. Instructor: Ali Hassan Sherazi. "
    "Dataset: BLS OEWS May 2025 Estimates."
    "</div>",
    unsafe_allow_html=True
)
