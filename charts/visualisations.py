import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def payoff_diagram(S, K, premium, option_type='call', position='long'):
    """P&L at expiry across a range of spot prices"""
    spot_range = np.linspace(S * 0.7, S * 1.3, 300)

    if option_type == 'call':
        intrinsic = np.maximum(spot_range - K, 0)
    else:
        intrinsic = np.maximum(K - spot_range, 0)

    pnl = intrinsic - premium
    if position == 'short':
        pnl = -pnl

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spot_range, y=pnl,
        mode='lines', name='P&L at Expiry',
        line=dict(color='#00CC96', width=2)
    ))
    fig.add_hline(y=0, line_dash='dash', line_color='white', opacity=0.5)
    fig.add_vline(x=S, line_dash='dot', line_color='yellow',
                  annotation_text=f'Spot: {S:.0f}')
    fig.update_layout(
        title=f'{position.title()} {option_type.title()} P&L — Strike {K}',
        xaxis_title='Spot Price at Expiry',
        yaxis_title='P&L',
        template='plotly_dark',
        height=400
    )
    return fig


def volatility_skew(strikes, ivs, expiry_label, spot):
    """IV vs Strike chart — shows the smile/skew"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strikes, y=[iv * 100 for iv in ivs],
        mode='lines+markers', name=expiry_label,
        line=dict(color='#EF553B', width=2)
    ))
    fig.add_vline(x=spot, line_dash='dot', line_color='yellow',
                  annotation_text='ATM')
    fig.update_layout(
        title=f'Volatility Skew — {expiry_label}',
        xaxis_title='Strike',
        yaxis_title='Implied Volatility (%)',
        template='plotly_dark',
        height=400
    )
    return fig


def iv_surface(chain_data, spot):
    """3D IV surface across strikes and expiries"""
    strikes_all, expiries_all, ivs_all = [], [], []

    for i, (exp, data) in enumerate(chain_data.items()):
        calls = data['calls'].dropna(subset=['impliedVolatility'])
        calls = calls[(calls['strike'] > spot * 0.8) &
                      (calls['strike'] < spot * 1.2)]
        for _, row in calls.iterrows():
            strikes_all.append(row['strike'])
            expiries_all.append(i)          # numeric index for axis
            ivs_all.append(row['impliedVolatility'] * 100)

    fig = go.Figure(data=[go.Scatter3d(
        x=strikes_all, y=expiries_all, z=ivs_all,
        mode='markers',
        marker=dict(size=4, color=ivs_all, colorscale='Viridis',
                    colorbar=dict(title='IV %'))
    )])
    fig.update_layout(
        title='IV Surface',
        scene=dict(
            xaxis_title='Strike',
            yaxis_title='Expiry (index)',
            zaxis_title='IV (%)'
        ),
        template='plotly_dark',
        height=500
    )
    return fig