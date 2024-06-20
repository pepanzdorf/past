from db_functions import load_all_data
from plots import *
from constants import *


all_data = load_all_data()

temperature_plots = main_temperature_plot(all_data)
temperature_plots.write_html("plots/temperature_histograms.html", full_html=False)

t_normal_table = temp_normal_table(all_data)
t_normal_table.write_html("plots/temp_normal_table.html", full_html=False)

t_hist_normal = histogram_normal_animation(all_data)
t_hist_normal.write_html("plots/temp_hist_normal.html", full_html=False, auto_play=False)

t_normals = plot_with_normal(all_data)
t_normals.write_html("plots/temp_normals.html", full_html=False)


def fill_template(template, contents):
    for key, value in contents.items():
        template = template.replace(key, value)

    return template


with open("template.html", "r") as f:
    template = f.read()

with open("plots/temperature_histograms.html", "r") as f:
    plot = f.read()

with open("texts/temp_text.html", "r") as f:
    text = f.read()

with open("texts/temp_text2.html", "r") as f:
    text2 = f.read()

with open("plots/temp_normal_table.html", "r") as f:
    table1 = f.read()

with open("plots/temp_hist_normal.html", "r") as f:
    hist_normal = f.read()

with open("plots/temp_normals.html", "r") as f:
    normals = f.read()

with open("weather_statistics.html", "w") as f:
    f.write(
        fill_template(
            template,
            {
                "{TEMP PLOT}": plot,
                "{TEMP TEXT}": text,
                "{TEMP TEXT 2}": text2,
                "{TEMP TABLE}": table1,
                "{TEMP HIST NORMAL}": hist_normal,
                "{TEMP NORMALS}": normals,
            },
        )
    )
