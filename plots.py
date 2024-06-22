import math
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.stats import norm, ttest_ind, linregress
import numpy as np
from constants import *
import matplotlib.pyplot as plt


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
        for sensor in ["temperature_dht", "temperature_bmp280", "temperature_ds18b20"]:
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

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=["Měsíc", "Výběrový průměr", "Směrodatná odchylka (z výběrového rozptylu)"]),
                cells=dict(
                    values=[
                        list(MONTH_NAMES.values()),
                        [
                            f"{group['temperature_ds18b20'].mean():.2f}"
                            for _, group in by_months
                        ],
                        [
                            f"{group['temperature_ds18b20'].std(ddof=1):.2f}"
                            for _, group in by_months
                        ],
                    ]
                ),
            )
        ]
    )

    fig.update_layout(
        width=800,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig


def plot_with_normal(data):
    by_months = data.groupby(["month"])

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.1, 0.9],
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=0.02,
        horizontal_spacing=0.02,
    )

    cmap = plt.get_cmap('coolwarm')
    colors = [cmap(i) for i in np.linspace(0, 1, 12)]

    def rgba_to_rgb(rgba):
        return f'rgb({int(rgba[0] * 255)}, {int(rgba[1] * 255)}, {int(rgba[2] * 255)})'

    colors = [rgba_to_rgb(color) for color in colors]

    plot_data = [(month, group, np.mean(group["temperature_ds18b20"]), np.std(group["temperature_ds18b20"], ddof=1)) for month, group in by_months]
    plot_data.sort(key=lambda x: x[2])

    means = [mean for _, _, mean, _ in plot_data]

    for i, (month, group, mean, std) in enumerate(plot_data):
        x = np.arange(PLOT_START, PLOT_END, 0.001)
        y = norm.pdf(x, mean, std)
        # noinspection PyTypeChecker
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=f"{MONTH_NAMES[month[0]]} - normální rozdělení",
                marker_color=colors[i],
                hovertemplate='<b>%{fullData.name}</b><br>%{x:.2f}˚C<extra></extra>',
            ),
            row=2,
            col=1,
        )

    fig.add_trace(
        go.Scatter(
            x=means,
            y=[0] * len(means),
            mode='markers',
            marker=dict(
                size=10,
                color=colors,
            ),
            showlegend=False,
            hovertemplate='<b>%{text}</b><br>%{x:.2f}˚C<extra></extra>',
            text=[f"{MONTH_NAMES[month[0]]}" for month, _, _, _ in plot_data]
        ),
        row=1,
        col=1
    )

    fig.update_layout(
        title_text="Normální rozdělení teploty pro jednotlivé měsíce",
        showlegend=True,
        margin=dict(l=20, r=20, t=30, b=30),
        height=500,
    )

    return fig


