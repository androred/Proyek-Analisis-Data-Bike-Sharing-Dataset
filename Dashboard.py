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
st.header("Dashboard Bike Rent")

# Create Sidebar
with st.sidebar:
    st.sidebar.header("About")
    st.sidebar.write("This dashboard was created to answer business questions about the number of bike rentals per day and the season that has the most bike rentals. The data is taken from the Bike Sharing Dataset. The dataset contains 731 rows and 16 columns. The columns include the date, season, year, month, holiday, weekday, workingday, weather, temperature, humidity, windspeed, and the number of bike rented. The dataset is taken from the UCI Machine Learning Repository.")
    st.sidebar.caption("Created by: Akhbarrr")

st.subheader("Number of Bike Renters by Day") 
average_cnt = dayly_df["cnt"].mean()
fig, ax = plt.subplots(figsize=(15, 10))

sns.barplot(
    y="cnt",
    x="dteday",
    hue="dteday",
    data=dayly_df,
    palette="viridis",
    dodge=False,
    ax=ax
)

date_label = ["Day " + str(i * 60) for i in range(len(dayly_df) // 60 + 1)]
ax.set_xticks(range(0, len(dayly_df), 60))
ax.set_xticklabels(date_label)

ax.text(
    0.5, 0.95, f"Average cnt: {average_cnt:.2f}",
    horizontalalignment='center',
    verticalalignment='center',
    transform=ax.transAxes,
    fontsize=12,
    bbox=dict(facecolor='white', alpha=0.5)
)
ax.set_title("Bike Rented by Day", loc="center", fontsize=15)
ax.set_ylabel("Bike Rented")
ax.set_xlabel("Day")
ax.tick_params(axis="x", labelsize=10)
st.pyplot(fig)

st.subheader("Correlation Heatmap of Bike Sharing Dataset")
fig, ax = plt.subplots(figsize=(15, 10))

columns_for_correlation = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt']
day_new = data_df[columns_for_correlation]
correlation_matrix = day_new.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=1)


st.subheader("Number of Bike Renters by Season")
fig, ax = plt.subplots(figsize=(15, 10))
sns.barplot(
    y="cnt",
    x="season",
    hue=["Spring", "Summer", "Fall", "Winter"],
    data=season_df,
    palette="viridis",
    dodge=False,
    ax=ax
)
season_label = ["Spring", "Summer", "Fall", "Winter"]
ax.set_xticks(range(len(season_label)), labels=season_label)
ax.set_title("Bike Rented by Season", loc="center", fontsize=15)
ax.set_ylabel("Bike Rented")
ax.set_xlabel("Season")
ax.tick_params(axis="x", labelsize=10)
for x in ax.patches:
    ax.annotate(f'{x.get_height():.0f}', (x.get_x() + x.get_width() / 2., x.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
st.pyplot(fig)


st.subheader("Analyzes the relationship between season and count of bike rental")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

sns.barplot(
    x='season', 
    y='cnt', 
    hue=["Spring", "Summer", "Fall", "Winter"], 
    data=season_df, 
    palette='Paired', 
    ax=ax1)
ax1.set_title("Relationship Between Season and Count")
for p in ax1.patches:
    ax1.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')

sns.barplot(
    x='season', 
    y='cnt', 
    hue=["Spring", "Summer", "Fall", "Winter"], 
    data=season_df, 
    palette='Paired', 
    ax=ax2)
ax2.set_title("Relationship Between Season and Count with Year Hue")
for p in ax2.patches:
    ax2.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
st.pyplot(fig)

st.subheader("Conclusion")
st.write("Rata-rata penyewaan terjadi setiap harinya diangka 4000 - 5000 penyewa. Penyewaan yang paling banyak terjadi dengan parameter musim yaitu pada musim Gugur atau musim 3")
