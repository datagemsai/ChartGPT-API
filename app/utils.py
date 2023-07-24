from streamlit.components.v1 import html
import streamlit as st


def copy_url_to_clipboard(url):
    """
    Copy a URL to the clipboard.
    """
    script= f"""
        <script type="text/javascript">
            // Copy the URL
            parent.navigator.clipboard.writeText(parent.location.origin + "{url}").then(() => {{
                alert("Copied the chart URL: " + parent.location.origin + "{url}");
            }})
            .catch(() => {{
                alert("Failed to copy the chart URL");
            }});
        </script>
    """
    html(script)
    st.session_state.question = ""

def open_page(url, target="_blank"):
    """
    Open a page in a new tab.
    """
    script = f"""
        <script type="text/javascript">
            // Open and focus window in new tab
            window.open('{url}', '{target}').focus();
        </script>
    """
    html(script)
    st.session_state.question = ""

def open_page_and_copy_url_to_clipboard(url, target="_blank"):
    """
    Open a page in a new tab and copy the URL to the clipboard.
    """
    open_page(url, target)
    copy_url_to_clipboard(url)
