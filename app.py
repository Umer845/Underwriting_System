import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
from PyPDF2 import PdfReader

def run_app():
    st.title("📋 Underwriter System")

    # ---- DB CONNECTION ----
    conn = psycopg2.connect(
        dbname="Underwritter",
        user="postgres",
        password="United2025",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # ---- SESSION ----
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = 1  # TEMP

    if 'active_page' not in st.session_state:
        st.session_state['active_page'] = "Upload File"

    # ---- Sidebar ----
    if st.sidebar.button("Upload File", key="nav_upload"):
        st.session_state['active_page'] = "Upload File"
    if st.sidebar.button("Risk Profile", key="nav_risk"):
        st.session_state['active_page'] = "Risk Profile"
    if st.sidebar.button("Premium Calculation", key="nav_premium"):
        st.session_state['active_page'] = "Premium Calculation"

    # ==========================
    # 🔍 Search + Next Block
    # ==========================

    # ---- Pages ----
    if st.session_state['active_page'] == "Upload File":
        st.subheader("Upload Vehicle Data")

        file_type = st.radio("Select file type", ["Excel (.xlsx)", "PDF (.pdf)"])
        uploaded_file = st.file_uploader("Choose file", type=['xlsx', 'pdf'])

        if uploaded_file is not None:
            if file_type == "Excel (.xlsx)":
                df = pd.read_excel(uploaded_file)
                st.write(df)

                if st.button("Save Excel to DB", key="save_excel"):
                    for _, row in df.iterrows():
                        cur.execute("""
                            INSERT INTO vehicle_inspection 
                            (user_id, client_name, model_year, make_name, sub_make_name, tracker_id, suminsured, clam_amount, grosspremium, netpremium, no_of_claims, vehicle_capacity)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            st.session_state['user_id'],
                            row['CLIENT_NAME'],
                            row['MODEL_YEAR'],
                            row['MAKE_NAME'],
                            row['SUB_MAKE_NAME'],
                            row['TRACKER_ID'],
                            row['SUMINSURED'],
                            row['CLM_AMOUNT'],
                            row['GROSSPREMIUM'],
                            row['NETPREMIUM'],
                            row['NO_OF_CLAIMS'],
                            row['VEHICLE_CAPACITY']
                        ))
                    conn.commit()
                    st.success("✅ Excel data inserted into vehicle_inspection!")

            elif file_type == "PDF (.pdf)":
                pdf = PdfReader(uploaded_file)
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                st.session_state['pdf_context'] = text
                st.success("✅ PDF uploaded and context saved for Q&A!")

        # =============================
        # 🔍 END Search + Next Block
        # =============================

        # ====================================
        # 🚦Risk Assesment Block (SAFE ✅)
        # ====================================

    elif st.session_state['active_page'] == "Risk Profile":
        st.subheader("Calculate Risk Profile")

        driver_age = st.number_input("Driver Age", min_value=18, max_value=100)
        make_name = st.text_input("Make Name", value="Proton")
        sub_make_name = st.text_input("Sub Make Name", value="Saga")
        model_year = st.number_input("Model Year", min_value=1990, max_value=datetime.now().year)

        if st.button("Calculate Risk", key="calc_risk"):
            if model_year == 2025:
                cur.execute("""
                    SELECT 
                        AVG(no_of_claims)::FLOAT, 
                        AVG(vehicle_capacity)::FLOAT
                    FROM vehicle_inspection
                    WHERE upper(make_name) = %s
                    AND upper(sub_make_name) = %s
                    AND model_year BETWEEN 2020 AND 2024
                    AND no_of_claims > 0
                """, (make_name.upper(), sub_make_name.upper()))
            else:
                cur.execute("""
                    SELECT 
                        AVG(no_of_claims)::FLOAT, 
                        AVG(vehicle_capacity)::FLOAT
                    FROM vehicle_inspection
                    WHERE upper(make_name) = %s
                    AND upper(sub_make_name) = %s
                    AND model_year = %s
                    AND no_of_claims > 0
                """, (make_name.upper(), sub_make_name.upper(), model_year))

            row = cur.fetchone()

            if row and row[0] is not None and row[1] is not None:
                avg_no_of_claims, avg_vehicle_capacity = row

                if driver_age < 25:
                    age_score = 1.0
                elif 25 <= driver_age <= 35:
                    age_score = 0.6
                elif 36 <= driver_age <= 55:
                    age_score = 0.4
                else:
                    age_score = 1.0

                if avg_vehicle_capacity <= 1000:
                    cap_score = 0.4
                elif 1001 <= avg_vehicle_capacity <= 1600:
                    cap_score = 0.6
                elif 1601 <= avg_vehicle_capacity <= 2000:
                    cap_score = 0.8
                else:
                    cap_score = 1.0

                if avg_no_of_claims < 2:
                    claim_score = 0.4
                elif 2 <= avg_no_of_claims <= 3:
                    claim_score = 0.6
                elif 4 <= avg_no_of_claims <= 5:
                    claim_score = 0.8
                else:
                    claim_score = 1.0

                total_score = age_score + cap_score + claim_score

                if total_score <= 1.8:
                    risk_level = "Low"
                elif 1.8 < total_score <= 2.4:
                    risk_level = "Low to Moderate"
                elif 2.4 < total_score < 3:
                    risk_level = "Moderate to High"
                else:
                    risk_level = "High"

                bg_color = {
                    "Low": "#32da32",
                    "Low to Moderate": "#d4c926",
                    "Moderate to High": "#26b4d4",
                    "High": "#dd2c2c"
                }[risk_level]

                st.info(f"""
                **Fetched Data:**
                - Vehicle Capacity: {avg_vehicle_capacity:.2f}
                - Average Number of Claims: {avg_no_of_claims:.2f}

                **Risk Scores:**
                - Age Score: {age_score}
                - Capacity Score: {cap_score}
                - Claims Score: {claim_score}

                **Total Score:** {total_score:.2f}
                """)

                st.markdown(f"""
                    <div style="background-color: {bg_color}; color: white; padding: 12px; border-radius: 6px;">
                        ✅ <b>Risk Level:</b> {risk_level}
                    </div>
                """, unsafe_allow_html=True)

                cur.execute("""
                    INSERT INTO vehicle_risk
                    (user_id, driver_age, make_name, sub_make_name, model_year, capacity, num_claims, risk_level, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (
                    st.session_state['user_id'],
                    driver_age,
                    make_name,
                    sub_make_name,
                    model_year,
                    avg_vehicle_capacity,
                    avg_no_of_claims,
                    risk_level,
                    datetime.now()
                ))
                risk_id = cur.fetchone()[0]
                conn.commit()
                st.session_state['risk_id'] = risk_id

                st.success("✅ Risk profile saved!")

            else:
                st.error("No matching data found with claims > 0!")

    # ==========================================
    # 🚦 END Risk Assesment Block (SAFE ✅)
    # ==========================================
    

    # ===================================
    # 🚗 Premium Rate Block (SAFE ✅)
    # ===================================

    elif st.session_state['active_page'] == "Premium Calculation":
        st.subheader("Calculate Premium")

        if 'risk_id' not in st.session_state:
            st.warning("⚠️ Please calculate risk profile first.")
        else:
            make_name = st.text_input("Make Name", key="premium_make")
            sub_make_name = st.text_input("Sub Make Name", key="premium_sub_make")
            model_year = st.number_input("Model Year", min_value=1990, max_value=2035, key="premium_year")

            if st.button("Calculate Premium", key="calc_premium"):
                if model_year == 2025:
                    cur.execute("""
                        WITH years AS (
                            SELECT 2020 AS year UNION ALL
                            SELECT 2021 UNION ALL
                            SELECT 2022 UNION ALL
                            SELECT 2023 UNION ALL
                            SELECT 2024
                        ),
                        yearly_sums AS (
                            SELECT
                                y.year,
                                COALESCE(SUM(vi.suminsured), 0) AS total_suminsured,
                                COALESCE(SUM(vi.netpremium), 0) AS total_netpremium
                            FROM years y
                            LEFT JOIN vehicle_inspection vi
                                ON vi.model_year = y.year
                                AND upper(vi.make_name) = %s
                                AND upper(vi.sub_make_name) = %s
                            GROUP BY y.year
                        )
                        SELECT
                            SUM(total_suminsured)::FLOAT / 4 AS avg_suminsured,
                            SUM(total_netpremium)::FLOAT / 4 AS avg_netpremium
                        FROM yearly_sums
                    """, (make_name.upper(), sub_make_name.upper()))
                    row = cur.fetchone()
                    if row and row[0] is not None and row[1] is not None:
                        avg_suminsured, avg_netpremium = row

                        base_premium_rate = (avg_netpremium / avg_suminsured) * 100

                        cur.execute("SELECT risk_level FROM vehicle_risk WHERE id = %s", (st.session_state['risk_id'],))
                        risk_level = cur.fetchone()[0]

                        if risk_level == "Low":
                            base_premium_rate += base_premium_rate + 0.10
                        elif risk_level == "Low to Moderate":
                            base_premium_rate += base_premium_rate + 0.15
                        elif risk_level == "Moderate to High":
                            base_premium_rate += base_premium_rate + 0.30
                        elif risk_level == "High":
                            base_premium_rate += base_premium_rate + 0.50

                        st.info(f"""
                        **2020–2024 Average Data:**
                        - Average Sum Insured: {avg_suminsured:.2f}
                        - Average Net Premium: {avg_netpremium:.2f}
                        - Risk Level: {risk_level}
                        """)

                        st.success(f"💰 Estimated 2025 Premium Rate: {base_premium_rate:.2f}%")

                        cur.execute("""
                            UPDATE vehicle_risk
                            SET premium_rate = %s
                            WHERE id = %s
                        """, (base_premium_rate, st.session_state['risk_id']))
                        conn.commit()
                        st.success("✅ Premium saved to vehicle_risk.")
                    else:
                        st.error("No valid data for 2020–2024 for this make/submake!")

                else:
                    cur.execute("""
                        SELECT suminsured, netpremium, tracker_id
                        FROM vehicle_inspection
                        WHERE upper(make_name) = %s
                        AND upper(sub_make_name) = %s
                        AND model_year = %s
                        ORDER BY id DESC LIMIT 1
                    """, (make_name.upper(), sub_make_name.upper(), model_year))
                    row = cur.fetchone()

                    if row:
                        suminsured, netpremium, tracker_id = row

                        cur.execute("SELECT risk_level FROM vehicle_risk WHERE id = %s", (st.session_state['risk_id'],))
                        risk_level = cur.fetchone()[0]

                        premium_rate_percent = (netpremium / suminsured) * 100

                        if risk_level == "Low":
                            premium_rate_percent += premium_rate_percent * 0.10
                        elif risk_level == "Low to Moderate":
                            premium_rate_percent += premium_rate_percent * 0.15
                        elif risk_level == "Moderate to High":
                            premium_rate_percent += premium_rate_percent * 0.30
                        elif risk_level == "High":
                            premium_rate_percent += premium_rate_percent * 0.50

                        if tracker_id and tracker_id > 0:
                            premium_rate_percent += premium_rate_percent * 0.05
                        else:
                            premium_rate_percent += premium_rate_percent * 0.10

                        st.info(f"""
                        **Fetched Data:**
                        - Sum Insured: {suminsured}
                        - Net Premium: {netpremium}
                        - Tracker ID: {tracker_id}
                        - Risk Level: {risk_level}
                        """)

                        st.success(f"💰 Final Premium Rate: {premium_rate_percent:.2f}%")

                        cur.execute("""
                            UPDATE vehicle_risk
                            SET premium_rate = %s
                            WHERE id = %s
                        """, (premium_rate_percent, st.session_state['risk_id']))
                        conn.commit()
                        st.success("✅ Premium saved to vehicle_risk.")
                    else:
                        st.error("No inspection data found!")

        # ========================================
        # 🚗 END Premium Rate Block (SAFE ✅)
        # ========================================

