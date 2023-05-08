import os
import streamlit.components.v1 as components
import streamlit as st

_my_component = components.declare_component(
    "my_component",
    url="http://localhost:3001"
)
return_value = _my_component(greeting="Ahoy", name="Streamlit")
st.write(return_value)

