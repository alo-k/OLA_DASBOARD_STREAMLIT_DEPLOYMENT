import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="OLA Dashboard", layout="wide")

# =========================
# LOAD DATA (CSV ONLY)
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("ola_rides.csv")

df_all = load_data()

st.title("OLA Ride Analytics Dashboard")

# =========================
# SECTION SELECTOR
# =========================
section = st.radio(
    "Choose Section",
    [
        "SQL Dashboard",
        "EDA Analysis",
        "Streamlit Visualizations",
        "Power BI Dashboard (Screenshot)"
    ]
)
# =========================
# SQL DASHBOARD
# =========================
if section == "SQL Dashboard":

    queries = {
        "Q1. Successful Bookings": """
            SELECT * FROM ola_rides
            WHERE Booking_Status = 'Success';
        """,

        "Q2. Avg Ride Distance by Vehicle Type": """
            SELECT Vehicle_Type, AVG(Ride_Distance) AS Avg_Ride_Distance
            FROM ola_rides
            GROUP BY Vehicle_Type;
        """,

        "Q3. Total Cancellations by Customer": """
            SELECT COUNT(*) AS Total_Rides_Canceled_By_Customer
            FROM ola_rides
            WHERE Booking_Status = 'Canceled by Customer';
        """,

        "Q4. Top 5 Customers by Rides": """
            SELECT TOP 5 Customer_ID, COUNT(*) AS Total_Rides
            FROM ola_rides
            GROUP BY Customer_ID
            ORDER BY Total_Rides DESC;
        """,
                "Q5. Driver Cancellations (Personal/Car Issues)": """
        SELECT COUNT(*) AS No_Of_Rides_Canceled_By_Driver
        FROM ola_rides
        WHERE Booking_Status = 'Canceled by Driver'
        AND Canceled_Rides_by_Driver = 'Personal & Car related issue';
        """,

        "Q6. Max & Min Driver Rating (Prime Sedan)": """
        SELECT Vehicle_Type,
               MAX(Driver_Ratings) AS Max_Driver_Rating,
               MIN(Driver_Ratings) AS Min_Driver_Rating
        FROM ola_rides
        WHERE Vehicle_Type = 'Prime Sedan'
        GROUP BY Vehicle_Type;
        """,

        "Q7. Rides Paid Using UPI": """
        SELECT *
        FROM ola_rides
        WHERE Payment_Method = 'UPI';
        """,

        "Q8. Avg Customer Rating by Vehicle Type": """
        SELECT Vehicle_Type,
               AVG(Customer_Rating) AS Avg_Customer_Rating
        FROM ola_rides
        WHERE Customer_Rating IS NOT NULL
        GROUP BY Vehicle_Type;
        """,

        "Q9. Total Booking Value (Successful Rides)": """
        SELECT SUM(Booking_Value) AS Total_Booking_Value
        FROM ola_rides
        WHERE Booking_Status = 'Success';
        """,

        "Q10. Incomplete Rides with Reason": """
        SELECT Booking_ID, Vehicle_Type,
               Incomplete_Rides, Incomplete_Rides_Reason
        FROM ola_rides
        WHERE Incomplete_Rides = 'Yes';
        """
        }
    question = st.selectbox("Select a Question", queries.keys())

    st.subheader("SQL Query")
    st.code(queries[question], language="sql")

    df = df_all.copy()

    st.subheader("Query Result")
    st.dataframe(df)

