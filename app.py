import streamlit as st
import pandas as pd

from sanitizer import sanitize_excel

# Dummy user credentials
USER_CREDENTIALS = {"admin": "adminpw", "sanju": "sanjupw"}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# Hide Streamlit UI elements using CSS
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

def check_login(username, password):
    """Validate login credentials"""
    return USER_CREDENTIALS.get(username) == password


def add_footer():
    """Footer - Fixed at the bottom center"""
    st.markdown(
        """
        <style>
            .footer {
                position: fixed;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                text-align: center;
                font-size: 14px;
                color: gray;
            }
        </style>
        <div class="footer">© 2025 <b>MediXpert</b> by <b>Santu</b>. All rights reserved.</div>
        """,
        unsafe_allow_html=True,
    )


def login_page():
    """Centered and clean login form"""
    st.set_page_config(page_title="MediXpert Login")
    st.markdown(hide_st_style, unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .login-container {
            width: 320px;
            margin: auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            background-color: white;
            text-align: center;
        }
        .login-container, h2 {
            font-size: 22px;
            color: #007bff;
            text-align: center;
        }
        .stForm {
            border: none;
            width: 60%;
            border-radius: 5px;
            padding: 8px;
            margin-left: 20%
        }
        .stFormSubmitButton {
            width: 100%;
            margin-left: 35%;
        }
        .stButton button:hover {
            background-color: #04AA6D;
            color: white;
        }
        .footer {
            position: fixed;
            bottom: 10px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: gray;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h2 style='margin-top: 15%;'>MediXpert</h2>", unsafe_allow_html=True)

    with st.form('user_form', clear_on_submit = True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

    if submit_button:
        if check_login(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password")

    # st.markdown("</div>", unsafe_allow_html=True)
    add_footer()  # Add footer


def reports_sanitizer():
    """Reports Sanitizer Page"""
    st.set_page_config(page_title="Welcome to MediXpert")
    st.markdown(hide_st_style, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #007bff;'>Ledger Reports Sanitizer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Upload and sanitize your reports easily.</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

    uploaded_file = st.file_uploader("Upload a report", type=["xlsx", "csv"])
    # breakpoint()
    sanitize_file_path = ""

    if uploaded_file:
        st.success("File uploaded successfully!")
        if st.button("Sanitize Report"):
            sanitize_file_path = sanitize_excel(uploaded_file)
            st.success("Sanitization completed! You can now download your report.")

    if sanitize_file_path:
        with open(sanitize_file_path, "rb") as template_file:
            template_byte = template_file.read()
        st.download_button(
            label="Download Sanitize Report",
            data=template_byte,
            file_name="sanitized_report.xlsx",
            mime="application/vnd.ms-excel"
        )

    # Footer
    add_footer()  # Add footer


def main():
    """Main app logic"""
    if not st.session_state["logged_in"]:
        login_page()
    else:
        reports_sanitizer()


if __name__ == "__main__":
    main()
