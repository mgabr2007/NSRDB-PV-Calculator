import streamlit as st
import pandas as pd
import math
import folium
from streamlit_folium import st_folium

def calculate_energy(data, area, azimuth):
    if data.empty:
        st.error("No data available to calculate energy.")
        return 0
    
    # Adjusting to the correct column names
    try:
        ghi = data['GHI'].mean()
        dni = data['DNI'].mean()
        dhi = data['DHI'].mean()
    except KeyError as e:
        st.error(f"Column not found: {e}")
        return 0

    # Calculate the effective irradiance on the vertical facade
    azimuth_radians = math.radians(azimuth)
    
    # Assuming a vertical surface facing the azimuth angle
    incident_irradiance = dni * max(math.cos(azimuth_radians), 0) + dhi

    # Calculate the energy generated by the facade
    energy_generated = incident_irradiance * area
    return energy_generated

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

st.title('Solar Energy Potential Calculator')

# Streamlit inputs
area = st.number_input('Facade Area (m²)', min_value=1.0, value=10.0)
azimuth = st.number_input('Facade Azimuth (degrees)', min_value=0.0, max_value=360.0, value=180.0)
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
    if 'last_clicked' in map_data:
        latitude = map_data['last_clicked']['lat']
        longitude = map_data['last_clicked']['lng']
        st.write(f"Selected Location: Latitude {latitude}, Longitude {longitude}")

if st.button('Calculate Energy'):
    if uploaded_file is not None:
        if latitude is not None and longitude is not None:
            solar_data = load_data(uploaded_file)
            if not solar_data.empty:
                st.write(solar_data.head())  # Display the first few rows for debugging
                energy_generated = calculate_energy(solar_data, area, azimuth)
                st.write(f"Average Energy Generated: {energy_generated:.2f} Wh")
            else:
                st.error('No data available in the uploaded file.')
        else:
            st.error('Please select a location on the map.')
    else:
        st.error('Please upload a CSV file containing solar data.')
