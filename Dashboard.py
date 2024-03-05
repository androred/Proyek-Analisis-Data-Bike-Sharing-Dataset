import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_season_df(day_df):
    season_df = day_df.groupby(["season"])["cnt"].sum().reset_index()
    return season_df

def create_dayly_df(day_df):
    dayly_df = day_df.groupby(["dteday"])["cnt"].sum().reset_index()
    return dayly_df 
    
data_df = pd.read_csv("https://raw.githubusercontent.com/androred/Proyek-Analisis-Data-Bike-Sharing-Dataset/main/Data/day.csv")

season_df = create_season_df(data_df)
dayly_df = create_dayly_df(data_df)


#create header
st.header("** Dashboard Bike Rent** ")

# Create Sidebar
with st.sidebar:
    st.sidebar.header("About")
    st.sidebar.write("This dashboard was created to answer business questions about the number of bike rentals per day and the season that has the most bike rentals. The data is taken from the Bike Sharing Dataset. The dataset contains 731 rows and 16 columns. The columns include the date, season, year, month, holiday, weekday, workingday, weather, temperature, humidity, windspeed, and the number of bike rented. The dataset is taken from the UCI Machine Learning Repository.")
    st.sidebar.caption("Created by: Akhbarrr")

st.subheader("Number of Bike Renters by Season")
fig, ax = plt.subplots(figsize=(15, 10))
data_2012 = season_df[season_df["yr"]==1] 
ax = sns.barplot(
    y="cnt", 
    x="season",
    hue="season",
    data=data_2012,
    palette="viridis",
    dodge=False,  
    legend=False,
    ax=ax
)
season_label = ["Spring", "Summer", "Fall", "Winter"]
ax.set_xticks(range(len(season_label)), labels=season_label)
ax.set_title("Bike Rented by Season in 2012", loc="center", fontsize=15)
ax.set_ylabel("Bike Rented")
ax.set_xlabel("Season")
ax.tick_params(axis="x", labelsize=10)
for x in ax.patches:
    ax.annotate(f'{x.get_height():.0f}', (x.get_x() + x.get_width() / 2., x.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
st.pyplot(fig)
