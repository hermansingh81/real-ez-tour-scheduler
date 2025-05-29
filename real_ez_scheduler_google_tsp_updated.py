
import streamlit as st
import pandas as pd
import requests
import urllib.parse

st.set_page_config(page_title="Real EZ Scheduler", layout="wide")
st.title("Real EZ Scheduler: Optimized Tour with Walking/Driving Mode")

st.markdown("Enter up to 10 properties, rank them by priority (1 = highest), and select your tour mode. The app will optimize your route using the Google Maps API.")

# Travel mode selection
travel_mode = st.radio("Select Tour Mode", ["driving", "walking"], horizontal=True)

# Input fields
addresses, agents, emails, phones, ranks = [], [], [], [], []
cols = st.columns([2, 2, 2, 2, 1])

for i in range(10):
    with cols[0]:
        addr = st.text_input(f"Address {i+1}", key=f"addr_{i}")
    with cols[1]:
        agent = st.text_input("Agent Name", key=f"agent_{i}")
    with cols[2]:
        email = st.text_input("Agent Email", key=f"email_{i}")
    with cols[3]:
        phone = st.text_input("Agent Phone", key=f"phone_{i}")
    with cols[4]:
        rank = st.number_input("Rank", min_value=1, max_value=10, step=1, key=f"rank_{i}")

    if addr:
        addresses.append(addr)
        agents.append(agent)
        emails.append(email)
        phones.append(phone)
        ranks.append(rank)

# Check for duplicate rankings
if len(ranks) > 1 and len(set(ranks)) != len(ranks):
    st.error("Each listing must have a unique rank from 1 to N.")
elif addresses:
    df = pd.DataFrame({
        "Address": addresses,
        "Agent": agents,
        "Email": emails,
        "Phone": phones,
        "Rank": ranks
    }).sort_values("Rank")

    st.subheader("Ranked Tour Plan")
    st.dataframe(df)

    # API Key input
    api_key = st.text_input("Enter your Google Maps API Key", type="password")

    if st.button("Generate Optimized Route"):
        if len(df) < 2:
            st.error("At least 2 addresses are needed.")
        elif not api_key:
            st.error("Please enter your Google Maps API Key.")
        else:
            origin = urllib.parse.quote_plus(df.iloc[0]["Address"])
            destination = urllib.parse.quote_plus(df.iloc[-1]["Address"])
            midpoints = df["Address"].tolist()[1:-1]
            waypoints = "|".join([urllib.parse.quote_plus(a) for a in midpoints])

            url = (
                f"https://maps.googleapis.com/maps/api/directions/json?"
                f"origin={origin}&destination={destination}&"
                f"waypoints=optimize:true|{waypoints}&"
                f"mode={travel_mode}&key={api_key}"
            )

            response = requests.get(url)
            data = response.json()

            if data["status"] == "OK":
                route = data["routes"][0]
                order = route["waypoint_order"]
                optimized = [df.iloc[0]["Address"]] + [midpoints[i] for i in order] + [df.iloc[-1]["Address"]]

                st.success("Optimized route generated.")
                st.subheader("Optimized Stop Order")
                for i, stop in enumerate(optimized, 1):
                    st.markdown(f"**Stop {i}:** {stop}")

                maps_url = (
                    f"https://www.google.com/maps/dir/?api=1"
                    f"&origin={origin}"
                    f"&destination={destination}"
                    f"&travelmode={travel_mode}"
                    f"&waypoints={'%7C'.join([urllib.parse.quote_plus(midpoints[i]) for i in order])}"
                )
                st.markdown(f"[🗺️ View Route on Google Maps]({maps_url})")
            else:
                st.error(f"Google Maps API Error: {data['status']}")

    # Messaging simulation
    st.subheader("Messaging Agents (Simulated)")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Message All Agents"):
            st.success("Messages sent to all agents (simulated).")
    with col2:
        for idx, row in df.iterrows():
            if st.button(f"Message {row['Agent']} ({row['Address']})", key=f"msg_{idx}"):
                st.success(f"Message sent to {row['Agent']} (simulated).")

    # Simulated agent replies
    st.subheader("Simulated Agent Reply Parsing")
    for i, row in df.iterrows():
        st.markdown(f"**{row['Address']}** — Agent {row['Agent']} replied: ✅ *Confirmed at 2:30 PM*")
