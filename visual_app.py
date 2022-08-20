#!/usr/bin/env python
# coding: utf-8

# Import modules
import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(page_title="Managed Charging Enrollment Demo",
                   layout="wide",
                   initial_sidebar_state="auto",
                   page_icon=":battery:")

# Load Enrollment Data
@st.experimental_singleton
def load_data():
    # Read in latest enrollment data from SDV team
    df = pd.read_csv("enrollments.csv")
    
    # Remove users that failed to enroll
    df = df[df["utility_status"] != "Failed"].reset_index(drop=True)
    
    # Extract out lat/lon for each enrolled user
    df["_home_location"] = df["_home_location"].astype(str)
    df = df[df["_home_location"] != "nan"].reset_index(drop=True)
    df["_home_location"] = df["_home_location"].str[1:-1]
    df[["lat", "lon"]] = df["_home_location"].str.split(",", 2, expand=True)
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    
    # Aggregate the number of enrollments at each lat/lon coordinate
    df["enrollments"] = 1
    df = df.groupby(["utility_code", "lat", "lon"]).sum().reset_index()
    
    # Subset out the desired columns
    df = df[["utility_code", "lat", "lon", "enrollments"]]

    # Rename the columns
    df.columns = ["Utility", "Latitude", "Longitude", "Enrollments"]
    
    return df


# Function for Utility Enrollment Map
def map(zoom, data, lat, lon, color):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 0,
                "bearing": 0
            },
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data,
                    pickable=True,
                    opacity=0.5,
                    stroked=True,
                    filled=True,
                    radius_scale=10,
                    radius_min_pixels=1,
                    radius_max_pixels=100,
                    line_width_min_pixels=1,
                    get_position=["Longitude", "Latitude"],
                    get_radius="Enrollments",
                    get_fill_color=color,
                    get_line_color=[0, 0, 0]
                ),
            ],
        )
    )


# Filter the Data for a Specific Utility
@st.experimental_memo
def filterdata(df, utility):
    if utility == "DTE":
        data = df[df["Utility"] == "dte"].reset_index(drop=True)
    elif utility == "National Grid":
        data = df[df["Utility"] == "nationalgrid"].reset_index(drop=True)
    elif utility == "Xcel Energy":
        data = df[df["Utility"] == "xcel"].reset_index(drop=True)
    else:
        data = df
    return data

# Aggregate the Number of Enrollments
@st.experimental_memo
def countusers(data):
    data["Enrolled Users"] = 1
    data = data.groupby(["Utility"]).sum().reset_index()
    data = data[["Utility", "Enrolled Users"]]
    return data

# Aggregate the Number of Monthly Enrollments by Utilities
@st.experimental_memo
def monthlyusers():
    # Read in latest enrollment data from SDV team
    df = pd.read_csv("enrollments.csv")
    
    # Remove users that failed to enroll
    df = df[df["utility_status"] != "Failed"].reset_index(drop=True)
    
    # Get the enrollment month
    df["utility_status_date"] = pd.to_datetime(df["utility_status_date"], utc=True)
    df["month"] = df["utility_status_date"].dt.date
    df["month"] = df["month"].astype(str)
    df["month"] = df["month"].str[:7]
    
    # Subset desired columns
    df = df[["month", "utility_code"]]
    
    # Count number of enrollments
    df["Enrollments"] = 1
    df = df.groupby(["month", "utility_code"]).sum().reset_index()
    df["Enrollments"] = df["Enrollments"].astype(int)
    
    # Rename the columns
    df.columns = ["Month", "Utility", "Enrollments"]
    
    # Rename the utilities
    df.loc[df["Utility"] == "dte", "Utility"] = "DTE"
    df.loc[df["Utility"] == "nationalgrid", "Utility"] = "National Grid"
    df.loc[df["Utility"] == "xcel", "Utility"] = "Xcel Energy"
    
    return df

# Read in data for the number of enrolled vs not enrolled GM vehicles
@st.experimental_memo
def enrollments():
    # Read in total vehicular enrollments data
    df = pd.read_csv("total_vins.csv")
    
    return df

# Read in data for average hourly cost of electricity for Xcel
def electricityRates():
    # Read in total vehicular enrollments data
    df = pd.read_csv("electricity_costs_xcel.csv")
    
    return df

# Create a Matplotlib bar chart of monthly enrollments
def barplot(df):

    # Create the axis and subplot
    fig, ax = plt.subplots(figsize=(10, 3))
    
    # Plot the monthly enrollment data
    df.plot(kind="bar", stacked=True, color=["#00FF00", "#FF0000", "#0000FF"], ax=ax)
    
    # Add the chart title
    plt.title("Monthly Enrollment by Utility", fontsize=20)
    
    # Add axis titles
    plt.xlabel("Month", fontsize=15)
    plt.ylabel("Enrollments", fontsize=15)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)
    
    return fig

    
# Streamlit App Layout

# Title
st.title("""V1G Managed Charging Program""")

# App Summary
st.write(
    """
        Examine the distribution of GM electric vehicle owners enrolled in the V1G Managed Charging Program.
        Enrolled users who elect to have their vehicle's charge times managed by General Motors received
        discounted electricity pricing rates.
    """
)

