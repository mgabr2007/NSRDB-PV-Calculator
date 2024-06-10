import streamlit as st
import requests
import pandas as pd
import urllib.parse
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

    if len(response_json['errors']) > 0:
        errors = '\n'.join(response_json['errors'])
        st.error(f"Request errored out: {errors}")
        st.stop()
    return response_json

def main(api_key, email, points, names):
    BASE_URL = "https://developer.nrel.gov/api/nsrdb/v2/solar/nsrdb-msg-v1-0-0-tdy-download.json?"
    input_data = {
        'attributes': 'clearsky_dhi,clearsky_dni,air_temperature,clearsky_ghi,cloud_fill_flag,cloud_type,dew_point,dhi,dni,fill_flag,ghi,relative_humidity,solar_zenith_angle,surface_albedo,surface_pressure,total_precipitable_water,wind_direction,wind_speed',
        'interval': '60',
        'include_leap_day': 'true',
        'api_key': api_key,
        'email': email,
    }
    
    for name in names:
        st.write(f"Processing name: {name}")
        for id, location_ids in enumerate(points):
            input_data['names'] = [name]
            input_data['location_ids'] = location_ids
            st.write(f'Making request for point group {id + 1} of {len(points)}...')
            
            headers = {
                'x-api-key': api_key
            }
            data = get_response_json_and_handle_errors(requests.post(BASE_URL, json=input_data, headers=headers))
            download_url = data['outputs']['downloadUrl']
            st.write(data['outputs']['message'])
            st.write(f"Data can be downloaded from this url: {download_url}")
            st.write(f"Processed point group {id + 1}.")

            # Delay for 1 second to prevent rate limiting
            time.sleep(1)

st.title('Solar Data Downloader')

# Streamlit inputs
api_key = st.text_input('API Key', type='password')
email = st.text_input('Email')
points = st.text_area('Location IDs (comma separated)', '698192')
names = st.multiselect('Names', ['tdy', 'tdy-2014', 'tdy-2022'], ['tdy'])

if st.button('Download Data'):
    points_list = points.split(',')
    main(api_key, email, points_list, names)
