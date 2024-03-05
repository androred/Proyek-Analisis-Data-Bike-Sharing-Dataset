import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Average Daily Bike Rentals
average_daily_rentals = all_df['cnt'].mean()
st.subheader("Average Daily Bike Rentals")
st.write(f"The average daily bike rentals is approximately {average_daily_rentals:.2f} bikes.")

# Find the Season with the Most Bike Rentals
most_rented_season = season_df.groupby('season')['cnt'].sum().idxmax()
season_label = ["Spring", "Summer", "Fall", "Winter"]
st.subheader("Season with the Most Bike Rentals")
st.write(f"The season with the most bike rentals is {season_label[most_rented_season-1]}.")

# Visualization Bike Renters by Season in 2012
st.subheader("Number of Bike Renters by Season in 2012")
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
for p in ax.patches:
    ax.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
st.pyplot(fig)
