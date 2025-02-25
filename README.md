# UST Yield Curve Analysis

## 📌 Project Overview
This project is part of the broader **UST Yield Curve Analysis** repository, which aims to update the **classic method of fitting yield curves using CRSP monthly bonds data**. The original research was conducted by **Coleman, Ibbotson, and Fisher**, and our goal is to refine their methodology for yield curve estimation and market dynamics analysis.

This specific module **compares different forward rate curve models** by processing `.pkl` output files and generating:  
- **Monthly yield curve comparison plots** for specific `quotedate`s (**display_comparison.py**).  
- **Time series visualizations** of different maturities, including **static images & interactive windows** (**timeseries.py**).  

These scripts call functions from `discfact.py` and `DateFunctions_1.py` to ensure accurate discount factor calculations and date handling.

---

## 📂 File Structure
```
UST_YieldCurve_Analysis/
│── output/                 # Stores all generated results
│   ├── merge/              # Merged datasets for curve comparison
│   ├── comparison_plots/   # Monthly yield curve comparison images
│   ├── time_series/        # Static and interactive time series
│── src/                    # Source code
│   ├── display_comparison.py  # Generates comparison yield curve plots
│   ├── timeseries.py          # Generates time series visualizations
│   ├── discfact.py            # Discount factor calculations
│   ├── DateFunctions_1.py     # Date processing functions
│── data/                   # Input datasets
│   ├── CRSP_bonds_data/     # Raw bond yield data
│   ├── processed_pkl/       # Computed forward curves in .pkl format
│── README.md               # Project documentation
```

---

## ⚙️ How to Generate Output
### **1️⃣ Merging & Preparing Data**
- **display_comparison.py** loads `.pkl` results from Python & Fortran curve models.
- Adds identifiers for different models (`pwcf`, `pwtf`) and merges the datasets.
- Saves the combined dataset in `output/merge/merge.pkl` and `merge.csv`.

### **2️⃣ Generating Yield Curve Comparisons**
- **display_comparison.py** reads `merge.pkl`, selects specific `quotedate`s, and:
  - Plots monthly forward curves.
  - Saves images in `output/comparison_plots/`.

### **3️⃣ Time Series Visualization**
- **timeseries.py** generates static & interactive time series plots:
  - **Static plots**: Different maturities over time (e.g., 10YR, 30YR) → saved in `output/time_series/*.png`.
  - **Interactive HTML visualization**: Multi-maturity time series with a slider → saved as `output/time_series/*.html`.

---

## 🌍 Hosting Interactive Time Series Visualization
- [Access the interactive window here](https://xiaoxiguazi.github.io/UST_YieldCurve_Analysis/parbd_rate.html)
