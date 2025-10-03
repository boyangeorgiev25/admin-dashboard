import streamlit as st

from config.config import config


def venues_tab():
    st.header("Venue Management")

    tab1, tab2 = st.tabs(["View Venues", "Add Venue"])

    with tab1:
        _view_venues()

    with tab2:
        _add_venue()


def _view_venues():
    st.subheader("All Venues")

    if st.button("🔄 Refresh", key="refresh_venues"):
        st.rerun()

    try:
        venues = st.session_state.venue_service.get_all_venues()

        if not venues:
            st.info("No venues found")
            return

        st.write(f"Total: {len(venues)} venues")

        for venue in venues:
            with st.expander(f"🏢 {venue['name']} - {venue['subtype_name']}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**ID:** {venue['id']}")
                    st.write(f"**Address:** {venue['address']}")
                    st.write(f"**Keywords:** {venue['keywords']}")
                    st.write(f"**URL:** {venue['url']}")
                    st.write(f"**Location:** {venue['location']}")

                with col2:
                    if venue['img_url']:
                        try:
                            st.image(venue['img_url'], width=150)
                        except Exception:
                            st.caption(f"Image: {venue['img_url']}")

                    if st.button(f"🗑️ Delete", key=f"del_venue_{venue['id']}"):
                        _delete_venue(venue['id'], venue['name'])

    except Exception as e:
        st.error(f"Error loading venues: {str(e)}")


def _add_venue():
    st.subheader("Add New Venue")

    try:
        activity_types = st.session_state.venue_service.get_activity_types()

        type_options = {f"{t['emoji']} {t['subtype']} ({t['type']})": t['id'] for t in activity_types}

        with st.form("add_venue_form"):
            name = st.text_input("Venue Name*", max_chars=60)

            selected_type = st.selectbox("Activity Type*", options=list(type_options.keys()))
            subtype_id = type_options[selected_type]

            address = st.text_input("Address*", max_chars=150)

            city = st.text_input("City*", max_chars=100, help="Used to geocode location")

            keywords = st.text_input("Keywords", max_chars=150, help="Comma separated")

            img_url = st.text_input("Image URL", max_chars=150)

            url = st.text_input("Website URL", max_chars=150)

            submitted = st.form_submit_button("Add Venue")

            if submitted:
                if not name or not address or not city:
                    st.error("Name, address, and city are required")
                else:
                    _save_venue(name, subtype_id, keywords, address, city, img_url, url)

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _save_venue(name, subtype_id, keywords, address, city, img_url, url):
    try:
        location = _fetch_location(city)

        success = st.session_state.venue_service.add_venue(
            name, subtype_id, keywords, address, img_url, url, location
        )

        if success:
            st.success(f"✓ Added venue: {name}")
            st.balloons()
        else:
            st.error("Failed to add venue")

    except Exception as e:
        st.error(f"Error: {str(e)}")


def _delete_venue(venue_id, venue_name):
    try:
        if st.session_state.venue_service.delete_venue(venue_id):
            st.success(f"✓ Deleted venue: {venue_name}")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _fetch_location(city: str) -> str:
    import csv

    locations = {}

    try:
        with open("belgian-cities.csv", mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                name = row["name"].lower().strip()
                lat = float(row["lat"])
                lng = float(row["lng"])
                locations[name] = (lng, lat)
    except FileNotFoundError:
        pass

    location = locations.get(city.lower().strip())

    if location:
        return f"POINT({location[0]} {location[1]})"

    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError

        geolocator = Nominatim(user_agent="jointly_dashboard")
        location = geolocator.geocode(city, country_codes="BE")

        if location:
            return f"POINT({location.longitude} {location.latitude})"
    except (GeocoderTimedOut, GeocoderServiceError, Exception):
        pass

    return config.DEFAULT_LOCATION
