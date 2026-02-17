"""
Streamlit UI for Swaption Vol Table

Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.modules.get_swaption_table import get_swaption_table, get_swaption_table_latest, _load_data
from src.reporting.html_table_formatter import format_table_html

# Page config
st.set_page_config(
    page_title="Swaption Vol Table",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 14px;
        color: #666;
        margin-bottom: 20px;
    }
    .stDataFrame {
        font-size: 12px;
    }
    .mover-cell {
        background-color: #808080 !important;
        color: white !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">📊 Vol Monitor – Swaption Vol Table</p>', unsafe_allow_html=True)

# Sidebar for date input
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Date input
    vol_data, _ = _load_data()
    min_date = vol_data['date'].min()
    max_date = vol_data['date'].max()
    
    st.write(f"**Available date range:**")
    st.write(f"{min_date} to {max_date}")
    
    selected_date = st.date_input(
        "Select Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    st.write(f"**Selected:** {selected_date}")
    
    # Quick date buttons
    st.write("**Quick Select:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Latest"):
            selected_date = max_date
            st.rerun()
    with col2:
        if st.button("1 Week Ago"):
            from datetime import timedelta
            new_date = max_date - timedelta(days=7)
            if new_date >= min_date:
                selected_date = new_date
                st.rerun()
    
    st.markdown("---")
    st.write("**Info:**")
    st.write("• Dark gray cells = Largest movers")
    st.write("• Negative values in parentheses")
    st.write("• 20 swaption combinations shown")

# Load table
@st.cache_data
def load_table_for_date(as_of_date: date):
    """Load table for specific date (cached)"""
    return get_swaption_table(as_of_date)

try:
    with st.spinner(f"Loading table for {selected_date}..."):
        table = load_table_for_date(selected_date)
    
    st.markdown(f'<p class="sub-header">As of: {selected_date} | {len(table)} swaption combinations</p>', unsafe_allow_html=True)
    
    # Display formatted HTML table with colors
    html_table = format_table_html(table, selected_date)
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Show largest movers summary
    movers = table[
        table['is_largest_1d_mover'] | 
        table['is_largest_1w_mover'] | 
        table['is_largest_1m_mover']
    ]
    
    if len(movers) > 0:
        st.markdown("### 🔴 Largest Movers Summary")
        mover_summary = []
        for _, row in movers.iterrows():
            mover_types = []
            if row['is_largest_1d_mover']:
                mover_types.append("1d")
            if row['is_largest_1w_mover']:
                mover_types.append("1w")
            if row['is_largest_1m_mover']:
                mover_types.append("1m")
            mover_summary.append({
                'Term/Tenor': row['term_tenor'],
                'Largest Movers': ', '.join(mover_types)
            })
        st.dataframe(pd.DataFrame(mover_summary), use_container_width=True, hide_index=True)
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV download
        csv = table.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"swaption_vol_table_{selected_date}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel export button
        if st.button("📊 Export to Excel"):
            from src.modules.get_swaption_table import get_swaption_table_excel
            excel_file = get_swaption_table_excel(selected_date)
            st.success(f"✓ Excel file created: {excel_file}")
            st.info("Open the file to view Nomura-style formatting with color coding")
    
    # Notes
    st.markdown("---")
    st.markdown("**Notes on Color Coding:**")
    st.markdown("""
    - **Largest movers** (dark gray cells):
        - 1-day largest movers over 2 weeks
        - 1-week largest movers over 1 month  
        - 1-month largest movers over 6 months
    - **Negative values** shown in parentheses
    """)
    
except Exception as e:
    st.error(f"Error loading table: {e}")
    st.exception(e)
