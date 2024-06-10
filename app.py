import streamlit as st
import requests
import pandas as pd
import time
import math

def get_response_json_and_handle_errors(response: requests.Response) -> dict:
    if response.status_code != 200:
        st.error(f"An error occurred: {response.status_code} {response.reason}")
        st.error(f"Response body: {response.text}")
        st.stop()

    try:
        response_json = response.json()
    except Exception as e:
        st.error(f"Response couldn't be parsed as JSON: {response.text}")
        st.error(f"Exception: {e}")
        st.stop()

    if 'errors' in response_json and len(response_json['errors']) > 0:
        errors = '\n'.join(response_json['errors'])
        st.error(f"Request errored out: {errors}")
        st.stop()
    return response_json

def fetch_solar_data(api_key, email, coordinates, years):
    BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.json?"
    attributes = 'ghi,dni,dhi'
    all_data = []

    for year in years:
        st.write(f"Processing year: {year}")
        for coord in coordinates:
            params = {
                'api_key': api_key,
                'email': email,
                'names': year,
                'attributes': attributes,
                'interval': '60',
                'wkt': f"POINT({coord['lon']} {coord['lat']})"
            }
            st.write(f'Making request for coordinate {coord}...')

            response = requests.get(BASE_URL, params=params)
            data = get_response_json_and_handle_errors(response)
            all_data.append(pd.DataFrame(data['outputs']['data']))
            
            st.write(f"Data for {coord['lat']}, {coord['lon']} retrieved successfully.")
            
            # Delay for 1 second to prevent rate limiting
            time.sleep(1)
    
    return pd.concat(all_data)

def calculate_energy(data, area, azimuth):
    ghi = data['ghi'].mean()
    dni = data['dni'].mean()
    dhi = data['dhi'].mean()
    
    azimuth_radians = math.radians(azimuth)
    incident_irradiance = ghi * math.cos(azimuth_radians) + dni * math.sin(azimuth_radians) + dhi

    energy_generated = incident_irradiance * area
    return energy_generated

st.title('Solar Energy Potential Calculator')

# Streamlit inputs
api_key = st.text_input('API Key', type='password')
email = st.text_input('Email')
coordinates_input = st.text_area('Coordinates (latitude,longitude pairs separated by newlines)', '40.7128,-74.0060\n34.0522,-118.2437')
years = st.multiselect('Years', list(range(1998, 2021)), [2020])
area = st.number_input('Facade Area (m²)', min_value=1.0, value=10.0)
azimuth = st.number_input('Facade Azimuth (degrees)', min_value=0.0, max_value=360.0, value=180.0)

if st.button('Calculate Energy'):
    try:
        coordinates_list = []
        for line in coordinates_input.split('\n'):
            lat_lon = line.split(',')
            if len(lat_lon) == 2:
                coordinates_list.append({'lat': float(lat_lon[0].strip()), 'lon': float(lat_lon[1].strip())})
        if not coordinates_list:
            st.error('No valid coordinates provided.')
        else:
            solar_data = fetch_solar_data(api_key, email, coordinates_list, years)
            energy_generated = calculate_energy(solar_data, area, azimuth)
            st.write(f"Average Energy Generated: {energy_generated:.2f} Wh")
    except Exception as e:
        st.error(f'Error processing data: {e}')
