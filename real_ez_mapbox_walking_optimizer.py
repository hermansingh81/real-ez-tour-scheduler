
import streamlit as st
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Walking Route Optimizer", layout="centered")
st.title("Real EZ Walking Route Optimizer (Mapbox)")

st.markdown("Enter 3 to 10 property addresses. This app will calculate the most efficient **walking** route using the Mapbox Optimized Trips API.")

# Get Mapbox API Key
mapbox_token = st.text_input("Enter your Mapbox Access Token", type="password")

# Address input
st.subheader("Property Addresses")
addresses = []
for i in range(10):
    addr = st.text_input(f"Address {i+1}", key=f"addr_{i}")
    if addr:
        addresses.append(addr)

# Geocode function using Mapbox
def geocode_address(address, token):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{urllib.parse.quote(address)}.json?access_token={token}"
    res = requests.get(url)
    if res.status_code == 200 and res.json()["features"]:
        coords = res.json()["features"][0]["center"]
        return coords[0], coords[1]  # lon, lat
    return None

# Optimize Route using Mapbox
if st.button("Optimize Walking Route"):
    if len(addresses) < 3:
        st.error("Please enter at least 3 addresses.")
    elif not mapbox_token:
        st.error("Mapbox access token is required.")
    else:
        coords_list = []
        for addr in addresses:
            coords = geocode_address(addr, mapbox_token)
            if coords:
                coords_list.append(coords)
            else:
                st.error(f"Could not geocode: {addr}")
                break

        if len(coords_list) == len(addresses):
            coord_str = ";".join([f"{lon},{lat}" for lon, lat in coords_list])
            url = (
                f"https://api.mapbox.com/optimized-trips/v1/mapbox/walking/"
                f"{coord_str}?access_token={mapbox_token}&roundtrip=true&source=first&destination=last&overview=full&geometries=geojson"
            )
            res = requests.get(url)
            data = res.json()

            if "trips" in data and data["trips"]:
                trip = data["trips"][0]
                waypoint_order = data["waypoints"]
                order = sorted([(w["waypoint_index"], i) for i, w in enumerate(waypoint_order)])
                optimized_addresses = [addresses[i[1]] for i in order]

                st.success("Optimized walking route generated.")
                st.subheader("Optimized Stop Order")
                for i, stop in enumerate(optimized_addresses, 1):
                    st.markdown(f"**Stop {i}:** {stop}")

                st.markdown("This optimizer uses real-time walking paths and traffic-aware estimates via Mapbox.")
            else:
                st.error("Failed to retrieve optimized route from Mapbox.")
