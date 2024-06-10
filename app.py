import streamlit as st
import pandas as pd
import math
import folium
from streamlit_folium import st_folium
import pvlib

def calculate_energy(data, latitude, longitude, area, azimuth, efficiency):
    if data.empty:
        st.error("No data available to calculate energy.")
        return 0
    
    # Convert azimuth to pvlib format (0 south, 90 west, 180 north, 270 east)
    azimuth_pvlib = (azimuth + 180) % 360
    
    # Create location object
    location = pvlib.location.Location(latitude, longitude)
    
    # Calculate solar position
    solar_position = location.get_solarposition(times=data.index)
    
    # Calculate plane of array (POA) irradiance
    poa_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=90,
        surface_azimuth=azimuth_pvlib,
        dni=data['DNI'],
        ghi=data['GHI'],
        dhi=data['DHI'],
        solar_zenith=solar_position['zenith'],
        solar_azimuth=solar_position['azimuth']
    )
    
    # Calculate incident irradiance
    incident_irradiance = poa_irradiance['poa_global'].mean()
    
    # Calculate the energy generated by the facade considering PV efficiency
    energy_generated = incident_irradiance * area * efficiency
    return energy_generated

def load_data(file):
    try:
        data = pd.read_csv(file, index_col=0, parse_dates=True)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

st.title('Solar Energy Potential Calculator')

st.write("""
## Instructions

This app calculates the average energy generated by a photovoltaic (PV) system on a building facade. 

### Parameters:

- **Facade Area (m²)**: The area of the facade in square meters.
- **Facade Azimuth (degrees)**: The direction the facade is facing, in degrees (0° is North, 90° is East, 180° is South, and 270° is West).
- **PV Efficiency (0-1)**: The efficiency of the photovoltaic system, ranging from 0 to 1.
- **CSV File**: Upload a CSV file containing solar irradiance data with columns for GHI (Global Horizontal Irradiance), DNI (Direct Normal Irradiance), and DHI (Diffuse Horizontal Irradiance).

### Calculation:

The calculation uses the following equation to estimate the average energy generated:

\[ \text{Energy Generated (Wh)} = \text{Incident Irradiance (W/m²)} \times \text{Facade Area (m²)} \times \text{PV Efficiency} \]

Incident Irradiance is calculated using the pvlib library considering the solar position and irradiance on a vertical surface.
""")

# Streamlit inputs
area = st.number_input('Facade Area (m²)', min_value=1.0, value=10.0)
azimuth = st.number_input('Facade Azimuth (degrees)', min_value=0.0, max_value=360.0, value=180.0)
efficiency = st.number_input('PV Efficiency (0-1)', min_value=0.0, max_value=1.0, value=0.2)
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Initialize map
m = folium.Map(location=[20, 0], zoom_start=2)

# Add a marker to the map with default location
marker = folium.Marker(location=[20, 0], draggable=True)
marker.add_to(m)

# Display the map and get the selected location
st.write("Click on the map to select a location:")
map_data = st_folium(m, width=700, height=500)

# Get the selected location
latitude = None
longitude = None

if map_data:
    st.write("Map data available:", map_data)  # Debugging line to display map_data
    if map_data.get('last_clicked') is not None:
        latitude = map_data['last_clicked']['lat']
        longitude = map_data['last_clicked']['lng']
        st.write(f"Selected Location: Latitude {latitude}, Longitude {longitude}")

if uploaded_file is not None:
    solar_data = load_data(uploaded_file)
    if not solar_data.empty:
        st.write("Uploaded file content:")
        st.write(solar_data.head())  # Display the first few rows for debugging

        # Detect and display the time interval of the data
        time_diffs = solar_data.index.to_series().diff().dropna()
        time_interval = time_diffs.mode().iloc[0] if not time_diffs.empty else pd.Timedelta(seconds=0)
        st.write(f"Data Interval: {time_interval}")

    if st.button('Calculate Energy'):
        if latitude is not None and longitude is not None:
            if not solar_data.empty:
                energy_generated = calculate_energy(solar_data, latitude, longitude, area, azimuth, efficiency)
                st.metric(label="Average Energy Generated", value=f"{energy_generated:.2f} Wh", delta=f"Interval: {time_interval}")
            else:
                st.error('No data available in the uploaded file.')
        else:
            st.error('Please select a location on the map.')
else:
    st.error('Please upload a CSV file containing solar data.')
