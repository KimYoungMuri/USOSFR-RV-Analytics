"""
HTML table formatter for Swaption Vol Table with color coding
"""
import pandas as pd
import numpy as np
from datetime import date


def format_table_html(table: pd.DataFrame, as_of_date: date) -> str:
    """
    Format table as HTML with Nomura-style colors
    
    Args:
        table: Swaption vol table DataFrame
        as_of_date: Date of the table
        
    Returns:
        HTML string
    """
    html = f"""
    <style>
        .vol-table {{
            font-family: Arial, sans-serif;
            font-size: 11px;
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }}
        .vol-table th {{
            background-color: #D3D3D3;
            color: black;
            font-weight: bold;
            padding: 8px;
            text-align: center;
            border: 1px solid #999;
        }}
        .vol-table td {{
            padding: 6px;
            text-align: right;
            border: 1px solid #ddd;
        }}
        .vol-table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .vol-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .mover-cell {{
            background-color: #808080 !important;
            color: white !important;
            font-weight: bold !important;
        }}
        .section-header {{
            background-color: #E8E8E8 !important;
            font-weight: bold;
            text-align: center;
        }}
        .term-tenor {{
            text-align: left !important;
            font-weight: bold;
        }}
    </style>
    """
    
    # Build HTML table
    html += f'<h3>Vol Monitor – Swaption Vol Table</h3>'
    html += f'<p><strong>As of: {as_of_date}</strong></p>'
    html += '<table class="vol-table">'
    
    # Header row 1
    html += '<tr>'
    html += '<th rowspan="2" class="term-tenor">Term/Tenor</th>'
    html += '<th colspan="6" class="section-header">Implied Basis Point Volatility (Annualized)</th>'
    html += '<th colspan="6" class="section-header">Implied Basis Point Volatility (Daily)</th>'
    html += '<th colspan="6" class="section-header">Realized Basis Point Volatility (Daily)</th>'
    html += '</tr>'
    
    # Header row 2
    html += '<tr>'
    # Annualized headers
    for h in ['Current', '1d Chg', '1w Chg', '1m Chg', '20d High', '20d Low']:
        html += f'<th>{h}</th>'
    # Daily headers
    for h in ['Current', '1d Chg', '1w Chg', '1m Chg', '20d High', '20d Low']:
        html += f'<th>{h}</th>'
    # Realized headers
    for h in ['10d', '20d', '60d', '90d', '120d', '180d']:
        html += f'<th>{h}</th>'
    html += '</tr>'
    
    # Data rows
    for _, row in table.iterrows():
        html += '<tr>'
        
        # Term/Tenor
        html += f'<td class="term-tenor">{row["term_tenor"]}</td>'
        
        # Annualized data
        ann_data = [
            ('implied_vol_ann_current', False),
            ('implied_vol_ann_1d_chg', row.get('is_largest_1d_mover', False)),
            ('implied_vol_ann_1w_chg', row.get('is_largest_1w_mover', False)),
            ('implied_vol_ann_1m_chg', row.get('is_largest_1m_mover', False)),
            ('implied_vol_ann_20d_high', False),
            ('implied_vol_ann_20d_low', False),
        ]
        
        for col, is_mover in ann_data:
            val = row[col]
            cell_class = 'mover-cell' if is_mover else ''
            if pd.isna(val):
                html += f'<td class="{cell_class}"></td>'
            else:
                if val < 0:
                    formatted = f"({abs(val):.2f})"
                else:
                    formatted = f"{val:.2f}"
                html += f'<td class="{cell_class}">{formatted}</td>'
        
        # Daily data
        daily_data = [
            ('implied_vol_daily_current', False),
            ('implied_vol_daily_1d_chg', row.get('is_largest_1d_mover', False)),
            ('implied_vol_daily_1w_chg', row.get('is_largest_1w_mover', False)),
            ('implied_vol_daily_1m_chg', row.get('is_largest_1m_mover', False)),
            ('implied_vol_daily_20d_high', False),
            ('implied_vol_daily_20d_low', False),
        ]
        
        for col, is_mover in daily_data:
            val = row[col]
            cell_class = 'mover-cell' if is_mover else ''
            if pd.isna(val):
                html += f'<td class="{cell_class}"></td>'
            else:
                if val < 0:
                    formatted = f"({abs(val):.2f})"
                else:
                    formatted = f"{val:.2f}"
                html += f'<td class="{cell_class}">{formatted}</td>'
        
        # Realized data
        realized_cols = ['realized_vol_10d', 'realized_vol_20d', 'realized_vol_60d',
                         'realized_vol_90d', 'realized_vol_120d', 'realized_vol_180d']
        for col in realized_cols:
            val = row.get(col, np.nan)
            if pd.isna(val):
                html += '<td></td>'
            else:
                html += f'<td>{val:.2f}</td>'
        
        html += '</tr>'
    
    html += '</table>'
    
    # Notes
    html += '''
    <div style="margin-top: 20px; font-size: 10px; color: #666;">
        <p><strong>Notes on Color Coding:</strong></p>
        <p>Largest movers (dark gray cells): 1-day largest movers over 2 weeks; 1-week largest movers over 1 month; 1-month largest movers over 6 months</p>
    </div>
    '''
    
    return html
