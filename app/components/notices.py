import app
import streamlit as st
from PIL import Image
import app.settings


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

        if app.settings.check_maintenance_mode():
            st.warning("""
            **Offline for maintenance**

            This app is undergoing maintenance right now.
            Please check back later.

            In the meantime, [check out our landing page](https://chartgpt.***REMOVED***)!
            """)
            st.stop()
