import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set design system styling
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['axes.edgecolor'] = '#E5E7EB'
plt.rcParams['axes.labelcolor'] = '#1F2937'
plt.rcParams['text.color'] = '#1F2937'
plt.rcParams['xtick.color'] = '#4B5563'
plt.rcParams['ytick.color'] = '#4B5563'
plt.rcParams['grid.color'] = '#F3F4F6'

# Custom Color Palette
PALETTE = {
    'primary': '#2F6EB4',      # BLS Blue
    'secondary': '#1F6F4F',    # Deep Teal
    'accent': '#EA580C',       # Coral Orange
    'muted': '#6B7280',        # Slate Gray
    'light': '#F3F4F6',        # Light Gray
    'highlight': '#7C3AED',    # Indigo Purple
    'multi': ['#2F6EB4', '#1F6F4F', '#EA580C', '#7C3AED', '#0D9488', '#D97706', '#DB2777', '#2563EB']
}

def create_pie_chart(df):
    """1. Pie Chart: Proportional distribution of employment across Area Types."""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Group by area type name and sum employment
    emp_by_area = df.groupby('AREA_TYPE_NAME')['TOT_EMP'].sum().reset_index()
    # Drop rows with zero or NaN employment
    emp_by_area = emp_by_area[emp_by_area['TOT_EMP'] > 0]
    
    if emp_by_area.empty:
        ax.text(0.5, 0.5, "No Employment Data Available", ha='center', va='center', fontsize=12)
        ax.axis('off')
        return fig
        
    ax.pie(
        emp_by_area['TOT_EMP'],
        labels=emp_by_area['AREA_TYPE_NAME'],
        autopct='%1.1f%%',
        colors=PALETTE['multi'][:len(emp_by_area)],
        startangle=140,
        textprops={'fontsize': 9, 'color': '#1F2937'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5, 'antialiased': True}
    )
    
    ax.set_title("Employment Distribution by Area Type", fontsize=12, fontweight='bold', pad=15)
    return fig