# Get Enrollment Data
data = load_data()

# See if there is a utility already selected
if not st.session_state.get("url_synced", False):
    try:
        utility = st.experimental_get_query_params()["utility"][0]
        st.session_state["utility"] = utility
        st.session_state["url_synced"] = True
    except KeyError:
        pass

# If the drop Down selection changes, update the query parameter
def update_query_params():
    utility_selected = st.session_state["utility"]
    st.experimental_set_query_params(utility=utility_selected)

st.header("""Vehicle Enrollments by Utility""")

# Layout the number of Rows/Columns for the next portion of the App
row1_1, row1_2 = st.columns((1, 3))

with row1_1:
    utility_selected = st.selectbox(
        "Select Utility", ("Show All", "DTE", "National Grid", "Xcel Energy")
    )
    st.header("""""")
    st.header("""""")
    st.header("""""")
    st.header("""""")
    st.header("""""")
    st.header("""""")
    st.write("Total Enrollments by Utility")
    st.dataframe(countusers(data))

# Filter data by utility
if utility_selected == "DTE":
    with row1_2:
        map_data = filterdata(data, utility_selected)
        latitude = map_data["Latitude"].mean()
        longitude = map_data["Longitude"].mean()
        map(8, map_data, latitude, longitude, [0, 255, 0])
elif utility_selected == "National Grid":
    with row1_2:
        map_data = filterdata(data, utility_selected)
        latitude = map_data["Latitude"].mean()
        longitude = map_data["Longitude"].mean()
        map(8, map_data, latitude, longitude, [255, 0, 0])
elif utility_selected == "Xcel Energy":
    with row1_2:
        map_data = filterdata(data, utility_selected)
        latitude = map_data["Latitude"].mean()
        longitude = map_data["Longitude"].mean()
        map(8, map_data, latitude, longitude, [0, 0, 255])
else:
    with row1_2:
        latitude = data["Latitude"].mean()
        longitude = data["Longitude"].mean()
        map(3, data, latitude, longitude, [255,255,0])


# Layout the bar chart showing monthly enrollments by Utility
row2_1, row2_2 = st.columns((2, 3))

# Get the monthly enrollment data by utility
monthly_enrollments = monthlyusers()

with row2_1:
    st.header("""""")
    st.header("""""")
    st.header("""""")
    table_data = pd.pivot_table(monthly_enrollments, values="Enrollments", index="Month", columns="Utility", aggfunc=np.sum, fill_value=0)
    st.dataframe(table_data)

with row2_2:
    st.header("""""")
    st.header("""""")
    st.altair_chart(
        alt.Chart(monthly_enrollments, title="Monthly Enrollments by Utility").mark_bar().encode(
            x="Month",
            y="sum(Enrollments)",
            tooltip=["Month", "Utility", "Enrollments"],
            color=alt.Color(field="Utility", type="nominal")
        ).properties(width=600)
    )

st.write(
    """
        DTE accounted for over 60% if enrolled vehicles despite only providing service to the greater Detroit, MI area.
        Many of the enrolled vehicles operating in the service areas covered by DTE are owned by GM employees. In its
        current pilot stage, vehicle owners must be invited by GM to participate in the program. As the program matures
        and moves out of the pilot stage, vehicle owners will be able to directly enroll with participating utilities.
    """
)

st.header("""Opportunities for Growth""")

# Layout the pie chart showing percentage of enrolled users vs number of GM EVs on the road
row3_1, row3_2, row3_3 = st.columns((2, 2, 2))

with row3_1:
    st.header("""""")
    st.altair_chart(
        alt.Chart(enrollments(), title="Vehicles Enrolled in Managed Charging").mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Percent of Vehicles", type="quantitative"),
            color=alt.Color(field="Vehicle Status", type="nominal"),
            tooltip=["Vehicle Status", "Percent of Vehicles", "Number of Vehicles"]
        )
    )

st.write (
    """
        The V1G Managed Charging Program is in its pilot stage. Currently, among the three utilities participating in the program,
        less than 1% of all GM electric vehicles operating in the service areas covered by these three utilities are enrolled in the
        program. This means there is exponential potential for growth as the program matures and moves beyond the pilot stage
    """
)

# Layout the row that show cases the average electriicty rates for Xcel for Enrolled and Non Enrolled Users

st.header("""Electricity Rates and Potential Savings for Xcel Energy Customers""")
hover = alt.selection_single(
    fields=["Hour"],
    nearest=True,
    on="mouseover",
    empty="none",
)
st.altair_chart(
    alt.Chart(electricityRates(), title="Average Q2 Xcel Energy Electricity Rates").mark_line(point="transparent").encode(
        x="Hour",
        y="Rate (¢/kWh)",
        color=alt.Color(field="Status", type="nominal"),
        tooltip=["Hour", "Status", "Rate (¢/kWh)"]
    ).properties(width=1000)
)
st.write(
    """
        For Q2 of 2022 (April - June), enrolled Xcel Energy customers were charged an average of 3.6 ¢/kWh for electricity
        compared to the 8.3 ¢/kWh non-enrolled customers were charged. This means that on average Xcel Energy customers enrolled
        in the managed charging program paid 57% less than non-enrolled customers when charging their electric vehicles at home.
    """
    )