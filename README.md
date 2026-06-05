# OEWS May 2025 Employment & Wage Dashboard

This is a professional-grade, interactive data visualization dashboard built for the **Exploratory Data Analysis** course project submission. 

- **Instructor:** Ali Hassan Sherazi
- **Submission Date:** 05-June-2026
- **Data Source:** Bureau of Labor Statistics (BLS) Occupational Employment and Wage Statistics (OEWS) May 2025 estimates

---

## 🛠️ Project Structure
The project code is organized strictly according to the submission folder guidelines:
```
/dashboard_project/
│
├── data/
│   └── all_data_M_2025.xlsx        # Standarized raw dataset (DO NOT RENAME)
│
├── notebooks/
│   └── analysis.ipynb              # Exploratory Data Analysis (EDA) notebook
│
├── app.py                          # Main Streamlit dashboard application file
├── charts.py                       # Matplotlib and Seaborn visualization functions
├── filters.py                      # Pandas data preprocessing, cleaning, and filtering logic
├── requirements.txt                # Required Python packages
└── README.md                       # Installation, execution, and insight documentation
```

---

## 🚀 Setup & Execution Instructions

This dashboard is built using Python 3.x and **Streamlit**. 

### 1. Prerequisites
Ensure you are using a Python environment (e.g., Anaconda or standard Python 3.x).

### 2. Install Dependencies
Open your terminal/command prompt, navigate to the project directory, and install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
Run the following command to start the Streamlit server and launch the interactive dashboard in your browser:
```bash
streamlit run app.py
```
If you are using Anaconda, you can run:
```bash
C:\Users\dell\anaconda3\python.exe -m streamlit run app.py
```

### ⚡ Automatic Caching & Performance Optimization
Because the dataset is extremely large (**413,528 rows**, ~80.6 MB Excel file), reading it directly from Excel in Pandas can take 1–2 minutes. 
To deliver a professional-grade user experience, this dashboard includes an **automatic data caching system**:
- On the **very first run**, the app loads the raw `data/all_data_M_2025.xlsx` file, cleans it, and automatically saves a cleaned version to `data/all_data_M_2025_clean.csv`.
- On all **subsequent runs**, the app loads the cleaned CSV cache directly, reducing startup time to **under 2 seconds**.
- The original Excel file remains completely untouched.

---

## 📊 Technical Features Flipped & Covered

### 1. Data Cleaning & Preprocessing (`filters.py`)
- Standardizes columns and maps numeric Area Type codes (`1`, `2`, `3`, `4`, `6`) to descriptive labels.
- Safely cleans and parses text placeholder values used by the BLS (e.g., `*`, `**`, `#`, `~`) into numeric values (`float`), ensuring calculations are mathematically accurate.

### 2. Visualizations (`charts.py`)
Fulfills the mandatory requirement of creating the 10 required chart types plus a bonus visualization, using **Matplotlib** and **Seaborn** with professional layout styling and typography:
1. **Pie Chart**: Proportional distribution of total employment by Area Type.
2. **Histogram**: Frequency distribution of Average Hourly Wage.
3. **Line Chart**: Wage percentile hierarchies across top occupation categories.
4. **Bar Chart**: Comparison of the highest-paying occupations.
5. **Scatter Plot**: Correlation of total employment vs. mean hourly wage (sampled for performance).
6. **Box Plot**: Outliers and quartile ranges of annual wages by Area Type.
7. **Heatmap**: Correlation matrix of numerical variables.
8. **Area Chart**: Cumulative employment trend across top economic sectors.
9. **Count Plot**: Record frequency across different Area Types.
10. **Violin Plot**: Probability density and spread of hourly wages by Area Type.
- **Bonus Bubble Chart**: Wage vs. employment with bubble sizes representing location quotients.

### 3. Filters & Interactivity
The sidebar controls include:
- **Area Type category filter**
- **State selection** (multi-select)
- **Search filter** for keywords (matches occupations, industries, or areas)
- **Sliders** to filter ranges of total employment and hourly wages
- **Reset button** that restores all settings to default instantly

---

## 💡 Key Analysis Insights

1. **Employment-Wage Hierarchy**:
   There is a clear logarithmic inverse relationship between total employment and average wage. The highest-employment occupations are clustered in lower hourly wage brackets, whereas highly specialized roles have high hourly wages but represent a tiny fraction of total employment.
   
2. **Geographical Concentration (Location Quotient)**:
   By utilizing the location quotient (LQ), we can identify specific cities or states that are highly specialized in certain industries. For example, areas with LQ > 5.0 denote a massive density of specific occupations compared to the national average, indicating local industry hubs.
   
3. **Wage Dispersion by Area**:
   Metropolitan Areas (MSAs) exhibit a wider wage spread, higher medians, and a larger number of high-income outliers compared to Nonmetropolitan Areas, reflecting the concentration of corporate, scientific, and technical occupations in urban centers.
