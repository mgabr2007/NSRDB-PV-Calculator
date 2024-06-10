import streamlit as st
import requests
import time

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

def main(api_key, email, coordinates, names):
    BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.csv?"

    for name in names:
        st.write(f"Processing name: {name}")
        for coord in coordinates:
            params = {
                'api_key': api_key,
                'email': email,
                'names': name,
                'attributes': 'ghi,dni,dhi,air_temperature,dew_point,relative_humidity,wind_speed,wind_direction,surface_pressure,toa_irradiance,clearsky_dhi,clearsky_dni,clearsky_ghi,cloud_type,fill_flag,footprint,ozone,surface_albedo,total_precipitable_water',
                'interval': '60',
                'wkt': f"POINT({coord['lon']} {coord['lat']})"
            }
            st.write(f'Making request for coordinate {coord}...')

            response = requests.get(BASE_URL, params=params)
            data = get_response_json_and_handle_errors(response)
            
            st.write(f"Data for {coord['lat']}, {coord['lon']} retrieved successfully.")
            st.write(data)  # or process the data as needed

            # Delay for 1 second to prevent rate limiting
            time.sleep(1)

st.title('Solar Data Downloader')

# Streamlit inputs
api_key = st.text_input('API Key', type='password')
email = st.text_input('Email')
coordinates_input = st.text_area('Coordinates (latitude,longitude pairs separated by newlines)', '40.7128,-74.0060\n34.0522,-118.2437')
names = st.multiselect('Names', ['tdy', 'tdy-2014', 'tdy-2022'], ['tdy'])

if st.button('Download Data'):
    try:
        coordinates_list = []
        for line in coordinates_input.split('\n'):
            lat_lon = line.split(',')
            if len(lat_lon) == 2:
                coordinates_list.append({'lat': float(lat_lon[0].strip()), 'lon': float(lat_lon[1].strip())})
        if not coordinates_list:
            st.error('No valid coordinates provided.')
        else:
            main(api_key, email, coordinates_list, names)
    except Exception as e:
        st.error(f'Error processing coordinates: {e}')
