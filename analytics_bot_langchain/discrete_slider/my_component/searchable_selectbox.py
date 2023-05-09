from typing import List, Dict
import streamlit as st

from analytics_bot_langchain.discrete_slider.my_component import st_keyup


def searchable_selectbox(label: str, options: List[Dict[str, str]]):
    """
    Renders a searchable selectbox component using st_keyup.

    label: Label for the component.
    options: A list of dictionaries with 'label' and 'value' keys representing
             the options available in the selectbox.
    """

    # Generate a dictionary mapping option labels to values
    options_dict = {option['label']: option['value'] for option in options}

    # Define a function to handle changes to the search input
    def on_change(value):
        if value:
            # Filter the options dictionary based on the search input
            filtered_options = {k: v for k, v in options_dict.items() if value.lower() in k.lower()}
            # Map the filtered options back to a list of dictionaries
            filtered_options_list = [{'label': k, 'value': v} for k, v in filtered_options.items()]
            # Render the filtered options in the selectbox
            selected_option = st.selectbox(label, options=filtered_options_list, format_func=lambda option: option['label'])
        else:
            # If the search input is empty, render all options in the selectbox
            selected_option = st.selectbox(label, options=options, format_func=lambda option: option['label'])

        # Return the value of the selected option
        return selected_option['value']

    # Render the st_keyup component with the search input and call the on_change function when it changes
    selected_value = st_keyup(label, on_change=on_change)

    # Return the selected value
    return selected_value