def histogram_normal_animation(data):
    by_months = data.groupby(["month"])

    fig = go.Figure()

    cmap = plt.get_cmap('coolwarm')
    colors = [cmap(i) for i in np.linspace(0, 1, 12)]

    def rgba_to_rgb(rgba):
        return f'rgb({int(rgba[0] * 255)}, {int(rgba[1] * 255)}, {int(rgba[2] * 255)})'

    hist_colors = [rgba_to_rgb((np.array(color) + 0.1)) for color in colors]
    colors = [rgba_to_rgb(color) for color in colors]

    plot_data = [(month, group, np.mean(group["temperature_ds18b20"]), np.std(group["temperature_ds18b20"], ddof=1)) for
                 month, group in by_months]

    plot_data.sort(key=lambda x: x[2])

    month_names = [MONTH_NAMES[month[0]] for month, _, _, _ in plot_data]

    y_max = 0

    for i, (month, group, mean, std) in enumerate(plot_data):
        x = np.arange(PLOT_START, PLOT_END, 0.001)
        y = norm.pdf(x, mean, std)
        y_max = max(y_max, max(y))
        # noinspection PyTypeChecker
        fig.add_trace(
            go.Histogram(
                x=group["temperature_ds18b20"],
                name=f"{MONTH_NAMES[month[0]]}",
                histnorm="probability",
                xbins=dict(
                    start=PLOT_START, end=PLOT_END, size=1
                ),
                hovertemplate="%{x:.2f}˚C - %{y:.2f}",
                visible=False,
                showlegend=False,
                marker_color=hist_colors[i],
            ),
        )

        # noinspection PyTypeChecker
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=f"{MONTH_NAMES[month[0]]} - normální rozdělení",
                marker_color=colors[i],
                hovertemplate='<b>%{fullData.name}</b><br>%{x:.2f}˚C<extra></extra>',
                visible=False,
                showlegend=False,
            ),
        )

    base_frame = [
            go.Histogram(visible=False),
            go.Scatter(visible=False),
     ] * 12

    frames_data = [
        base_frame.copy()
        for _ in range(12)
    ]

    for i in range(12):
        frames_data[i][2 * i] = go.Histogram(visible=True)
        frames_data[i][2 * i + 1] = go.Scatter(visible=True)

    frames = [
        go.Frame(data=frames_data[i], name=f"frame_{i}")
        for i in range(12)
    ]

    fig.update(frames=frames)

    for k in range(len(fig.frames)):
        fig.frames[k]['layout'].update(title_text=month_names[k])

    animation_settings = dict(
        frame=dict(duration=1000, redraw=True),
        fromcurrent=True,
        mode='afterall',
        transition=dict(duration=0),
        loop=True
    )

    fig.update_layout(
        updatemenus=[{
            'type': 'buttons',
            'buttons': [
                {
                    'label': 'Spustit animaci',
                    'method': 'animate',
                    'args': [None, animation_settings]
                }
            ],
            'showactive': True
        }],
        xaxis=dict(range=[PLOT_START, PLOT_END]),
        yaxis=dict(range=[0, y_max]),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=30),
        height=500,
    )

    return fig


def december_vs_july(data):
    temperatures = data[["month", "temperature_ds18b20"]]
    temperatures = temperatures.dropna()

    return ttest_ind(temperatures[temperatures["month"] == 12]["temperature_ds18b20"],
                     temperatures[temperatures["month"] == 7]["temperature_ds18b20"], alternative="less")


def temp_vs_light(data):
    temp_light = data[["day", "year", "month", "temperature_ds18b20", "light_bh1750"]]
    temp_light = temp_light.dropna()

    temp_light = temp_light[(temp_light["day"] == 10) & (temp_light["month"] == 4) & (temp_light["year"] == 2024)]

    result = linregress(temp_light["light_bh1750"], temp_light["temperature_ds18b20"])
    print(f"temp_vs_light: {result}")

    fig = px.scatter(temp_light, x="light_bh1750", y="temperature_ds18b20", title="Korelace mezi teplotou a světlem",)

    fig.add_trace(go.Scatter(x=temp_light["light_bh1750"], y=result.intercept + result.slope * temp_light["light_bh1750"],
                             mode="lines", name="Lineární regrese", line=dict(color="red")))

    fig.update_layout(
        title_text="Korelace mezi teplotou a světlem",
        xaxis_title="Světlo (lux)",
        yaxis_title="Teplota (°C)",
    )

    return fig


def temp_vs_humidity(data):
    temp_hum = data[["day", "year", "month", "temperature_ds18b20", "humidity_dht"]]
    temp_hum = temp_hum.dropna()

    temp_hum = temp_hum[(temp_hum["day"] == 1) & (temp_hum["month"] == 1) & (temp_hum["year"] == 2023)]

    result = linregress(temp_hum["temperature_ds18b20"], temp_hum["humidity_dht"])
    print(f"temp_vs_humidity: {result}")

    fig = px.scatter(temp_hum, x="temperature_ds18b20", y="humidity_dht", title="Korelace mezi teplotou a vlhkostí")

    fig.add_trace(go.Scatter(x=temp_hum["temperature_ds18b20"], y=result.intercept + result.slope * temp_hum["temperature_ds18b20"],
                             mode="lines", name="Lineární regrese", line=dict(color="red")))

    fig.update_layout(
        title_text="Korelace mezi teplotou a vlhkostí",
        xaxis_title="Teplota (°C)",
        yaxis_title="Vlhkost (%)",
    )

    return fig

