import plotly 
import plotly.graph_objects as go

def create_radar_chart(stats_dict):
    # Standard MLB tools on a 0-100 scale (percentiles)
    categories = ['Exit Velo', 'Launch Angle', 'Hard Hit%', 'Barrel%', 'Zone Contact']

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[stats_dict['ev'], stats_dict['la'], stats_dict['hh'], stats_dict['br'], stats_dict['zc']],
        theta=categories,
        fill='toself',
        name='Player Profile',
        line_color='#1f77b4'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="Player Tool Percentiles"
    )
    return fig

# Display in Streamlit:
# st.plotly_chart(create_radar_chart(my_stats), use_container_width=True)


