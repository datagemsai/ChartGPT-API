import streamlit as st
from my_component.searchable_selectbox import st_searchable_selectbox

# Some example options
options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]

# Call your custom component function
selected_option = st_searchable_selectbox("Select an option", options)

# Display the selected option
st.write(f"You selected {selected_option}")