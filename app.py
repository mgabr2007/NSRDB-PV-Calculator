import streamlit as st
import requests
import pandas as pd
import time

def get_response_json_and_handle_errors(response: requests.Response) -> dict:
    if response.status_code != 200:
        st.error(f"An error occurred: {response.status_code} {response.reason}")
        st.error(f"Response body: {response.text}")
        st.stop()

    try:
        response_json = response.json()
    except:
        st.error(f"Response couldn't be parsed as JSON: {response.text}")
        st.stop()

    if 'errors' in response_json and len(response_json['errors']) > 0:
        errors = '\n'.join(response_json['errors'])
        st.error(f"Request errored out: {errors}")
        st.stop()
    return response_json

def main(api_key, email, coordinates, names):
    BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb_msg_v1_0_0_tdy_download.json?"
    input_data = {
        'attributes': 'clearsky_dhi,clearsky_dni,air_temperature,clearsky_ghi,cloud_fill_flag,cloud_type,dew_point,dhi,dni,fill_flag,ghi,relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,wind_direction,wind_speed',
        'interval': '60',
        'include_leap_day': 'true',
        'api_key': api_key,
        'email': email,
    }
    
    for name in names:
        st.write(f"Processing name: {name}")
        for coord in coordinates:
            input_data['names'] = [name]
            input_data['lat'] = coord['lat']
            input_data['lon'] = coord['lon']
            st.write(f'Making request for coordinate {coord}...')

            headers = {
                'x-api-key': api_key
            }
            data = get_response_json_and_handle_errors(requests.post(BASE_URL, json=input_data, headers=headers))
            download_url = data['outputs']['downloadUrl']
            st.write(data['outputs']['message'])
            st.write(f"Data can be downloaded from this url: {download_url}")
            st.write(f"Processed coordinate {coord}.")

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