def create_histogram(df):
    """2. Histogram: Frequency distribution of Average Hourly Wage (H_MEAN)."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    # Extract non-null wages
    wages = df['H_MEAN'].dropna()
    
    if wages.empty:
        ax.text(0.5, 0.5, "No Wage Data Available", ha='center', va='center', fontsize=12)
        return fig
        
    # Plot histogram with KDE
    sns.histplot(
        wages,
        bins=30,
        kde=True,
        ax=ax,
        color=PALETTE['primary'],
        edgecolor='white',
        line_kws={'linewidth': 2}
    )
    
    ax.set_title("Frequency Distribution of Average Hourly Wage", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Average Hourly Wage ($)", fontsize=10)
    ax.set_ylabel("Frequency (Count)", fontsize=10)
    return fig

def create_line_chart(df):
    """3. Line Chart: Wage percentiles trends over occupation categories."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    percentile_cols = ['H_PCT10', 'H_PCT25', 'H_MEDIAN', 'H_PCT75', 'H_PCT90']
    
    # Take a group average of percentiles for major occupation groups (excluding total)
    occ_groups = df[~df['O_GROUP'].isin(['total', 'Unknown'])].groupby('OCC_TITLE')[percentile_cols].mean().dropna()
    
    if occ_groups.empty or len(occ_groups) < 2:
        # Fallback: plot top 10 individual occupations by employment
        top_10 = df[df['OCC_TITLE'] != 'All Occupations'].nlargest(10, 'TOT_EMP')
        if top_10.empty:
            ax.text(0.5, 0.5, "No Wage Percentile Data Available", ha='center', va='center', fontsize=12)
            return fig
        occ_groups = top_10.set_index('OCC_TITLE')[percentile_cols]
        
    # Select top 7 occupations for readability in line plot
    occ_groups_top = occ_groups.head(7)
    
    # Transpose to have percentiles on X axis and occupations as lines
    plot_data = occ_groups_top.T
    
    # Clean x tick labels: H_PCT10 -> 10th, etc.
    x_labels = ['10th', '25th', 'Median', '75th', '90th']
    
    # Plot a line for each occupation
    for idx, col in enumerate(plot_data.columns):
        ax.plot(
            x_labels, 
            plot_data[col], 
            marker='o', 
            linewidth=2, 
            label=col[:30] + '...' if len(col) > 30 else col,
            color=PALETTE['multi'][idx % len(PALETTE['multi'])]
        )
        
    ax.set_title("Wage Percentile Hierarchy across Top Occupations", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Wage Percentile", fontsize=10)
    ax.set_ylabel("Hourly Wage ($)", fontsize=10)
    ax.legend(title="Occupation", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, title_fontsize=9)
    plt.tight_layout()
    return fig

def create_bar_chart(df):
    """4. Bar Chart: Compare average wages across Top 10 Occupations or Industries."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    # Get top 10 occupations by employment (excluding All Occupations)
    top_jobs = df[df['OCC_TITLE'] != 'All Occupations'].groupby('OCC_TITLE')['H_MEAN'].mean().reset_index()
    top_jobs = top_jobs.dropna().sort_values(by='H_MEAN', ascending=False).head(10)
    
    if top_jobs.empty:
        ax.text(0.5, 0.5, "No Data Available for Comparison", ha='center', va='center', fontsize=12)
        return fig
        
    sns.barplot(
        x='H_MEAN',
        y='OCC_TITLE',
        data=top_jobs,
        ax=ax,
        palette="viridis",
        hue='OCC_TITLE',
        legend=False
    )
    
    ax.set_title("Top 10 Highest Paying Occupations (Hourly Mean)", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Mean Hourly Wage ($)", fontsize=10)
    ax.set_ylabel("Occupation", fontsize=10)
    
    # Truncate long y labels
    labels = [text.get_text() for text in ax.get_yticklabels()]
    short_labels = [label[:35] + '...' if len(label) > 35 else label for label in labels]
    ax.set_yticklabels(short_labels, fontsize=9)
    plt.tight_layout()
    return fig

def create_scatter_plot(df):
    """5. Scatter Plot: Relationship between Total Employment (TOT_EMP) and Mean Hourly Wage (H_MEAN)."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    # Filter out All Occupations and nulls
    scatter_df = df[(df['OCC_TITLE'] != 'All Occupations') & (df['TOT_EMP'] > 0)].dropna(subset=['TOT_EMP', 'H_MEAN'])
    
    if scatter_df.empty:
        ax.text(0.5, 0.5, "No Employment/Wage Data Available", ha='center', va='center', fontsize=12)
        return fig
        
    # Sample if dataset is too large to keep plot clean
    if len(scatter_df) > 1000:
        scatter_df = scatter_df.sample(1000, random_state=42)
        
    sns.scatterplot(
        x='TOT_EMP',
        y='H_MEAN',
        data=scatter_df,
        alpha=0.6,
        color=PALETTE['secondary'],
        edgecolor=None,
        ax=ax
    )
    
    # Set logarithmic X axis since employment ranges from hundreds to millions
    ax.set_xscale('log')
    ax.set_title("Total Employment vs. Mean Hourly Wage", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Total Employment (Log Scale)", fontsize=10)
    ax.set_ylabel("Mean Hourly Wage ($)", fontsize=10)
    return fig

def create_box_plot(df):
    """6. Box Plot: Data spread, median, and outliers of Annual Wages by Area Type."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    box_df = df.dropna(subset=['A_MEAN'])
    
    if box_df.empty:
        ax.text(0.5, 0.5, "No Annual Wage Data Available", ha='center', va='center', fontsize=12)
        return fig
        
    sns.boxplot(
        x='AREA_TYPE_NAME',
        y='A_MEAN',
        data=box_df,
        palette=PALETTE['multi'][:len(box_df['AREA_TYPE_NAME'].unique())],
        ax=ax,
        hue='AREA_TYPE_NAME',
        legend=False
    )
    
    ax.set_title("Annual Wage Distribution by Area Type", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Area Type", fontsize=10)
    ax.set_ylabel("Annual Mean Wage ($)", fontsize=10)
    plt.xticks(rotation=15)
    plt.tight_layout()
    return fig

def create_heatmap(df):
    """7. Heatmap: Visualize correlation matrix of numerical features."""
    fig, ax = plt.subplots(figsize=(7, 5.5))
    
    corr_cols = [
        'TOT_EMP', 'H_MEAN', 'A_MEAN', 'LOC_QUOTIENT',
        'H_PCT10', 'H_PCT25', 'H_MEDIAN', 'H_PCT75', 'H_PCT90'
    ]
    
    # Filter columns that exist
    cols_to_use = [col for col in corr_cols if col in df.columns]
    
    corr_df = df[cols_to_use].corr()
    
    if corr_df.empty or corr_df.isna().all().all():
        ax.text(0.5, 0.5, "No Correlation Data Available", ha='center', va='center', fontsize=12)
        return fig
        
    sns.heatmap(
        corr_df,
        annot=True,
        cmap='coolwarm',
        fmt=".2f",
        linewidths=.5,
        ax=ax,
        vmin=-1,
        vmax=1,
        annot_kws={'size': 9}
    )
    
    ax.set_title("Correlation Matrix of Numeric Metrics", fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    return fig

def create_area_chart(df):
    """8. Area Chart: Cumulative employment trends over major categories or top groups."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    # Group by occupation group (major standard SOC groups) and get top 5
    top_groups = df[df['O_GROUP'] == 'major'].groupby('OCC_TITLE')['TOT_EMP'].sum().reset_index()
    top_groups = top_groups.nlargest(5, 'TOT_EMP')
    
    if top_groups.empty:
        # Fallback: group by area type
        top_groups = df.groupby('AREA_TYPE_NAME')['TOT_EMP'].sum().reset_index()
        
    if top_groups.empty or top_groups['TOT_EMP'].sum() == 0:
        ax.text(0.5, 0.5, "No Employment Data Available for Area Chart", ha='center', va='center', fontsize=12)
        return fig
        
    categories = top_groups['OCC_TITLE'].tolist() if 'OCC_TITLE' in top_groups.columns else top_groups['AREA_TYPE_NAME'].tolist()
    totals = top_groups['TOT_EMP'].tolist()
    
    # Shorten names for plotting
    cat_short = [cat[:25] + '...' if len(cat) > 25 else cat for cat in categories]
    
    # Draw cumulative area plot
    x = range(len(cat_short))
    cumulative = np.cumsum(totals)
    
    ax.fill_between(x, 0, cumulative, label="Cumulative", color=PALETTE['primary'], alpha=0.3)
    ax.plot(x, cumulative, color=PALETTE['primary'], marker='o', linewidth=2)
    
    # Plot individual area fills as stack
    bottom = np.zeros(len(cat_short))
    for idx, val in enumerate(totals):
        ax.fill_between([idx], bottom[idx], bottom[idx]+val, color=PALETTE['multi'][idx % len(PALETTE['multi'])], alpha=0.7, label=cat_short[idx])
        
    ax.set_xticks(x)
    ax.set_xticklabels(cat_short, rotation=25, ha='right', fontsize=9)
    ax.set_title("Cumulative Employment of Top Sectors", fontsize=12, fontweight='bold', pad=15)
    ax.set_ylabel("Cumulative Total Employment", fontsize=10)
    ax.legend(title="Sectors", fontsize=8, title_fontsize=9)
    plt.tight_layout()
    return fig

def create_count_plot(df):
    """9. Count Plot: Frequency count of records across Area Types."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    if df.empty:
        ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)
        return fig
        
    sns.countplot(
        x='AREA_TYPE_NAME',
        data=df,
        palette=PALETTE['multi'][:len(df['AREA_TYPE_NAME'].unique())],
        ax=ax,
        hue='AREA_TYPE_NAME',
        legend=False
    )
    
    ax.set_title("Number of Records by Area Type", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Area Type", fontsize=10)
    ax.set_ylabel("Record Count", fontsize=10)
    plt.xticks(rotation=15)
    plt.tight_layout()
    return fig

def create_violin_plot(df):
    """10. Violin Plot: Distribution and probability density of hourly wages by Area Type."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    violin_df = df.dropna(subset=['H_MEAN'])
    
    if violin_df.empty:
        ax.text(0.5, 0.5, "No Wage Data Available", ha='center', va='center', fontsize=12)
        return fig
        
    sns.violinplot(
        x='AREA_TYPE_NAME',
        y='H_MEAN',
        data=violin_df,
        palette=PALETTE['multi'][:len(violin_df['AREA_TYPE_NAME'].unique())],
        ax=ax,
        hue='AREA_TYPE_NAME',
        legend=False
    )
    
    ax.set_title("Wage Distribution & Probability Density by Area Type", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Area Type", fontsize=10)
    ax.set_ylabel("Mean Hourly Wage ($)", fontsize=10)
    plt.xticks(rotation=15)
    plt.tight_layout()
    return fig

def create_bubble_chart(df):
    """Bonus Chart: Bubble Chart of Average Wage vs Employment with Bubble Size representing Location Quotient."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Filter data with location quotients and non-zero values
    bubble_df = df[(df['OCC_TITLE'] != 'All Occupations') & (df['LOC_QUOTIENT'] > 0) & (df['TOT_EMP'] > 0)].dropna(subset=['TOT_EMP', 'H_MEAN', 'LOC_QUOTIENT'])
    
    if bubble_df.empty:
        ax.text(0.5, 0.5, "No Data for Bubble Chart", ha='center', va='center', fontsize=12)
        return fig
        
    # Sample to avoid heavy plots
    if len(bubble_df) > 500:
        bubble_df = bubble_df.sample(500, random_state=42)
        
    # Bubble size represents location quotient (scaled for plotting)
    sizes = bubble_df['LOC_QUOTIENT'] * 20
    
    scatter = ax.scatter(
        x=bubble_df['TOT_EMP'],
        y=bubble_df['H_MEAN'],
        s=sizes,
        alpha=0.6,
        c=bubble_df['LOC_QUOTIENT'],
        cmap='viridis',
        edgecolors='w',
        linewidths=0.5
    )
    
    ax.set_xscale('log')
    ax.set_title("Wage vs. Employment with Bubble Size as Location Quotient", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Total Employment (Log Scale)", fontsize=10)
    ax.set_ylabel("Mean Hourly Wage ($)", fontsize=10)
    
    # Legend for sizes
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='LQ = 1.0', markerfacecolor='#2F6EB4', markersize=5),
        plt.Line2D([0], [0], marker='o', color='w', label='LQ = 5.0', markerfacecolor='#2F6EB4', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='LQ = 10.0', markerfacecolor='#2F6EB4', markersize=15),
    ]
    ax.legend(handles=legend_elements, loc="upper left", title="Location Quotient (LQ)", fontsize=8, title_fontsize=9)
    fig.colorbar(scatter, ax=ax, label="Location Quotient")
    plt.tight_layout()
    return fig
