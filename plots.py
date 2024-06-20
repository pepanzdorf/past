import math
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.stats import norm
import numpy as np
from constants import *


def main_temperature_plot(data):
    by_months = data.groupby(["month"])

    num_subplots = len(by_months)

    # Create subplots
    fig = make_subplots(
        rows=math.ceil(num_subplots / 2),
        cols=2,
        subplot_titles=[f"{MONTH_NAMES[month]}" for month in by_months.groups.keys()],
        vertical_spacing=0.04,
        shared_xaxes=True,
    )

    # Add histograms to subplots
    for i, (month, group) in enumerate(by_months, start=1):
        for sensor in ["temperature_dht", "temperature_ds18b20", "temperature_bmp280"]:
            if group[sensor].notna().sum() >= 1000:  # Skip if there are not enough data

                # noinspection PyTypeChecker
                fig.add_trace(
                    go.Histogram(
                        x=group[sensor],
                        name=f"{MONTH_NAMES[month[0]]} - {sensor}",
                        histnorm="probability",
                        xbins=dict(  # bins used for histogram
                            start=PLOT_START, end=PLOT_END, size=1
                        ),
                        marker_color=(
                            "red"
                            if sensor == "temperature_dht"
                            else (
                                "blue"
                                if sensor == "temperature_ds18b20"
                                else "lawngreen"
                            )
                        ),
                        hovertemplate="%{x:.2f}˚C - %{y:.2f}",
                    ),
                    row=math.ceil(i / 2),
                    col=i % 2 + 1,
                )

                # x = np.arange(PLOT_START, PLOT_END, 0.001)
                # y = norm.pdf(x, np.mean(group[sensor]), np.std(group[sensor], ddof=1))
                # # noinspection PyTypeChecker
                # fig.add_trace(
                #     go.Scatter(
                #         x=x,
                #         y=y,
                #         mode="lines",
                #         name=f"{MONTH_NAMES[month[0]]} - {sensor} - normální rozdělení",
                #         marker_color=(
                #             "red"
                #             if sensor == "temperature_dht"
                #             else (
                #                 "blue"
                #                 if sensor == "temperature_ds18b20"
                #                 else "lawngreen"
                #             )
                #         ),
                #     ),
                #     row=math.ceil(i / 2),
                #     col=i % 2 + 1,
                # )

        fig.update_xaxes(
            range=[PLOT_START, PLOT_END],
            title_text="Teplota (°C)",
            row=math.ceil(i / 2),
            col=i % 2 + 1,
            showticklabels=True,
        )

    # Show the legend only once
    # Update layout
    fig.update_traces(opacity=0.75)
    fig.update_layout(
        height=400 * math.ceil(num_subplots / 2),
        autosize=False,
        width=1600,
        title_text="Histogramy teploty pro jednotlivé měsíce",
        showlegend=True,
        barmode="overlay",
    )

    return fig


def temp_normal_table(data):
    by_months = data.groupby(["month"])

    fig = go.Figure(data=[go.Table(header=dict(values=["Měsíc", "Výběrový průměr", "Výběrový rozptyl", "Min", "Max"]),
                             cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
                    ])

    return fig
