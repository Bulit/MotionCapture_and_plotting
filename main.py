from capture import df
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource
import pandas
# Add this 2 line to suppress FutureWarning from pandas about using .append method
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

df["Start"] = pandas.to_datetime(df["Start"])
df["End"] = pandas.to_datetime(df["End"])

df['Start_string'] = df['Start'].dt.strftime('%Y-%M-%D %H:%M:%S')
df['End_string'] = df['End'].dt.strftime('%Y-%M-%D %H:%M:%S')

cds = ColumnDataSource(df)

p = figure(x_axis_type = 'datetime', height = 100, width = 500, sizing_mode = 'scale_width' ,title = 'MotionGraph')
# remove y-axis grid
p.yaxis.minor_tick_line_color = None
# remove y-axis tick number
p.yaxis[0].ticker.desired_num_ticks=1
# add HooverTool info after hovering on our quad
hover = HoverTool(tooltips = [('Start', '@Start_string'),('End', '@End_string')])
p.add_tools(hover)

g = p.quad(left = 'Start', right = 'End', bottom = 0, top = 1, source = cds)

output_file('MotionGraph.html')

show(p)