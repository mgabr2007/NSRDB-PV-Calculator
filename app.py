import streamlit as st
import pandas as pd
import math

def calculate_energy(data, area, azimuth):
    if data.empty:
        st.error("No data available to calculate energy.")
        return 0

    st.write("Columns in data:", data.columns.tolist())  # Display column names for debugging
    
    ghi = data['GHI'].mean()
    dni = data['DNI'].mean()
    dhi = data['DHI'].mean()
    
    azimuth_radians = math.radians(azimuth)
    incident_irradiance = ghi * math.cos(azimuth_radians) + dni * math.sin(azimuth_radians) + dhi

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
api_key = st.text_input('API Key', type='password')
email = st.text_input('Email')
coordinates_input = st.text_area('Coordinates (latitude,longitude pairs separated by newlines)', '40.7128,-74.0060\n34.0522,-118.2437')
years = st.multiselect('Years', list(range(1998, 2021)), [2020])
area = st.number_input('Facade Area (m²)', min_value=1.0, value=10.0)
azimuth = st.number_input('Facade Azimuth (degrees)', min_value=0.0, max_value=360.0, value=180.0)
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if st.button('Calculate Energy'):
    if uploaded_file is not None:
        solar_data = load_data(uploaded_file)
        if not solar_data.empty:
            st.write(solar_data.head())  # Display the first few rows for debugging
            energy_generated = calculate_energy(solar_data, area, azimuth)
            st.write(f"Average Energy Generated: {energy_generated:.2f} Wh")
        else:
            st.error('No data available in the uploaded file.')
    else:
        st.error('Please upload a CSV file containing solar data.')
