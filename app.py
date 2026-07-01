import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(
    page_title="Aviation Analytics Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data Function ---
@st.cache_data
def load_data():
    csv_path = 'aviation_dataset.csv'
    if not os.path.exists(csv_path):
        st.error(f"Error: '{csv_path}' not found. Please run your data generation script first!")
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path)
    df['Departure_DateTime'] = pd.to_datetime(df['Departure_DateTime'], errors='coerce')
    df['Route'] = df['Origin'] + " ➔ " + df['Destination']
    # Calculate Load Factor
    df['Load_Factor_%'] = (df['Passenger_Count'] / df['Max_Capacity'] * 100).round(1)
    return df

df_raw = load_data()

if not df_raw.empty:
    # --- Sidebar Filters ---
    st.sidebar.header("🛸 Filter Options")
    
    # Origin Filter
    all_origins = sorted(df_raw['Origin'].unique())
    selected_origins = st.sidebar.multiselect("Select Origin Hubs", all_origins, default=all_origins)
    
    # Aircraft Type Filter
    all_aircraft = sorted(df_raw['Aircraft_Type'].unique())
    selected_aircraft = st.sidebar.multiselect("Select Aircraft Types", all_aircraft, default=all_aircraft)
    
    # Filter the dataframe based on selection
    df = df_raw[
        (df_raw['Origin'].isin(selected_origins)) & 
        (df_raw['Aircraft_Type'].isin(selected_aircraft))
    ]

    # --- Header ---
    st.title("✈️ Global Aviation Operations & Business Intelligence")
    st.markdown("An interactive EDA dashboard tracking fleet performance, financials, and sustainability metrics.")
    st.write("---")

    # --- Top Level Metrics (KPIs) ---
    total_flights = len(df)
    total_rev = df['Total_Revenue_USD'].sum()
    total_pax = df['Passenger_Count'].sum()
    
    # Calculate On-Time Performance %
    on_time_count = len(df[df['Flight_Status'] == 'On Time'])
    otp = (on_time_count / total_flights * 100) if total_flights > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Flights", f"{total_flights:,}")
    col2.metric("Gross Revenue", f"${total_rev:,.2f}")
    col3.metric("Total Passengers", f"{total_pax:,}")
    col4.metric("On-Time Performance (OTP)", f"{otp:.1f}%")

    st.write("---")

    # --- Tabbed Layout for EDA Operations ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⏱️ Operations & Delays", 
        "💰 Financial Performance", 
        "🌱 Fleet & Sustainability", 
        "📈 Time-Series Trends", 
        "⭐ Customer Satisfaction"
    ])

    # --- Tab 1: Operations & Delays ---
    with tab1:
        st.subheader("Flight Status Breakdown & Delay Tracking")
        c1, c2 = st.columns(2)
        
        with c1:
            status_counts = df['Flight_Status'].value_counts().reset_index()
            fig_status = px.pie(status_counts, names='Flight_Status', values='count', 
                                title="Flight Status Distribution", hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with c2:
            delayed_flights = df[df['Flight_Status'] == 'Delayed']
            avg_delay_ac = delayed_flights.groupby('Aircraft_Type')['Delay_Minutes'].mean().reset_index()
            fig_delay = px.bar(avg_delay_ac, x='Delay_Minutes', y='Aircraft_Type', orientation='h',
                               title="Average Delay Minutes by Aircraft Type",
                               labels={'Delay_Minutes': 'Avg Delay (Mins)', 'Aircraft_Type': 'Aircraft'},
                               color='Delay_Minutes', color_continuous_scale='Reds')
            st.plotly_chart(fig_delay, use_container_width=True)

    # --- Tab 2: Financial Performance ---
    with tab2:
        st.subheader("Revenue Analysis & Pricing Dynamics")
        c1, c2 = st.columns(2)
        
        with c1:
            # Top Routes by Revenue
            route_rev = df.groupby('Route')['Total_Revenue_USD'].sum().sort_values(ascending=False).reset_index().head(5)
            fig_route = px.bar(route_rev, x='Total_Revenue_USD', y='Route', orientation='h',
                               title="Top 5 Most Profitable Routes",
                               labels={'Total_Revenue_USD': 'Total Revenue ($)', 'Route': 'Route Corridor'},
                               color='Total_Revenue_USD', color_continuous_scale='Viridis')
            fig_route.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_route, use_container_width=True)
            
        with c2:
            # Ticket Price vs Passenger Count Scatter
            # Sample data if too dense to keep plot performant
            sample_df = df.sample(n=min(1000, len(df))) if len(df) > 0 else df
            fig_scatter = px.scatter(sample_df, x='Avg_Ticket_Price_USD', y='Passenger_Count',
                                     color='Aircraft_Type', size='Load_Factor_%',
                                     title="Ticket Price vs. Passenger Count (Sampled)",
                                     labels={'Avg_Ticket_Price_USD': 'Avg Ticket Price ($)', 'Passenger_Count': 'Passengers Placed'})
            st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Tab 3: Fleet & Sustainability ---
    with tab3:
        st.subheader("Fleet Carbon Footprint & Utilization Profiles")
        c1, c2 = st.columns(2)
        
        with c1:
            fleet_dist = df.groupby('Aircraft_Type')['Distance_KM'].sum().reset_index()
            fig_fleet = px.bar(fleet_dist, x='Aircraft_Type', y='Distance_KM',
                               title="Total Distance Traveled by Fleet Type (KM)",
                               color='Aircraft_Type', color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_fleet, use_container_width=True)
            
        with c2:
            co2_summary = df.groupby('Aircraft_Type')['CO2_Emissions_KG'].mean().reset_index()
            fig_co2 = px.bar(co2_summary, x='Aircraft_Type', y='CO2_Emissions_KG',
                             title="Average CO₂ Emissions per Flight (KG)",
                             color='CO2_Emissions_KG', color_continuous_scale='YlGnBu')
            st.plotly_chart(fig_co2, use_container_width=True)

    # --- Tab 4: Time-Series Trends ---
    with tab4:
        st.subheader("Chronological Traffic & Operational Trajectory")
        
        # Resample data by week
        df_time = df.set_index('Departure_DateTime').resample('W')[['Passenger_Count', 'Total_Revenue_USD']].sum().reset_index()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_time['Departure_DateTime'], y=df_time['Passenger_Count'],
                                      mode='lines+markers', name='Weekly Passengers', yaxis='y1', line=dict(color='RoyalBlue')))
        fig_trend.add_trace(go.Scatter(x=df_time['Departure_DateTime'], y=df_time['Total_Revenue_USD'],
                                      mode='lines+markers', name='Weekly Revenue ($)', yaxis='y2', line=dict(color='ForestGreen')))
        
        # Create dual axis layout
        fig_trend.update_layout(
            title="Weekly Passenger Volume and Revenue Trends Over Time",
            xaxis=dict(title="Timeline"),
            yaxis=dict(title="Passenger Volume", titlefont=dict(color='RoyalBlue'), tickfont=dict(color='RoyalBlue')),
            yaxis2=dict(title="Revenue ($)", titlefont=dict(color='ForestGreen'), tickfont=dict(color='ForestGreen'), overlaying='y', side='right'),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Tab 5: Customer Satisfaction ---
    with tab5:
        st.subheader("Service Quality & Sentiment Correlates")
        c1, c2 = st.columns(2)
        
        with c1:
            fig_hist = px.histogram(df.dropna(subset=['Customer_Rating']), x='Customer_Rating', nbins=20,
                                    title="Distribution of Overall Customer Ratings",
                                    color_discrete_sequence=['#FFB6C1'], labels={'Customer_Rating': 'Rating (1-5)'})
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with c2:
            # Boxplot checking impact of delay on ratings
            fig_box = px.box(df.dropna(subset=['Customer_Rating']), x='Flight_Status', y='Customer_Rating',
                             title="Customer Ratings Spread Across Flight Statuses",
                             color='Flight_Status', color_discrete_sequence=px.colors.qualitative.Vivid)
            st.plotly_chart(fig_box, use_container_width=True)
