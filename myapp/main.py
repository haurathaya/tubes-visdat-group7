import pandas as pd
import datetime as dt
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.models import CategoricalColorMapper
from bokeh.palettes import Spectral6
from bokeh.layouts import widgetbox, row, gridplot
from bokeh.models import DateRangeSlider, Select
from bokeh.models.widgets import Tabs, Panel

data = pd.read_csv('myapp/data/cinemaTicket_Ref.csv')

data['date']= pd.to_datetime(data['date']).dt.date
data["cinema_code_str"] = data["cinema_code"].astype(str)

cinemas = data[['cinema_code', 'date', 'total_sales', 'tickets_sold']].groupby(['cinema_code', 'date']).sum().reset_index()
films = data[['film_code', 'date', 'total_sales', 'tickets_sold']].groupby(['film_code', 'date']).sum().reset_index()
grouped = data[['cinema_code_str', 'total_sales', 'tickets_sold']].groupby(['cinema_code_str']).sum().sort_values(by='total_sales', ascending=False).head(5) / 1000000000

ints = cinemas['cinema_code'].value_counts().sort_index().index.tolist()
ints_film = films['film_code'].value_counts().sort_index().index.tolist()

source = ColumnDataSource(data={
    'cinema_code'       : cinemas[cinemas['cinema_code'] == 304]['cinema_code'],
    'date'              : cinemas[cinemas['cinema_code'] == 304]['date'],
    'tickets_sold'      : cinemas[cinemas['cinema_code'] == 304]['tickets_sold'],
    'total_sales'       : cinemas[cinemas['cinema_code'] == 304]['total_sales']/1000000000,
})

source_film = ColumnDataSource(data={
    'film_code'       : films[films['film_code'] == 1576]['film_code'],
    'date'              : films[films['film_code'] == 1576]['date'],
    'tickets_sold'      : films[films['film_code'] == 1576]['tickets_sold'],
    'total_sales'       : films[films['film_code'] == 1576]['total_sales']/1000000000,
})

source_top_cinema = ColumnDataSource(grouped)
cinema_codes = source_top_cinema.data['cinema_code_str'].tolist()

tooltips_cinema = [
            ('Cinema Code', '@cinema_code'),
            ('Date', '@date{%F}'),
            ('Total Sales', '@total_sales'),
            ('Tickets Sold', '@tickets_sold'),  
           ]

tooltips_film = [
            ('Film Code', '@film_code'),
            ('Date', '@date{%F}'),
            ('Total Sales', '@total_sales'),
            ('Tickets Sold', '@tickets_sold'),  
           ]

tooltips_cinema_vbar = [
            ('Cinema Code', '@cinema_code_str'),
            ('Total Sales', '@total_sales'),
            ('Tickets Sold', '@tickets_sold'),  
           ]

fig_cinema = figure(x_axis_type='datetime',
             plot_height=500, plot_width=1000,
             title='Cinema 304 Total Sales in 2018',
             x_axis_label='Date', y_axis_label='Total Sales (Triliun)')

fig_film = figure(x_axis_type='datetime',
             plot_height=500, plot_width=1000,
             title='Film 304 Total Sales in 2018',
             x_axis_label='Date', y_axis_label='Total Sales (Triliun)')

fig_cinema_vbar = figure(plot_height=500, plot_width=500,
                title='Top 5 Cinemas by Total Sales in 2018', x_range=cinema_codes,
                x_axis_label='Cinema Code', y_axis_label='Total Sales (Triliun)',
                toolbar_location=None)

fig_cinema.add_tools(HoverTool(tooltips=tooltips_cinema, formatters={'@date': 'datetime'}))

fig_film.add_tools(HoverTool(tooltips=tooltips_film, formatters={'@date': 'datetime'}))

fig_cinema_vbar.add_tools(HoverTool(tooltips=tooltips_cinema_vbar))

fig_cinema.line('date', 'total_sales', 
         color='#CE1141', 
         source=source)

fig_film.line('date', 'total_sales', 
         color='#000000', 
         source=source_film)

fig_cinema_vbar.vbar(x='cinema_code_str', top='total_sales', source=source_top_cinema, width=0.50)

