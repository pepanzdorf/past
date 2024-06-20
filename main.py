from db_functions import load_all_data
from plots import *
from constants import *


all_data = load_all_data()

fig = main_temperature_plot(all_data)
fig.write_html("plots/temperature_histograms.html", full_html=False)

t_normal_table = temp_normal_table(all_data)
with open("plots/temp_normal_table.html", "w") as f:
    f.write(t_normal_table)


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

with open("weather_statistics.html", "w") as f:
    f.write(fill_template(template, {
        "{TEMP PLOT}": plot,
        "{TEMP TEXT}": text,
        "{TEMP TEXT 2}": text2,
        "{TEMP TABLE}": t_normal_table
                                     }))
