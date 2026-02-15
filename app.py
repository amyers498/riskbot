import streamlit as st
import pandas as pd
import math

# --- Configuration & Page Setup ---
st.set_page_config(
    page_title="Futures Position Sizer",
    page_icon="chart_with_upwards_trend",
    layout="centered"
)

# --- FinTech Logic / Constants ---
# Asset specifications: Ticker -> Point Value (Multiplier)
ASSETS = {
    "MES (Micro S&P 500)": 5.0,
    "MNQ (Micro Nasdaq 100)": 2.0,
    "MGC (Micro Gold)": 10.0
}

def calculate_position_size(total_risk_dollars, stop_loss_points, point_value):
    """
    Calculates position size rounding down to the nearest whole contract.
    Formula: Floor(Total Risk / (Stop Points * Point Value))
    """
    if stop_loss_points <= 0 or point_value <= 0:
        return 0, 0.0
    
    risk_per_contract = stop_loss_points * point_value
    # We use math.floor to ensure we never exceed the dollar risk limit
    num_contracts = math.floor(total_risk_dollars / risk_per_contract)
    
    return int(num_contracts), risk_per_contract

# --- UI Layout ---
st.title("Futures Position Size Calculator")
st.markdown("Calculate contract size based on fixed dollar risk and technical stop loss.")

# Create a sidebar for account settings (Hypothetical Balance)
with st.sidebar:
    st.header("Account Settings")
    account_balance = st.number_input(
        "Hypothetical Account Balance ($)", 
        min_value=1000.0, 
        value=25000.0, 
        step=1000.0,
        help="Used to calculate risk percentage for safety warnings."
    )

# Main Input Section
col1, col2 = st.columns(2)

with col1:
    selected_asset_key = st.selectbox("Select Asset", options=list(ASSETS.keys()))
    point_value = ASSETS[selected_asset_key]
    st.caption(f"Point Value: ${point_value:.2f} per point")

with col2:
    risk_dollars = st.number_input("Total Dollar Risk ($)", min_value=10.0, value=300.0, step=10.0)
    stop_loss_points = st.number_input("Stop Loss (Points)", min_value=0.25, value=12.0, step=0.25)

st.divider()

# --- Calculation ---
contracts, risk_per_contract = calculate_position_size(risk_dollars, stop_loss_points, point_value)
actual_risk = contracts * risk_per_contract

# --- Results Display ---
st.subheader("Position Sizing")

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(label="Max Contracts", value=f"{contracts}")

with metric_col2:
    st.metric(label="Actual Risk ($)", value=f"${actual_risk:.2f}")

with metric_col3:
    risk_pct = (actual_risk / account_balance) * 100
    st.metric(label="Account Risk %", value=f"{risk_pct:.2f}%")

# --- Safety Warning ---
# Standard prop firm or conservative trading usually suggests risking 1-2% max
RISK_WARNING_THRESHOLD = 2.0 

if risk_pct > RISK_WARNING_THRESHOLD:
    st.error(f"⚠️ SAFETY WARNING: You are risking {risk_pct:.2f}% of your account balance. "
             f"Standard recommendation is below {RISK_WARNING_THRESHOLD}%.")
elif contracts == 0:
    st.warning("Risk is too tight for the selected stop loss. You cannot afford 1 contract.")
else:
    st.success("Risk is within acceptable parameters.")

# --- Profit Scenarios ---
if contracts > 0:
    st.subheader("Profit Scenarios (R:R)")
    
    scenarios = []
    for r_multiple in [1, 2, 3]:
        target_points = stop_loss_points * r_multiple
        potential_profit = contracts * target_points * point_value
        scenarios.append({
            "Risk:Reward": f"1:{r_multiple}",
            "Target (Points)": f"{target_points:.2f}",
            "Potential Profit ($)": f"${potential_profit:.2f}"
        })
    
    st.table(pd.DataFrame(scenarios))