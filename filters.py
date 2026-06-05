import pandas as pd
import numpy as np
import os

CACHE_CSV_PATH = 'data/all_data_M_2025_clean.csv'

def clean_numeric_col(series):
    """Converts a pandas series containing text placeholders to float."""
    # Replace common BLS placeholders with NaN
    # *: estimate not available
    # **: PRSE not available, or employment estimate not available
    # #: wage equal to or greater than $115.00/hour or $239,200/year
    # ~: not applicable
    s = series.astype(str).str.strip()
    s = s.replace(to_replace=[r'\*+', r'\#', '~', 'nan', 'None', '-'], value=np.nan, regex=True)
    return pd.to_numeric(s, errors='coerce')

def load_data(file_path='data/all_data_M_2025.xlsx'):
    """Loads dataset from Excel and cleans it. Uses a local CSV cache for optimization."""
    # Check if a clean CSV cache exists to speed up startup to < 2 seconds
    if os.path.exists(CACHE_CSV_PATH):
        print(f"Loading cleaned dataset from cache: {CACHE_CSV_PATH}")
        df = pd.read_csv(CACHE_CSV_PATH, low_memory=False)
        return df

    print(f"Reading raw dataset from: {file_path} (This can take 1-2 minutes for the first run)...")
    # Load sheet
    df = pd.read_excel(file_path, sheet_name='All May 2025 data')
    
    # Standardize column names to uppercase
    df.columns = [col.upper() for col in df.columns]
    
    # 1. Clean numeric columns
    numeric_cols = [
        'TOT_EMP', 'EMP_PRSE', 'JOBS_1000', 'LOC_QUOTIENT', 'PCT_TOTAL', 'PCT_RPT',
        'H_MEAN', 'A_MEAN', 'MEAN_PRSE',
        'H_PCT10', 'H_PCT25', 'H_MEDIAN', 'H_PCT75', 'H_PCT90',
        'A_PCT10', 'A_PCT25', 'A_MEDIAN', 'A_PCT75', 'A_PCT90'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric_col(df[col])
            
    # 2. Map Area Type code to descriptive names
    # 1= U.S.; 2= State; 3= U.S. Territory; 4= Metropolitan Statistical Area (MSA); 6= Nonmetropolitan Area
    area_type_map = {
        1: 'National (U.S.)',
        2: 'State',
        3: 'U.S. Territory',
        4: 'Metropolitan Area (MSA)',
        6: 'Nonmetropolitan Area'
    }
    if 'AREA_TYPE' in df.columns:
        # Convert area type to numeric first if it's not
        df['AREA_TYPE_CODE'] = pd.to_numeric(df['AREA_TYPE'], errors='coerce')
        df['AREA_TYPE_NAME'] = df['AREA_TYPE_CODE'].map(area_type_map).fillna('Other')
    else:
        df['AREA_TYPE_NAME'] = 'Unknown'
        
    # Fill standard text NaNs
    text_cols = ['AREA_TITLE', 'PRIM_STATE', 'NAICS_TITLE', 'OCC_CODE', 'OCC_TITLE', 'O_GROUP']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df.loc[df[col].isin(['nan', 'None', '']), col] = 'Unknown'
            
    # Cache the cleaned dataframe as a CSV file in the data/ folder
    try:
        print(f"Creating cache: {CACHE_CSV_PATH}")
        df.to_csv(CACHE_CSV_PATH, index=False)
    except Exception as e:
        print(f"Warning: Could not create cache file: {e}")
        
    return df

def apply_filters(df, filters):
    """
    Applies interactive filters to the dataframe.
    filters is a dictionary of the form:
    {
        'area_type': list of selected area types or 'All',
        'states': list of selected states or 'All',
        'o_groups': list of selected occupation levels/groups or 'All',
        'emp_range': (min_emp, max_emp),
        'wage_range': (min_wage, max_wage),
        'search_query': str (search in OCC_TITLE or NAICS_TITLE)
    }
    """
    filtered_df = df.copy()
    
    # 1. Filter by Area Type
    if 'area_type' in filters and filters['area_type'] != 'All':
        selected_types = filters['area_type']
        if not isinstance(selected_types, list):
            selected_types = [selected_types]
        if 'All' not in selected_types and len(selected_types) > 0:
            filtered_df = filtered_df[filtered_df['AREA_TYPE_NAME'].isin(selected_types)]
            
    # 2. Filter by States
    if 'states' in filters and filters['states'] != 'All':
        selected_states = filters['states']
        if not isinstance(selected_states, list):
            selected_states = [selected_states]
        if 'All' not in selected_states and len(selected_states) > 0:
            filtered_df = filtered_df[filtered_df['PRIM_STATE'].isin(selected_states)]
            
    # 3. Filter by Occupation Group (SOC Level)
    if 'o_groups' in filters and filters['o_groups'] != 'All':
        selected_groups = filters['o_groups']
        if not isinstance(selected_groups, list):
            selected_groups = [selected_groups]
        if 'All' not in selected_groups and len(selected_groups) > 0:
            filtered_df = filtered_df[filtered_df['O_GROUP'].isin(selected_groups)]
            
    # 4. Filter by Employment Range
    if 'emp_range' in filters and filters['emp_range'] is not None:
        min_emp, max_emp = filters['emp_range']
        # Filter matching range, but allow NaNs to be excluded or included? We exclude NaNs for range filters.
        filtered_df = filtered_df[filtered_df['TOT_EMP'].between(min_emp, max_emp, inclusive='both')]
        
    # 5. Filter by Wage Range
    if 'wage_range' in filters and filters['wage_range'] is not None:
        min_wage, max_wage = filters['wage_range']
        filtered_df = filtered_df[filtered_df['H_MEAN'].between(min_wage, max_wage, inclusive='both')]
        
    # 6. Filter by Search Query
    if 'search_query' in filters and filters['search_query'].strip() != '':
        query = filters['search_query'].lower().strip()
        # Search in occupation title or industry title or area title
        filtered_df = filtered_df[
            filtered_df['OCC_TITLE'].str.lower().str.contains(query, na=False) |
            filtered_df['NAICS_TITLE'].str.lower().str.contains(query, na=False) |
            filtered_df['AREA_TITLE'].str.lower().str.contains(query, na=False)
        ]
        
    return filtered_df
