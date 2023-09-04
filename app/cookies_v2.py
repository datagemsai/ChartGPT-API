import os
from cryptography.fernet import Fernet, InvalidToken
from streamlit.components.v1 import html
import streamlit as st


def get_cookies() -> dict:
    # Use a unique key to ensure we're listening for the right event/data
    cookie_event_key = "cookie_event"

    # JavaScript to get cookies and send them back to Streamlit
    st.write(
        f"""
    <script>
        function getCookies() {{
            var pairs = document.cookie.split(";");
            var cookies = {{}};
            for (var i = 0; i < pairs.length; i++) {{
                var pair = pairs[i].split("=");
                cookies[(pair[0]+'').trim()] = unescape(pair.slice(1).join('='));
            }}
            return cookies;
        }}

        var cookies = getCookies();
        // Send the cookies back to Streamlit
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: cookies,
            key: '{cookie_event_key}'
        }}, "*");
    </script>
    """,
        unsafe_allow_html=True,
    )

    cookies = st.session_state.get(cookie_event_key, {})

    if cookies:
        decrypted_cookies = {}
        for name, encrypted_value in cookies.items():
            try:
                decrypted_value = decrypt_cookie(
                    encrypted_value, os.environ["COOKIES_PASSWORD"]
                )
                decrypted_cookies[name] = decrypted_value
            except InvalidToken:
                pass
        return decrypted_cookies
    else:
        return {}


def decrypt_cookie(encrypted_cookie, key):
    cipher_suite = Fernet(key)
    decrypted_cookie = cipher_suite.decrypt(encrypted_cookie.encode()).decode()
    return decrypted_cookie


def set_cookies(cookie_dict):
    script = """
    <script language="javascript">
        (function () {
    """

    for key, value in cookie_dict.items():
        encrypted_value = encrypt_cookie(value, os.environ["COOKIES_PASSWORD"])
        script += f"""
            document.cookie = "{key}={encrypted_value}; path=/;";
        """

    script += """
        })();
    </script>
    """
    html(script)


def encrypt_cookie(value, key):
    cipher_suite = Fernet(key)
    encrypted_cookie = cipher_suite.encrypt(value.encode()).decode()
    return encrypted_cookie


def delete_cookie(cookie_name):
    html(
        f"""
    <script language="javascript">
        (function () {{
            document.cookie = "{cookie_name}=; expires=Thu, 01-Jan-1970 00:00:01 GMT; path=/;";
        }})();
    </script>
    """
    )


def clear_cookies():
    html(
        f"""
    <script language="javascript">
        (function () {{
            var cookies = document.cookie.split("; ");
            for (var i = 0; i < cookies.length; i++) {{
                var cookie = cookies[i];
                var eqPos = cookie.indexOf("=");
                var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                document.cookie = name + "=; expires=Thu, 01-Jan-1970 00:00:01 GMT; path=/;";
            }}
        }})();
    </script>
    """
    )
    # html("""
    # <script language="javascript">
    #     (function () {
    #         var cookies = document.cookie.split("; ");
    #         for (var c = 0; c < cookies.length; c++) {
    #             var d = window.location.hostname.split(".");
    #             while (d.length > 0) {
    #                 var cookieBase = encodeURIComponent(cookies[c].split(";")[0].split("=")[0]) + '=; expires=Thu, 01-Jan-1970 00:00:01 GMT; domain=' + d.join('.') + ' ;path=';
    #                 var p = location.pathname.split('/');
    #                 document.cookie = cookieBase + '/';
    #                 while (p.length > 0) {
    #                     document.cookie = cookieBase + p.join('/');
    #                     p.pop();
    #                 };
    #                 d.shift();
    #             }
    #         }
    #     })();
    # </script>
    # """)
