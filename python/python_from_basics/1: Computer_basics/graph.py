import numpy as np
import plotly.graph_objects as go

# Data
x = np.linspace(0, 4 * np.pi, 500)
y1 = np.sin(x)
y2 = np.cos(x)

# Create figure
fig = go.Figure(
    data=[
        go.Scatter(x=x, y=y1, mode="lines", name="sin(x)",
                   line=dict(color="magenta", width=2.5)),
        go.Scatter(x=x, y=y2, mode="lines", name="cos(x)",
                   line=dict(color="cyan", width=2.5, dash="dash"))
    ],
    layout=go.Layout(
        title="🌈 Animated Sine & Cosine Waves 🎶",
        xaxis=dict(range=[0, 4*np.pi]),
        yaxis=dict(range=[-1.2, 1.2]),
        plot_bgcolor="#f0f8ff",
        paper_bgcolor="#e6f7ff",
        font=dict(size=14),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="▶ Play",
                    method="animate",
                    args=[
                        None,
                        {
                            "frame": {
                                "duration": 50,
                                "redraw": True},
                            "fromcurrent": True}]),
                dict(
                    label="⏸ Pause",
                    method="animate",
                    args=[
                        [None],
                        {
                            "frame": {
                                "duration": 0,
                                "redraw": False},
                            "mode": "immediate"}])
            ]
        )]
    ),
    frames=[go.Frame(
        data=[
            go.Scatter(x=x[:k], y=y1[:k], mode="lines",
                       line=dict(color="magenta", width=2.5)),
            go.Scatter(x=x[:k], y=y2[:k], mode="lines", line=dict(
                color="cyan", width=2.5, dash="dash"))
        ]
    ) for k in range(1, len(x), 5)]
)

fig.show()
