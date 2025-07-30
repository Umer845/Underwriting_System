import streamlit as st
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash, check_password_hash
import app
import dashboard
import qa

# ✅ ---- Inject custom CSS ----
st.markdown("""
<style>
.st-emotion-cache-umot6g {
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 400;
    padding: 12px 16px;
    border-radius: 0.5rem;
    min-height: 2.5rem;
    margin: 0px 0px 0.5rem 0px;
    line-height: 1.6;
    text-transform: none;
    font-size: inherit;
    font-family: inherit;
    color: inherit;
    width: 100%;
    cursor: pointer;
    user-select: none;
    background-color: rgb(43, 44, 54);
    border: 1px solid rgba(250, 250, 250, 0.2);
}

.st-emotion-cache-umot6g:hover {
    border-color: #14C76D;
    color: #14C76D;
}
.st-emotion-cache-umot6g:active {
    color: #14C76D;
    border-color: #14C76D;
    background-color: transparent;
}
.st-emotion-cache-z8vbw2 {
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 400;
    padding: 12px 16px;
    border-radius: 0.5rem;
    min-height: 2.5rem;
    margin: 0px;
    line-height: 1.6;
    text-transform: none;
    font-size: inherit;
    font-family: inherit;
    color: inherit;
    width: auto;
    cursor: pointer;
    user-select: none;
    background-color: rgb(19, 23, 32);
    border: 1px solid rgba(250, 250, 250, 0.2);
}
.st-emotion-cache-z8vbw2:hover {
    border-color: #14C76D;
    color: #14C76D;
}


</style>
""", unsafe_allow_html=True)

# ✅ ---- DB CONNECTION ----
conn = psycopg2.connect(
    dbname="Underwritter",
    user="postgres",
    password="United2025",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ✅ ---- SESSION ----
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'active_page' not in st.session_state:
    st.session_state['active_page'] = "Upload File"  # Default page after login

# ✅ ---- Sidebar ----
if not st.session_state['logged_in']:
    st.sidebar.title("🔒 Auth")

    if st.sidebar.button("Login"):
        st.session_state['active_page'] = "Login"
    if st.sidebar.button("Register"):
        st.session_state['active_page'] = "Register"

    if st.session_state['active_page'] == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login Now"):
            cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            if result and check_password_hash(result[1], password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['user_id'] = result[0]
                st.session_state['active_page'] = "Upload File"
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    elif st.session_state['active_page'] == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        cnic = st.text_input("CNIC")
        make_name = st.text_input("Make Name")
        if st.button("Register Now"):
            hashed_pw = generate_password_hash(password)
            try:
                cur.execute(
                    sql.SQL("INSERT INTO users (username, password, cnic, make_name) VALUES (%s, %s, %s, %s)"),
                    [username, hashed_pw, cnic, make_name]
                )
                conn.commit()
                st.success("✅ Registered successfully.")
            except Exception as e:
                st.error(f"Error: {e}")

else:
    st.sidebar.title("📋 Navigation")

    if st.session_state['active_page'] == "Upload File":
        app.run_app()
    elif st.session_state['active_page'] == "Risk Profile":
        app.run_app()
    elif st.session_state['active_page'] == "Premium Calculation":
        app.run_app()
    if st.sidebar.button("Dashboard"):
        st.session_state['active_page'] = "Dashboard"
    if st.sidebar.button("Question Answer"):
        st.session_state['active_page'] = "Question Answer"
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.success("✅ Logged out")
        st.rerun()

    # ✅ ---- Render correct page ----
   
    elif st.session_state['active_page'] == "Dashboard":
        dashboard.show_dashboard()
    elif st.session_state['active_page'] == "Question Answer":
        qa.show_question_answer(cur)
