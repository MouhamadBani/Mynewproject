import requests
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

# Step 1: Fetch Financial Data from World Bank API
def fetch_world_bank_data():
    countries = "AGO;BDI;BEN;BFA;BWA;CAF;CIV;CMR;COD;COG;COM;CPV;DJI;DZA;EGY;ERI;ETH;GAB;GHA;GIN;GMB;GNB;GNQ;KEN;LBR;LBY;LSO;MAR;MDG;MLI;MOZ;MRT;MUS;MWI;NAM;NER;NGA;RWA;SDN;SEN;SLE;SOM;STP;SWZ;TCD;TGO;TUN;TZA;UGA;ZAF;ZMB;ZWE"
    indicators = ["FX.OWN.TOTL.ZS", "NY.GDP.PCAP.CD", "FP.CPI.TOTL.ZG", "BX.KLT.DINV.CD.WD"]
    
    financial_data = []
    for indicator in indicators:
        url = f"https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}?format=json&per_page=100"
        response = requests.get(url)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 1:
            records = data[1]
            for record in records:
                if record["value"] is not None:
                    financial_data.append({
                        "Country": record["country"]["value"],
                        "Year": int(record["date"]),
                        "Indicator": record["indicator"]["id"],
                        "Value": record["value"]
                    })
    return pd.DataFrame(financial_data)

# Step 2: Store Data in SQLite Database
def store_data_in_sql(df):
    conn = sqlite3.connect("africa_finance.db")
    df.to_sql("FinancialData", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

# Step 3: Build Interactive Dashboard with Streamlit
def build_dashboard(df):
    st.set_page_config(layout="wide")
    st.title("🌍 African Financial Inclusion & Economic Dashboard")
    
    available_countries = df["Country"].unique().tolist()
    default_countries = [c for c in ["Nigeria", "Kenya", "South Africa"] if c in available_countries]
    selected_countries = st.multiselect("Select Countries", available_countries, default=default_countries)
    df_filtered = df[df["Country"].isin(selected_countries)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Financial Trends")
        if not df_filtered.empty:
            st.line_chart(df_filtered.pivot(index="Year", columns="Indicator", values="Value"))
        else:
            st.write("No data available for selected countries.")
    
    with col2:
        st.subheader("📊 Statistical Overview")
        if not df_filtered.empty:
            st.write(df_filtered.groupby("Country")["Value"].describe())
        else:
            st.write("No statistics available for selected countries.")
    
    st.subheader("💡 GDP vs Financial Inclusion Comparison")
    if not df_filtered.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.scatterplot(data=df_filtered, x="Year", y="Value", hue="Country", style="Indicator", ax=ax)
        plt.xlabel("Year")
        plt.ylabel("Financial Metric Value")
        plt.title("Financial Indicators Trends in Africa")
        st.pyplot(fig)
    else:
        st.write("No data available for visualization.")
    
    st.subheader("🔍 Country-Specific Data Insights")
    if available_countries:
        country_selected = st.selectbox("Select a country for detailed analysis", available_countries)
        df_country = df[df["Country"] == country_selected]
        if not df_country.empty:
            st.write(df_country.pivot(index="Year", columns="Indicator", values="Value"))
        else:
            st.write("No data available for this country.")
    else:
        st.write("No countries available in the dataset.")

# Run Full Pipeline
def main():
    df = fetch_world_bank_data()
    store_data_in_sql(df)
    build_dashboard(df)

if __name__ == "__main__":
    main()