# =========================
# EDA SECTION
# =========================
if section == "EDA Analysis":

    st.subheader("Exploratory Data Analysis (Done in Jupyter)")

    df = df_all.copy()

    st.markdown("### Data Preview")
    st.code("df.head()")
    st.dataframe(df.head())

    st.markdown("### Dataset Shape")
    st.write("Rows:", df.shape[0])
    st.write("Columns:", df.shape[1])

    st.markdown("### Missing Values")
    st.code("df.isnull().sum()")
    st.dataframe(df.isnull().sum())

    st.markdown("### Summary Statistics")
    st.code("df.describe()")
    st.dataframe(df.describe())

    st.markdown("### Booking Status Count")
    st.code("df['Booking_Status'].value_counts()")
    st.dataframe(df["Booking_Status"].value_counts())

    st.markdown("### Vehicle Type Distribution")
    st.code("df['Vehicle_Type'].value_counts()")
    st.dataframe(df["Vehicle_Type"].value_counts())

    st.markdown("### Payment Method Distribution")
    st.code("df['Payment_Method'].value_counts()")
    st.dataframe(df["Payment_Method"].value_counts())

    st.markdown("### Booking Status Breakdown")
    st.code("df['Booking_Status'].value_counts(normalize=True)")
    st.dataframe(
    df["Booking_Status"].value_counts(normalize=True).rename("Percentage")
    )

    st.markdown("### Customer Rating Distribution")
    st.code("df['Customer_Rating'].describe()")
    st.dataframe(df["Customer_Rating"].describe())

    st.markdown("### Driver Rating Distribution")
    st.code("df['Driver_Ratings'].describe()")
    st.dataframe(df["Driver_Ratings"].describe())

    st.markdown("### Avg Ratings by Vehicle Type")
    rating_df = df.groupby("Vehicle_Type")[["Customer_Rating", "Driver_Ratings"]].mean()
    st.dataframe(rating_df)

    st.markdown("### Ride Distance Analysis")
    st.code("df['Ride_Distance'].describe()")
    st.dataframe(df["Ride_Distance"].describe())

    st.markdown("### Booking Value Analysis")
    st.code("df['Booking_Value'].describe()")
    st.dataframe(df["Booking_Value"].describe())

    st.markdown("### Correlation Analysis (Numeric Features)")
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    st.dataframe(numeric_df.corr())

    st.markdown("## Key EDA Insights")
    st.markdown("""
    - Prime Sedan rides have higher average booking value and ratings.
    - Majority of cancellations come from customer-side actions.
    - UPI and Cash dominate payment methods.
    - Longer ride distances correlate with higher booking value.
    """)

