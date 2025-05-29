
import streamlit as st
import pandas as pd
import requests
import urllib.parse

st.set_page_config(page_title="Real EZ Full Scheduler", layout="wide")

st.title("Real EZ Full Scheduler with Route Optimization and Agent Messaging")

st.markdown("Enter up to 10 properties, rank them by priority (1 = highest), and select your preferred tour mode (driving or walking).")

# Select travel mode
travel_mode = st.radio("Select Tour Mode:", ["driving", "walking"], horizontal=True)

# Input form
addresses = []
agents = []
emails = []
phones = []
ranks = []

cols = st.columns([2, 2, 2, 2, 1])
for i in range(10):
    with cols[0]:
        address = st.text_input(f"Address {i+1}", key=f"addr_{i}")
    with cols[1]:
        agent = st.text_input(f"Agent Name", key=f"agent_{i}")
    with cols[2]:
        email = st.text_input(f"Agent Email", key=f"email_{i}")
    with cols[3]:
        phone = st.text_input(f"Agent Phone", key=f"phone_{i}")
    with cols[4]:
        rank = st.number_input(f"Rank", min_value=1, max_value=10, step=1, key=f"rank_{i}")

    if address:
        addresses.append(address)
        agents.append(agent)
        emails.append(email)
        phones.append(phone)
        ranks.append(rank)

# Validate unique ranking
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

    st.subheader("Tour Plan (Ranked)")
    st.dataframe(df)

    # Google Maps API Key
    api_key = st.text_input("Enter your Google Maps API Key", type="password")

    # Route optimization
    if st.button("Generate Optimized Route"):
        if len(df) >= 2 and api_key:
            origin = urllib.parse.quote_plus(df.iloc[0]["Address"])
            destination = urllib.parse.quote_plus(df.iloc[-1]["Address"])
            waypoints = "|".join([urllib.parse.quote_plus(addr) for addr in df["Address"].tolist()[1:-1]])

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
                reordered = [df.iloc[0]["Address"]] + [df["Address"].tolist()[1:-1][i] for i in order] + [df.iloc[-1]["Address"]]
                st.success("Optimized route created!")

                st.subheader("Optimized Tour Order")
                for i, stop in enumerate(reordered, 1):
                    st.markdown(f"**Stop {i}:** {stop}")

                maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode={travel_mode}&waypoints={'%7C'.join([urllib.parse.quote_plus(df['Address'].tolist()[i]) for i in order])}"
                st.markdown(f"[View Full Route on Google Maps]({maps_url})")
            else:
                st.error(f"Google Maps API Error: {data['status']}")

    # Messaging section
    st.subheader("Messaging Agents")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Message All Agents"):
            st.success("Messages sent to all agents (simulated). AI will parse replies.")
    with col2:
        for idx, row in df.iterrows():
            if st.button(f"Message {row['Agent']} ({row['Address']})", key=f"msg_{idx}"):
                st.success(f"Message sent to {row['Agent']} (simulated).")

    # Simulated AI response parsing
    st.subheader("Simulated AI Response Parsing")
    st.markdown("Below are mocked results from agent replies. In production, replies will be parsed via OpenAI.")
    for i, row in df.iterrows():
        st.markdown(f"**{row['Address']}** — Agent {row['Agent']} replied: ✅ *Confirmed at 2:30 PM*")
