import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(
    page_title="Emirates Fleet Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Dark & Emirates Red CSS Injection
st.markdown(
    """
    <style>
    /* Global Background and Sidebar adjustments */
    .stApp {
        background-color: #0B0C10 !important;
        color: #F5F5F7 !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #111318 !important;
    }
    
    /* Recolor the selected pill tags in the sidebar to Emirates Red */
    div[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #D71921 !important;
        color: #FFFFFF !important;
        font-weight: 500;
        border-radius: 4px;
    }
    
    /* Border accent focus color for dropdown menus */
    div[data-testid="stSidebar"] div[data-baseweb="select"] {
        border-color: #D71921 !important;
    }
    
    /* Style tabs to look slick in dark mode */
    button[data-baseweb="tab"] {
        color: #A0A5B5 !important;
        font-size: 16px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #D71921 !important;
        font-weight: bold !important;
        border-bottom-color: #D71921 !important;
    }
    
    /* Horizontal rules */
    hr {
        border-color: #222630 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
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
    df['Load_Factor_%'] = (df['Passenger_Count'] / df['Max_Capacity'] * 100).round(1)
    return df

df_raw = load_data()

if not df_raw.empty:
    # --- Sidebar Filters ---
    st.sidebar.markdown("<h2 style='color:#D71921; font-size:22px;'>🔴 Hub Control</h2>", unsafe_allow_html=True)
    
    # Origin Filter
    all_origins = sorted(df_raw['Origin'].unique())
    selected_origins = st.sidebar.multiselect("Select Origin Hubs", all_origins, default=all_origins)
    
    # Aircraft Type Filter
    all_aircraft = sorted(df_raw['Aircraft_Type'].unique())
    selected_aircraft = st.sidebar.multiselect("Select Fleet Types", all_aircraft, default=all_aircraft)
    
    # Filter the dataframe based on selection
    df = df_raw[
        (df_raw['Origin'].isin(selected_origins)) & 
        (df_raw['Aircraft_Type'].isin(selected_aircraft))
    ]

    # --- Header ---
    st.markdown("<h1 style='color:#FFFFFF;'>✈️ Emirates SkyCargo & Fleet Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A0A5B5;'>Executive performance matrix monitoring networks, flight operations, and corporate sustainability.</p>", unsafe_allow_html=True)
    st.write("---")

    # --- Top Level Metrics (KPIs) ---
    total_flights = len(df)
    total_rev = df['Total_Revenue_USD'].sum()
    total_pax = df['Passenger_Count'].sum()
    
    on_time_count = len(df[df['Flight_Status'] == 'On Time'])
    otp = (on_time_count / total_flights * 100) if total_flights > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Network Departures", f"{total_flights:,}")
    col2.metric("Gross Revenue Realized", f"${total_rev:,.2f}")
    col3.metric("System Passengers Manifested", f"{total_pax:,}")
    col4.metric("On-Time Performance (OTP)", f"{otp:.1f}%")

    st.write("---")

    # --- Tabbed Layout for EDA Operations ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⏱️ Flight Operations", 
        "💰 Financial Metrics", 
        "🌱 Fleet Sustainability", 
        "📈 Route Trajectories", 
        "⭐ Guest Satisfaction"
    ])

    # Shared Dark Theme Layout Template for Plotly Figures
    dark_layout_template = dict(
        paper_bgcolor='#111318',
        plot_bgcolor='#111318',
        font=dict(color='#F5F5F7'),
        title_font=dict(color='#FFFFFF', size=16),
        xaxis=dict(gridcolor='#222630', title_font=dict(color='#A0A5B5'), tickfont=dict(color='#A0A5B5')),
        yaxis=dict(gridcolor='#222630', title_font=dict(color='#A0A5B5'), tickfont=dict(color='#A0A5B5'))
    )

    # --- Tab 1: Operations & Delays ---
    with tab1:
        st.subheader("Network Reliability & Interruption Tracking")
        c1, c2 = st.columns(2)
        
        with c1:
            status_counts = df['Flight_Status'].value_counts().reset_index()
            # Premium Palette: Crimson Red, Deep Gold, Dark Gray, Light Muted Slate
            fig_status = px.pie(status_counts, names='Flight_Status', values='count', 
                                title="Proportional Status Profile", hole=0.4,
                                color_discrete_sequence=['#D71921', '#D4AF37', '#2A2C33', '#4A4E59'])
            fig_status.update_layout(**dark_layout_template)
            st.plotly_chart(fig_status, use_container_width=True)
            
        with c2:
            delayed_flights = df[df['Flight_Status'] == 'Delayed']
            avg_delay_ac = delayed_flights.groupby('Aircraft_Type')['Delay_Minutes'].mean().reset_index()
            fig_delay = px.bar(avg_delay_ac, x='Delay_Minutes', y='Aircraft_Type', orientation='h',
                               title="Average System Delays by Equipment Profile",
                               labels={'Delay_Minutes': 'Mins', 'Aircraft_Type': 'Equipment'},
                               color='Delay_Minutes', color_continuous_scale=['#4A1113', '#D71921'])
            fig_delay.update_layout(**dark_layout_template)
            fig_delay.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_delay, use_container_width=True)

    # --- Tab 2: Financial Performance ---
    with tab2:
        st.subheader("Revenue Generation & Pricing Vectors")
        c1, c2 = st.columns(2)
        
        with c1:
            route_rev = df.groupby('Route')['Total_Revenue_USD'].sum().sort_values(ascending=False).reset_index().head(5)
            fig_route = px.bar(route_rev, x='Total_Revenue_USD', y='Route', orientation='h',
                               title="Top 5 Capital High-Yield Sectors",
                               labels={'Total_Revenue_USD': 'Gross Revenue ($)', 'Route': 'City Pairs'},
                               color='Total_Revenue_USD', color_continuous_scale=['#2A2C33', '#D71921'])
            fig_route.update_layout(**dark_layout_template)
            fig_route.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_route, use_container_width=True)
            
        with c2:
            sample_df = df.sample(n=min(1000, len(df))) if len(df) > 0 else df
            fig_scatter = px.scatter(sample_df, x='Avg_Ticket_Price_USD', y='Passenger_Count',
                                     color='Aircraft_Type', size='Load_Factor_%',
                                     title="Yield Price vs. Cabin Density Analysis (Sampled)",
                                     labels={'Avg_Ticket_Price_USD': 'Fare ($)', 'Passenger_Count': 'Manifested Pax'},
                                     color_discrete_sequence=['#D71921', '#D4AF37', '#A0A5B5', '#4A4E59', '#FFFFFF'])
            fig_scatter.update_layout(**dark_layout_template)
            st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Tab 3: Fleet & Sustainability ---
    with tab3:
        st.subheader("Environmental Metrics & Structural Utilization")
        c1, c2 = st.columns(2)
        
        with c1:
            fleet_dist = df.groupby('Aircraft_Type')['Distance_KM'].sum().reset_index()
            fig_fleet = px.bar(fleet_dist, x='Aircraft_Type', y='Distance_KM',
                               title="Total Fleet Asset Utilization (KM)",
                               color='Aircraft_Type', color_discrete_sequence=['#D71921'])
            fig_fleet.update_layout(**dark_layout_template)
            fig_fleet.update_layout(showlegend=False)
            st.plotly_chart(fig_fleet, use_container_width=True)
            
        with c2:
            co2_summary = df.groupby('Aircraft_Type')['CO2_Emissions_KG'].mean().reset_index()
            fig_co2 = px.bar(co2_summary, x='Aircraft_Type', y='CO2_Emissions_KG',
                             title="Mean Carbon Yield footprint per Sector (KG)",
                             color='CO2_Emissions_KG', color_continuous_scale=['#2A2C33', '#D71921'])
            fig_co2.update_layout(**dark_layout_template)
            fig_co2.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_co2, use_container_width=True)

    # --- Tab 4: Time-Series Trends ---
    with tab4:
        st.subheader("Chronological Traffic & Network Scaling")
        
        df_clean_time = df.dropna(subset=['Departure_DateTime'])
        
        if not df_clean_time.empty:
            df_time = df_clean_time.set_index('Departure_DateTime').resample('W')[['Passenger_Count', 'Total_Revenue_USD']].sum().reset_index()
            
            from plotly.subplots import make_subplots
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_trend.add_trace(
                go.Scatter(x=df_time['Departure_DateTime'], y=df_time['Passenger_Count'], 
                           mode='lines+markers', name='Weekly Volume', line=dict(color='#D71921', width=3)),
                secondary_y=False
            )
            
            fig_trend.add_trace(
                go.Scatter(x=df_time['Departure_DateTime'], y=df_time['Total_Revenue_USD'], 
                           mode='lines+markers', name='Weekly Revenue ($)', line=dict(color='#D4AF37', width=2, dash='dash')),
                secondary_y=True
            )
            
            fig_trend.update_layout(**dark_layout_template)
            fig_trend.update_layout(
                title_text="Weekly Volume and Yield Velocity Scaling Tracking",
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(17,19,24,0.7)')
            )
            fig_trend.update_xaxes(title_text="Operational Timeline", gridcolor='#222630')
            fig_trend.update_yaxes(title_text="Passenger Counts", title_font=dict(color="#D71921"), tickfont=dict(color="#D71921"), gridcolor='#222630', secondary_y=False)
            fig_trend.update_yaxes(title_text="Gross Revenue Velocity ($)", title_font=dict(color="#D4AF37"), tickfont=dict(color="#D4AF37"), secondary_y=True)
            
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("Data threshold insufficient for trend mapping.")

    # --- Tab 5: Customer Satisfaction ---
    with tab5:
        st.subheader("Premium Guest Sentiment Indices")
        c1, c2 = st.columns(2)
        
        with c1:
            fig_hist = px.histogram(df.dropna(subset=['Customer_Rating']), x='Customer_Rating', nbins=15,
                                    title="Guest Satisfaction Score Distribution",
                                    color_discrete_sequence=['#D71921'], labels={'Customer_Rating': 'Score (1-5 Tier)'})
            fig_hist.update_layout(**dark_layout_template)
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with c2:
            fig_box = px.box(df.dropna(subset=['Customer_Rating']), x='Flight_Status', y='Customer_Rating',
                             title="Experience Variance Mapped against Operational Status",
                             color='Flight_Status', color_discrete_sequence=['#D4AF37', '#D71921', '#A0A5B5', '#4A4E59'])
            fig_box.update_layout(**dark_layout_template)
            fig_box.update_layout(showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
