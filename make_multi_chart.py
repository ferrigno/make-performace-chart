import streamlit as st
#import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

properties = ['FOV', 'Sp. Resolution', 'En. Range', 'Location Accuracy', 'Duty Cycle']
# max_values = [4*np.pi, 0.1, 3e6, 3., 100.]
# min_values = [0.0, 0.15/6, 10.0, 1./3600., 0.0]
log_scale=[False, False, True, True, False]
invert_scale=[False, True, False, True, False]
helps = ['In steradians', '$\Delta E / E$', 'max - min', 'in degrees', 'in percent']

instruments = ['INTEGRAL', 'NuSTAR', 'Fermi/GBM' , 'Swift/BAT' ]
colors = ['blue', 'red', 'yellow', 'green']

default_colors = {}

for ii, cc in zip (instruments, colors):
    default_colors.update({ii:cc})

missions={
'INTEGRAL' : [  4*np.pi, 
  2.0/500.,
  2000.-75.,
  (3./60.),
  85.]
,
'Fermi/LAT':[2.4,
0.1,
3e6-20e3,
0.5/60,
60.]
,
'Fermi/GBM' : [9.5,
    0.1,
    30000.-8.,
    3.,
    60.]
,
'NuSTAR' : [(1./6.)**2, 
0.4 / 10.,
75.,
1.5/3600.,
60.]
,

'Swift/XRT':[(23.6/60.)**2,
0.15/6.,
10.,
2./3600.,
50.]
,
'Swift/BAT' : [1.4,
5./60.,
125.,
3/60.,
50.,
]
}

# NuSTAR:
# FoV (50% resp.): 10' at 10 keV, 6' at 68 keV
# Spectral Resolution (FWHM): 400 eV at 10 keV, 900 eV at 68 keV
# Energy Range: 3 - 78.4 keV
# Strong Source (>10σ) Positioning: 1.5" (1 σ)
# duty cycle of > 50%

# Fermi/LAT:
# Field of view: 2.4 steradians
# Energy Resolution       < 10%
# Energy Range    20 MeV - 300 GeV
# Source Location Determination   < 0.5'

# Fermi/GBM:
# Field of view: 9.5 steradians
# Energy Resolution (FWHM, 0.1-1 MeV), <10%
# Energy range: 8 keV to 40 MeV
# Gamma-ray burst localization: typical 3°
# Duty cycle ~60%

# Swift/XRT:
# FOV 23.6 x 23.6 arcmin
# resolution at launch was ∼140 eV at 6 keV, The resolution will degrade during the mission, but will remain above 300 eV at the end of the mission life for a worst-case environment
# Energy Range    0.2-10 keV
# few arcseconds source location accuracy

# Swift/BAT:
# Field of View   1.4 sr (> 50% partially-coded); 2.2 sr (> 20% partially-coded)
# Energy Resolution ∼5 keV@60 keV
# Energy Range    15-150 keV
# Position Centroid Accuracy 1-3 arcmin
# Similar to Fermi/GBM? 50-60%?

colors={'red': '#FF0000',
        'green': '#00FF00',
        'cyan':  '#00FFFF',
        'orange' : '#FD7120',
        'blue' : '#0000FF',
        'yellow': '#FFFF00'}

def make_skills(values, min_values, max_values):
    skills = {}
    
    for p, x, mi, ma, l, i in zip (properties, values, min_values, max_values, log_scale, invert_scale):

        if i:
            if l:
                y = np.abs(np.log10(x/ma/2))
                n = np.abs(np.log10(mi/ma/2))
            else:
                y = np.abs(x - ma*2)
                n = np.abs(mi - ma*2)
        else:
            if l:
                y = np.log10(x/mi*2)
                n = np.log10(ma/mi*2)
            else:
                y = x - mi/2
                n = ma - mi/2
        
        skills.update({p : y/n * 100})
        #print(x, mi, ma)
        #print(p, y, n, y/n * 100 )
    
    return pd.DataFrame([skills])


def radar_chart(selected_instruments, selected_colors, min_values, max_values, fill_area):

    GRAY = '#999999'

    angles = [i / float(len(properties)) * 2 * np.pi for i in range(len(properties))]

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

    for ss,cc in zip(selected_instruments, selected_colors):
        values=missions[ss]
        #print(ss)
        df = make_skills(values, min_values, max_values)

        series_values = df.loc[0] \
                    .values \
                    .flatten() \
                    .tolist()
    
        series.set_rlabel_position(0)
        series.plot(
            angles+[angles[0]],
            series_values+[series_values[0]],
            color=cc,
            linestyle='solid',
            linewidth=1, label=ss
            )
        if fill_area:
            series.fill(
                angles,
                series_values,
                color=cc,
                alpha=0.6
                )

    plt.legend(loc='upper right')

    st.pyplot(fig)

    return fig

def out(x):
    return "%.2f" % x

if __name__ == '__main__':
    st.title("Make a chart for your instruments")

    selected_instruments = st.multiselect('Select the instruments to display from the drop-down menu', missions.keys(), default=instruments)
    fill_area = st.checkbox("Check to fill the area", False)
    
    # st.write("Invert the scale for this property")
    # cols = (st.columns(len(properties)))
    # for i, (col, pp) in enumerate(zip(cols, properties)):
    #     with col:
    #         invert_scale[i] = st.checkbox(pp, invert_scale[i], key='invert_%d' % i )
    
    st.write("Use a log scale for this property")
    cols = (st.columns(len(properties)))
    for i, (col, pp) in enumerate(zip(cols, properties)):
        with col:
            log_scale[i] = st.checkbox(pp, log_scale[i], key='log_%d' % i)

    min_values = len(properties) * [1e10]
    max_values = len(properties) * [-1e10]
    
    for ss in selected_instruments:
        values = missions[ss]
        for i in range(len(properties)):
            if values[i] < min_values[i]:
                min_values[i] = values[i]
            if values[i] > max_values[i]:
                max_values[i] = values[i]

    st.write('Select the colors and adjust values')   
    selected_colors = []
    cols = (st.columns(len(selected_instruments)))
    for col,ss in zip(cols, selected_instruments):
#    for ss in selected_instruments:
        with col:
            default_color = 'cyan'
            if ss in default_colors:
                default_color = default_colors[ss]
            default_color = colors[default_color]
            color = st.color_picker(ss, default_color)
            selected_colors.append(color)
            values = missions[ss]
            for i, pp in enumerate(properties):               
                values[i] = st.number_input(pp, value=values[i], key=ss+pp, format="%.3f", help=helps[i])


    my_fig = radar_chart(selected_instruments, selected_colors, min_values, max_values, fill_area)

    but_html= st.button('create image to download')   #first button

    if but_html:
        fname = st.text_input("Filename", 'comparison.png' )
        with st.spinner('creating file...'):
          my_fig.savefig(fname)                 # function that creates the file
        
          with open(fname, 'rb') as exfile:
             st.download_button(              #second button
                label="download png file",
                data=exfile,
                file_name=fname,
                mime='image/png',
             )

