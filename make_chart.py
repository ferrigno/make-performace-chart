import streamlit as st
#import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

properties = ['FOV', 'Sp. Resolution', 'En. Range', 'Location Accuracy', 'Duty Cycle']
max_values = [4*np.pi, 1.0, 1e4, 90., 100.]
min_values = [0.0, 0.001, 10.0, 0.6/3600., 0.0]
log_scale=[False, False, True, False, False]
invert_scale=[False, True, False, True, False]
helps = ['In steradians', '$\Delta E / E$', 'max - min', 'in degrees', 'in percent']

colors={'red': '#FF0000',
        'green': '#00FF00',
        'cyan':  '#00FFFF',
        'orange' : '#FD7120',
        'blue' : '#00BFFF'}



def make_skills(values):
    skills = {}
    
    for p, x, mi, ma, l, i in zip (properties, values, min_values, max_values, log_scale, invert_scale):

        if i:
            y = x - ma
            n = mi - ma
        else:
            y = x - mi
            n = ma - mi
        
        skills.update({p : y/n * 100})
    
    return pd.DataFrame([skills])


def radar_chart(values, title,color):

    GRAY = '#999999'

    angles = [i / float(len(properties)) * 2 * np.pi for i in range(len(properties))]

    df = make_skills(values)

    #fig = px.line_polar(df, r='r', theta='theta', line_close=True)

    fig, series = plt.subplots(1, subplot_kw=dict(projection='polar'))

    plt.xticks(angles, properties, color=GRAY, size=8)

    plt.yticks(
     [20, 40, 60, 80],
     ['20', '40', '60', '80'],
     color=GRAY,
     size=7
    )
    plt.ylim(0,100)

    series_values = df.loc[0] \
                    .values \
                    .flatten() \
                    .tolist()
    
    series.set_rlabel_position(0)
    series.plot(
        angles,
        series_values,
        color=colors[color],
        linestyle='solid',
        linewidth=1, label=title
        )
    series.fill(
        angles,
        series_values,
        color=colors[color],
        alpha=0.6
        )

    plt.legend()

    st.pyplot(fig)

    return fig

def out(x):
    return "%.2f" % x

if __name__ == '__main__':
    st.write("Make a chart for your instrument")
    title = st.text_area("Instrument", height=1, max_chars=128, help="Your instrument")
    color = st.select_slider('Color', colors.keys(), help='The color of the bar chart')
    values = np.zeros(len(properties))
    for i, (tt, mi, ma, l, h) in enumerate(zip(properties, min_values, max_values, log_scale, helps)):
        if l:
            input_values = 10**np.linspace(float(np.log10(mi)), float(np.log10(ma)), 100)
            val = st.select_slider(tt, input_values, value=input_values[50], format_func=out, help=h )
        else:
            val = st.slider(tt, mi, ma,(mi+ma)/2, help=h)
        values[i] = val
    my_fig = radar_chart(values, title, color)

    but_html= st.button('create image to download')   #first button

    if but_html:
        with st.spinner('creating file...'):
          fname = title+'.png'
          my_fig.savefig(fname)                 # function that creates the file
        
          with open(fname, 'rb') as exfile:
             st.download_button(              #second button
                label="download png file",
                data=exfile,
                file_name=fname,
                mime='image/png',
             )