# =========================
# STREAMLIT VERSION POWER BI SECTION
# =========================
if section == "Streamlit Visualizations":
    st.subheader("Power BI Style Dashboard")
    df = df_all.copy()
    
    # -------- KPI CARDS --------
    st.markdown("### Key Metrics")
    total_rides = df_all.shape[0]
    total_revenue = df_all["Booking_Value"].sum()
    avg_fare = df_all["Booking_Value"].mean()
    avg_distance = df_all["Ride_Distance"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rides", total_rides)
    col2.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    col3.metric("Avg Fare", f"₹{avg_fare:.2f}")
    col4.metric("Avg Distance (km)", f"{avg_distance:.2f}")

    # --- Ride Volume Over Time ---
    df_all['Date'] = pd.to_datetime(df_all['Date'])
    df_all['Date'] = pd.to_datetime(df_all['Date'])
    ride_volume_daily = (
    df_all.groupby(df_all['Date'].dt.date)['Booking_ID']
    .count()
    .reset_index()
    )
    ride_volume_daily.rename(
    columns={'Booking_ID': 'Ride Volume'},
    inplace=True
    )
    fig = px.line(
    ride_volume_daily,
    x='Date',
    y='Ride Volume',
    title='Ride Volume Over Time'
    )
    fig.update_traces(
    line=dict(color='yellow', width=3),
    mode='lines'   # 🔥 PURE LINE
    )
    fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Number of Rides',
    template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Bookng Status Breakdown ---
    status_counts = df_all.groupby('Booking_Status')['Booking_ID'].count().reset_index()
    status_counts.rename(columns={'Booking_ID': 'Count'}, inplace=True)

    # --- Donut Chart ---
    fig = px.pie(
    status_counts,
    names='Booking_Status',
    values='Count',
    title='Booking Status Breakdown',
    hole=0.5,  # makes it a donut chart
    color_discrete_sequence=px.colors.qualitative.Pastel  # optional: nice pastel colors
    )

    fig.update_traces(
    textposition='inside', 
    textinfo='percent+label'  # shows both % and label inside the slices
    )

    fig.update_layout(
    template='plotly_white',
    legend_title_text='Booking Status'
    )

    # --- Display in Streamlit ---
    st.plotly_chart(fig, use_container_width=True)

    # --- Avg Customer Rating By Vehicle Type ---
    avg_rating = df_all.groupby('Vehicle_Type')['Customer_Rating'].mean().reset_index()
    avg_rating.rename(columns={'Customer_Rating': 'Average Rating'}, inplace=True)

    # --- Bar Chart ---
    fig = px.bar(
    avg_rating,
    x='Vehicle_Type',
    y='Average Rating',
    title='Average Customer Rating by Vehicle Type',
    text='Average Rating',  # shows values on top of bars
    color='Average Rating',  # optional: color bars based on value
    color_continuous_scale='Viridis'  # gradient color scale
    )

    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')  # format values
    fig.update_layout(
    xaxis_title='Vehicle Type',
    yaxis_title='Average Customer Rating',
    template='plotly_white'
    )

    # --- Display in Streamlit ---
    st.plotly_chart(fig, use_container_width=True)

    # --- Top 5 Vehicle_Type By Ride Diatance ---
    # --- Aggregate total ride distance by vehicle type ---
    vehicle_distance = (
    df_all.groupby('Vehicle_Type')['Ride_Distance']
    .sum()
    .reset_index()
)

    # --- Get Top 5 vehicle types ---
    top_5_vehicle_distance = vehicle_distance.sort_values(
    by='Ride_Distance',
    ascending=False
    ).head(5)

    # --- Bar Chart ---
    fig = px.bar(
    top_5_vehicle_distance,
    x='Vehicle_Type',
    y='Ride_Distance',
    title='Top 5 Vehicle Types by Ride Distance',
    text='Ride_Distance',
    color='Ride_Distance',
    color_continuous_scale='YlOrRd'  # yellow → orange → red
    )

    # --- Styling ---
    fig.update_traces(
    texttemplate='%{text:.0f}',
    textposition='outside'
    )

    fig.update_layout(
    xaxis_title='Vehicle Type',
    yaxis_title='Total Ride Distance',
    template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    #--- Revenue By Payment Method ---
    # --- Aggregate revenue by payment method ---
    revenue_payment = (
    df_all.groupby('Payment_Method')['Booking_Value']
    .sum()
    .reset_index()
    )

    revenue_payment.rename(
    columns={'Booking_Value': 'Total Revenue'},
    inplace=True
    )

    fig = px.pie(
    revenue_payment,
    names='Payment_Method',
    values='Total Revenue',
    title='Revenue by Payment Method',
    hole=0.5,
    color='Payment_Method',
    color_discrete_map={
        'UPI': '#2ECC71',     # green
        'Cash': '#F39C12',    # orange
        'Card': '#F1C40F'     # yellow
    }
    )
    fig.update_traces(
    textinfo='percent+label',
    hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}'
    )
    fig.update_layout(
    template='plotly_dark',
    legend_title='Payment Method'
    )
    st.plotly_chart(fig, use_container_width=True)

    #--- Top 5 Customer By Booking Value ---
    # --- Aggregate total booking value by customer ---
    customer_revenue = (
    df_all.groupby('Customer_ID')['Booking_Value']
    .sum()
    .reset_index()
    )
    customer_revenue.rename(
    columns={'Booking_Value': 'Total Booking Value'},
    inplace=True
    )   

    # --- Get Top 5 customers ---
    top_5_customers = customer_revenue.sort_values(
    by='Total Booking Value',
    ascending=False
    ).head(5)

    top_5_customers['Customer_ID'] = top_5_customers['Customer_ID'].astype(str)
    # --- Column Chart ---
    fig = px.bar(
    top_5_customers,
    x='Customer_ID',
    y='Total Booking Value',
    title='Top 5 Customers by Booking Value',
    text='Total Booking Value',
    color='Total Booking Value',
    color_continuous_scale='YlOrBr'
    )

    # --- Styling ---
    fig.update_traces(
    texttemplate='₹%{text:,.0f}',
    textposition='outside'
    )

    fig.update_layout(
    xaxis_title='Customer ID',
    yaxis_title='Total Booking Value',
    template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    #--- Ride Distance Distribution Per Day ---
     # --- Aggregate total ride distance per day ---
    daily_distance = (
    df_all.groupby(df_all['Date'].dt.date)['Ride_Distance']
    .sum()
    .reset_index()
    )

    daily_distance.rename(columns={'Ride_Distance': 'Total Ride Distance'}, inplace=True)

    # --- Line Chart (pure line, no area) ---
    fig = px.line(
    daily_distance,
    x='Date',
    y='Total Ride Distance',
    title='Ride Distance Distribution Per Day'
    )

    # --- Styling ---
    fig.update_traces(
    line=dict(color='yellow', width=3),
    mode='lines'   # ensures pure line (no markers)
    )

    fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Ride Distance',
    template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    #--- Cancel Rides Driver Vs Customer ---
    customer_cancellations = df_all['Canceled_Rides_by_Customer'].notna().sum()
    driver_cancellations = df_all['Canceled_Rides_by_Driver'].notna().sum()

    cancel_data = pd.DataFrame({
    'Cancelled By': ['Customer', 'Driver'],
    'Count': [customer_cancellations, driver_cancellations]
    })

    fig = px.pie(
    cancel_data,
    names='Cancelled By',
    values='Count',
    title='Cancelled Rides: Driver vs Customer',
    hole=0.5,
    color='Cancelled By',
    color_discrete_map={
        'Customer': '#FF6B6B',
        'Driver': '#FFD93D'
    }
    )

    fig.update_traces(
    textinfo='percent+label',
    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}'
    )

    fig.update_layout(
    template='plotly_dark',
    legend_title='Cancelled By'
    )
    st.plotly_chart(fig, width='stretch')

    #--- Driver Vs Customer Rating---

    # --- Calculate averages ---
    avg_customer_rating = df_all['Customer_Rating'].mean()
    avg_driver_rating = df_all['Driver_Ratings'].mean()

    # --- Prepare data ---
    rating_df = pd.DataFrame({
    'Rating Type': ['Customer Rating', 'Driver Rating'],
    'Average Rating': [avg_customer_rating, avg_driver_rating]
    })
    # --- Stacked / Comparison Bar Chart ---
    fig = px.bar(
    rating_df,
    x='Rating Type',
    y='Average Rating',
    title='Driver Rating vs Customer Rating',
    color='Rating Type',
    color_discrete_map={
        'Customer Rating': '#FFD93D',  # yellow
        'Driver Rating': '#4CAF50'     # green
    }
    )
    # --- Styling ---
    fig.update_layout(
    template='plotly_dark',
    yaxis_title='Average Rating',
    xaxis_title='',
    showlegend=False
    )
    fig.update_traces(
    texttemplate='%{y:.3f}',
    textposition='outside'
    )
    st.plotly_chart(fig, width='stretch')


    # --- Driver Rating Distribution ---
   # Count of Booking_ID per Driver_Ratings
    driver_rating_dist = (
    df_all
    .groupby('Driver_Ratings')['Booking_ID']
    .count()
    .reset_index()
    .rename(columns={'Booking_ID': 'Booking Count'})
    )
    # --- Column Chart ---
    fig = px.bar(
    driver_rating_dist,
    x='Driver_Ratings',
    y='Booking Count',
    title='Driver Rating Distribution',
    color='Driver_Ratings',
    color_continuous_scale='YlOrBr'
    )
    # --- Styling ---
    fig.update_layout(
    template='plotly_dark',
    xaxis_title='Driver Ratings',
    yaxis_title='Count of Booking ID',
    bargap=0.15
    )
    fig.update_traces(
    texttemplate='%{y}',
    textposition='outside'
    )
    st.plotly_chart(fig, width='stretch')

if section == "Power BI Dashboard (Screenshot)":
    st.subheader("📊 Power BI Dashboard")
    st.markdown(
        """
        This dashboard was originally built in **Power BI**.  
        Due to Power BI Premium limitations, a screenshot version is displayed here.
        """
    )
    st.image(
        "Power Bi Screenshot.png",
        caption="Power BI Dashboard Snapshot",
        width='stretch'
    )
        