fig = figure(x_axis_type='datetime',
            plot_height=500, plot_width=800,
            title='Trend of Top 5 Cinemas by Total Sales in 2018',
            x_axis_label='Date', y_axis_label='Total Sales',
            toolbar_location=None)

color_list = ['#212121', '#b83b5e', '#3fc1c9', '#3490de', '#f9ed69']
idx = 0
for i in grouped.index:
    i = int(i)
    source_ = ColumnDataSource(data={
        'cinema_code'       : cinemas[cinemas['cinema_code'] == i]['cinema_code'],
        'date'              : cinemas[cinemas['cinema_code'] == i]['date'],
        'tickets_sold'      : cinemas[cinemas['cinema_code'] == i]['tickets_sold'],
        'total_sales'       : cinemas[cinemas['cinema_code'] == i]['total_sales']/1000000000,
    })

    fig.line('date', 'total_sales', 
         color=color_list[idx], legend_label='Cinema'+str(i), 
         source=source_, muted_alpha=0.1)
    
    idx += 1

fig.legend.location = 'top_left'
fig.legend.click_policy = 'mute'
                                   
cinema_gridplot = gridplot([[fig_cinema_vbar, fig]], toolbar_location='right')

def update_cinema(attr, old, new):

    [start, end] = slider.value
    date_from = dt.datetime.fromtimestamp(start/1000.0).date()
    date_until = dt.datetime.fromtimestamp(end/1000.0).date()

    cinema_cd = int(cinema_select.value)

    # new data
    cinema_date = cinemas[(cinemas['date'] >= date_from) & (cinemas['date'] <= date_until)]
    new_data = {
        'cinema_code'       : cinema_date[cinema_date['cinema_code'] == cinema_cd]['cinema_code'],
        'date'              : cinema_date[cinema_date['cinema_code'] == cinema_cd]['date'],
        'tickets_sold'      : cinema_date[cinema_date['cinema_code'] == cinema_cd]['tickets_sold'],
        'total_sales'       : cinema_date[cinema_date['cinema_code'] == cinema_cd]['total_sales']/1000000000,
    }
    source.data = new_data

    fig_cinema.title.text = 'Total Sales Cinema '+cinema_select.value+ ' in 2018'


init_value = (data['date'].min(), data['date'].max())
slider = DateRangeSlider(start=init_value[0], end=init_value[1], value=init_value)
slider.on_change('value',update_cinema)

cinema_select = Select(
    options= [str(x) for x in ints],
    value= '304',
    title='Cinema Code'
)
cinema_select.on_change('value', update_cinema)

def update_film(attr, old, new):

    [start, end] = slider_film.value
    date_from = dt.datetime.fromtimestamp(start/1000.0).date()
    date_until = dt.datetime.fromtimestamp(end/1000.0).date()

    film_cd = int(film_select.value)

    # new data
    films_date = films[(films['date'] >= date_from) & (films['date'] <= date_until)]
    new_data = {
        'film_code'       : films_date[films_date['film_code'] == film_cd]['film_code'],
        'date'              : films_date[films_date['film_code'] == film_cd]['date'],
        'tickets_sold'      : films_date[films_date['film_code'] == film_cd]['tickets_sold'],
        'total_sales'       : films_date[films_date['film_code'] == film_cd]['total_sales']/1000000000,
    }
    source_film.data = new_data

    fig_film.title.text = 'Total Sales Film '+film_select.value+ ' in 2018'

slider_film = DateRangeSlider(start=init_value[0], end=init_value[1], value=init_value)
slider_film.on_change('value',update_film)

film_select = Select(
    options= [str(x) for x in ints_film],
    value= '1576',
    title='Film Code'
)
film_select.on_change('value', update_film)

# Create layout and add to current document
layout = row(widgetbox(cinema_select, slider), fig_cinema)
layout_film = row(widgetbox(film_select, slider_film), fig_film)

first_panel = Panel(child=layout, title='Cinema\'s by Sales')
second_panel = Panel(child=layout_film, title='Film\'s by Sales')
third_panel = Panel(child=cinema_gridplot, title='Top Cinema\'s by Sales')

tabs = Tabs(tabs=[first_panel, second_panel, third_panel])

curdoc().add_root(tabs)