import app
import streamlit as st
from PIL import Image


class Notices:
    def __init__(self) -> None:
        if app.DISPLAY_USER_UPDATES:
            st.info("""
            This is an **early access** version of ChartGPT.
            We're still working on improving the model's performance, finding bugs, and adding more features and datasets.

            Have any feedback or bug reports? [Let us know!](https://ne6tibkgvu7.typeform.com/to/jZnnMGjh)
            """, icon="🚨")

            st.warning("""
            **Update: 10 May 2023, 15:00 CET**

            Due to limits on OpenAI's API, we are now using GPT-3.5 instead of GPT-4. We are actively resolving this with OpenAI support.
            In the meantime you may experience inconsistent or less reliable results.
            """)

        if app.MAINTENANCE_MODE:
            st.warning("""
            **Offline for maintenance**

            This app is undergoing maintenance right now.
            Please check back later.

            In the meantime, [check us out on Product Hunt](https://www.producthunt.com/products/chartgpt)!
            """)
            ph_1 = Image.open('media/product_hunt_1.jpeg')
            ph_2 = Image.open('media/product_hunt_2.jpeg')
            ph_3 = Image.open('media/product_hunt_3.jpeg')
            st.image(ph_1)
            st.image(ph_2)
            st.image(ph_3)
            st.stop()
