"""
Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED
This file is part of "The Stress App" project and is released under the 
GNU Affero General Public License v3.0 (AGPL-3.0)
See the GNU Affero General Public License for more details: <https://www.gnu.org/licenses/agpl-3.0.html>
"""

import streamlit as st
import pandas as pd
import numpy as np
import pint
from welly import Well
from welly import Curve

import stresslog as lsd


from common_functions import create_well_log_plot, resample_well, getwelldev, load_aliases, save_aliases, get_missing_aliases, get_df_from_user
from _4_I_mob import mobile_import
import random

# Streamlit implementation



# Set page config to wide mode



# Initialize session state for aliases
if 'aliases' not in st.session_state:
    st.session_state.aliases = load_aliases()

if 'alias' not in st.session_state:
    st.session_state.alias = load_aliases()#st.session_state.aliases
    
if 'aliasState' not in st.session_state:
    st.session_state.aliasState = False # All critical aliases set correctly
# Set up session state for curve data
if 'curve_data' not in st.session_state:
    st.session_state.curve_data = None
if 'las_file' not in st.session_state:
    st.session_state.las_file = None
if 'wellobj' not in st.session_state:
    st.session_state.wellobj = None
if 'data_array' not in st.session_state:
    st.session_state.data_array = [None,None,None,None,None,None,None,None,None]#Dev,Forms,Flags,Litho,Image,UCS,RFT,MINIFRAC,Drilling
if 'custom_tracks' not in st.session_state:
    st.session_state.custom_tracks = []
if 'track_curve_ranges' not in st.session_state:
    st.session_state.track_curve_ranges = []
if 'curve_properties' not in st.session_state:
    st.session_state.curve_properties = {}
if 'track_grids' not in st.session_state:
    st.session_state.track_grids = []
if 'mudattributedf' not in st.session_state:
    st.session_state.mudattributedf = None



vert_height = 685
st.session_state.refresher=False



custom_tracks = []
track_curve_ranges = []
curve_properties = {}
track_grids = []




#with st.sidebar:
#@st.dialog("Aliases and Check Plot Config")
if st.session_state.las_file is None:
    st.session_state.las_file = st.file_uploader("Upload a LAS file", type=["las"])
    if st.button("No Las? No Problem",use_container_width=True):
        righeight=random.randint(7,75)
        gl=random.randint(-1000,1000)
        if gl<0:
            kb = righeight
        else:
            kb = gl+righeight
        ad,cb,stringer = lsd.create_random_las(kb=kb,gl=gl,drop=['RHOB'])
        st.session_state.las_file = stringer


        st.write("Created random las file")
    banner = """
        <link href="https://fonts.googleapis.com/css2?family=Orbitron&family=Oxanium:wght@400&display=swap" rel="stylesheet">
        <style>
            .banner-container {
                text-align: center;
            }
            .banner-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 4vw; /* Dynamically adjusts to 4% of the viewport width */
                color: rgba(128, 128, 128, 0.5);
                margin: 0;
            }
            .banner-subtitle {
                font-family: 'Oxanium', sans-serif;
                font-size: 8vw; /* Dynamically adjusts to 8% of the viewport width */
                color: rgba(128, 128, 128, 0.5);
                margin: 0;
            }
            .banner-version {
                font-family: 'Oxanium', sans-serif;
                font-size: 2vw; /* Dynamically adjusts to 2% of the viewport width */
                color: rgba(128, 128, 128, 0.5);
                margin: 0;
            }

            /* Media queries for fine-tuning */
            @media (max-width: 600px) {
                .banner-title {
                    font-size: 5vw;
                }
                .banner-subtitle {
                    font-size: 10vw;
                }
                .banner-version {
                    font-size: 3vw;
                }
            }

            @media (min-width: 1200px) {
                .banner-title {
                    font-size: 60px; /* Fixed size for larger screens */
                }
                .banner-subtitle {
                    font-size: 120px;
                }
                .banner-version {
                    font-size: 30px;
                }
            }
        </style>
        <div class="banner-container">
            <div class="banner-title">ROCK LAB</div>
            <div class="banner-subtitle">The Stress App</div>
            <div class="banner-version">stresslog v1.1.3</div>
        </div>
        """

    # Use Streamlit to display the HTML
    st.markdown(banner, unsafe_allow_html=True)
    if st.session_state.las_file is not None:
        st.rerun()
else:
    if st.session_state.mobile_version:
        mobile_import()
    else:
        # Plot container
        cols = st.columns([1,2])
        with cols[0]:
            with st.container(height=719):
                st.title("WELL DATA QC")

                if st.session_state.las_file is not None:
                    #st.session_state.las_file = uploaded_file
                    # Pass the file-like object directly to Well.from_las()
                    try:
                        byteme = st.session_state.las_file.getvalue()
                        string_data = byteme.decode('utf-8', errors='replace')
                    except:
                        string_data = st.session_state.las_file.getvalue()
                    well = Well.from_las(string_data)
                    st.session_state.wellobj = well
                    st.session_state.curve_data = well.df()
                    curves = st.session_state.wellobj.df()
                    
                    with st.container():
                        # Evaluate required aliases before drawing the widget
                        curves_list = list(st.session_state.curve_data)
                        aliases = st.session_state.aliases
                        result_dict = {}
                        no_match_keys = []

                        # Process each alias group
                        for key, alias_group in aliases.items():
                            match = next((curve for curve in alias_group if curve in curves_list), 'None')
                            result_dict[key] = match
                            if match == "None" or match is None:
                                no_match_keys.append(key)
                        missing_aliases = no_match_keys

                        # Conditions for required aliases
                        single_aliases = ["sonic", "resdeep"]  # These should be set individually
                        group_aliases = ["WOB", "ROP", "RPM", "ECD"]  # All of these should be set together

                        is_sonic_set = result_dict.get("sonic") not in ["None", None]
                        is_resdeep_set = result_dict.get("resdeep") not in ["None", None]
                        is_group_set = all(result_dict.get(alias) not in ["None", None] for alias in group_aliases)

                        # Dynamically set expanded state
                        alias_expanded = not (is_sonic_set or is_resdeep_set or is_group_set)
                        st.session_state.aliasState = not alias_expanded
                        with st.expander("Aliases", expanded=alias_expanded):
                            for alias in aliases.keys():
                                current_selection = st.session_state.aliases.get(alias, [])
                                new_selection = st.multiselect(
                                    f"Select curve for {alias.upper()}",
                                    options=["None"] + list(st.session_state.curve_data.columns),
                                    default=[
                                        value
                                        for value in st.session_state.aliases.get(alias, ["None"])
                                        if value in ["None"] + list(st.session_state.curve_data.columns)
                                    ],
                                )
                                updated_selection = list(set(current_selection + new_selection))
                                st.session_state.aliases[alias] = updated_selection

                            # Save updated aliases to JSON
                            save_aliases(st.session_state.aliases)

                            st.session_state.alias = result_dict
                            st.write(st.session_state.alias)
                        #uploaded_file = st.file_uploader("Upload a LAS file", type=["las"])
                        #uploaded_file = st.session_state.las_file+
                        
                        neutron2 = st.session_state.wellobj.data[st.session_state.alias['neutron']].values

                        default_tracks = [[st.session_state.alias['gr']],
                                          [st.session_state.alias['resdeep'],st.session_state.alias['resshal']],
                                          [st.session_state.alias['sonic'],st.session_state.alias['neutron'],st.session_state.alias['density']]
                        ]
                        #st.write(default_tracks)
                        default_curve_ranges = [{st.session_state.alias['gr']:{"left":0,"right":150}},
                                                {st.session_state.alias['resdeep']:{"left":0.02,"right":200},
                                                 st.session_state.alias['resshal']:{"left":0.02,"right":200}},
                                                {st.session_state.alias['density']:{"left":1.8,"right":2.8},
                                                 st.session_state.alias['neutron']:{"left":0.54,"right":-0.06} if np.nanmean(neutron2)<1 else {"left":54.0,"right":-6.0},
                                                 st.session_state.alias['sonic']:{"left":140,"right":40}}
                        ]
                        default_curve_properties = {st.session_state.alias['gr']:{"color":"#276b02","thickness":2.0,"line_style":"solid","logarithmic":False},
                                                    st.session_state.alias['resdeep']:{"color":"#818181","thickness":1.5,"line_style":"solid","logarithmic":True},
                                                    st.session_state.alias['resshal']:{"color":"#c71b1b","thickness":1.5,"line_style":"dashdot","logarithmic":True},
                                                    st.session_state.alias['density']:{"color":"#b9602e","thickness":2.0,"line_style":"solid","logarithmic":False},
                                                    st.session_state.alias['neutron']:{"color":"#1c34aa","thickness":1.0,"line_style":"dot","logarithmic":False},
                                                    st.session_state.alias['sonic']:{"color":"#818181","thickness":1.5,"line_style":"solid","logarithmic":False}
                        }
                        
                        if 'curve_data' in st.session_state and st.session_state.curve_data is not None:
                            #st.subheader("Visualization Settings")
                            
                            available_curves = list(st.session_state.curve_data.columns)
                            try:
                                available_curves.remove('DEPT')
                            except:
                                pass
                            with st.expander("Track Configuration", expanded=False):
                                num_tracks = st.number_input("Number of Tracks", min_value=1, max_value=6, value=len(default_tracks))
                                vert_height = st.number_input(
                                    "Set plot height in pixels", value=680, placeholder="How tall you want the plot?"
                                )
                            


                                for i in range(num_tracks):
                                #with st.container(f"Track {i + 1} Settings", expanded=False):
                                    # Select curves for this track
                                    default_curves = [
                                        curve for curve in default_tracks[i] if curve in available_curves
                                    ] if i < len(default_tracks) else []
                                    f"#### Track {i + 1}"
                                    track_curves = st.multiselect(
                                        f"Select curves for Track {i + 1}",
                                        available_curves,
                                        default=default_curves,
                                        key=f"track_{i}"
                                    )
                                    custom_tracks.append(track_curves)
                                    
                                    # Track grid configuration
                                    st.write("Track Grid Configuration")
                                    col1, col2 = st.columns([1, 3])
                                    with col1:
                                        show_grid = st.checkbox("Show grid", key=f"show_grid_{i}")
                                    with col2:
                                        grid_values = st.text_input(
                                            "Grid values (comma-separated)",
                                            key=f"grid_values_{i}",
                                            help="Enter comma-separated values for grid lines"
                                        )
                                    
                                    try:
                                        grid_vals = [float(x.strip()) for x in grid_values.split(',') if x.strip()]
                                    except ValueError:
                                        grid_vals = []
                                    
                                    track_grids.append({
                                        'show': show_grid,
                                        'values': grid_vals
                                    })
                                    
                                    # Create range and style inputs for each selected curve
                                    curve_ranges = {}
                                    for curve in track_curves:
                                        st.write(f"Settings for {curve}")
                                        
                                        # Range settings
                                        default_range = default_curve_ranges[i].get(curve, {"left": 0, "right": 1})
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            left_val = st.number_input(
                                                f"Left edge value",
                                                value=default_range["left"],
                                                key=f"left_{i}_{curve}"
                                            )
                                        with col2:
                                            right_val = st.number_input(
                                                f"Right edge value",
                                                value=default_range["right"],
                                                key=f"right_{i}_{curve}"
                                            )
                                        
                                        curve_ranges[curve] = {'left': left_val, 'right': right_val}
                                        
                                        # Style settings
                                        default_style = default_curve_properties.get(curve, {"color": "#000000", "thickness": 1.5, "line_style": "solid", "logarithmic": False})
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            color = st.color_picker(
                                                f"Color",
                                                value=default_style["color"],
                                                key=f"color_{i}_{curve}"
                                            )
                                        
                                        with col2:
                                            thickness = st.number_input(
                                                f"Thickness",
                                                min_value=0.5,
                                                max_value=5.0,
                                                value=default_style["thickness"],
                                                step=0.5,
                                                key=f"thickness_{i}_{curve}"
                                            )
                                        
                                        with col3:
                                            line_style = st.selectbox(
                                                f"Line style",
                                                options=['solid', 'dash', 'dot', 'dashdot'],
                                                index=['solid', 'dash', 'dot', 'dashdot'].index(default_style["line_style"]),
                                                key=f"line_style_{i}_{curve}"
                                            )
                                        
                                        with col4:
                                            is_log = st.checkbox(
                                                "Log scale",
                                                value=default_style["logarithmic"],
                                                key=f"log_{i}_{curve}"
                                            )
                                        
                                        # Store curve properties
                                        curve_properties[curve] = {
                                            'color': color,
                                            'thickness': thickness,
                                            'line_style': line_style,
                                            'logarithmic': is_log
                                        }
                                    
                                    track_curve_ranges.append(curve_ranges)
                                    #st.markdown("---")

                        #if st.form_submit_button("Update",use_container_width=True):
                        #    st.rerun()
                    
                    #st.write("Load Deviation Data")
                    if st.button("Load/Edit Deviation Survey Data", use_container_width=True):
                        get_df_from_user(["MD","INC","AZIM"],0)
                    
                    #st.session_state.data_array[0]
                    # Initialize well_info dictionary in session state if not exists
                    if 'well_info' not in st.session_state:
                        olakb=1
                        olagl=0

                        try:
                            olakb=st.session_state.wellobj.header.set_index("mnemonic").loc["KB", "value"]
                        except:
                            pass
                        try:
                            olakb=st.session_state.wellobj.header.set_index("mnemonic").loc["EKB", "value"]
                        except:
                            pass
                        try:
                            olagl=st.session_state.wellobj.header.set_index("mnemonic").loc["GL", "value"]
                        except:
                            pass
                        try:
                            olagl=st.session_state.wellobj.header.set_index("mnemonic").loc["EGL", "value"]
                        except:
                            pass
                        st.session_state.well_info = {
                            'Well Name': getattr(well, 'name', '') or '',
                            'Well UWI/API': getattr(well, 'uwi', '') or getattr(well, 'api', '') or '',
                            'Kelly Bushing Elevation': str(olakb),
                            'Ground Level Elevation': str(olagl),
                            'Water Table Elevation': '0',
                            'Bottom Hole Temperature': '',
                            'Latitude': str(getattr(well.location, 'lat', '') or ''),
                            'Longitude': str(getattr(well.location, 'lon', '') or ''),
                            'Mud resistance': '',
                            'Mud Filtrate Resistance': ''
                        }
                    
                    # Create a form with two columns and 5 rows
                    with st.form(key='well_info_form'):
                        submit_button = st.form_submit_button(label='Proceed to Calculations',type="primary", use_container_width=True)
                        # Define the fields in order
                        fields = [
                            'Well Name', 'Well UWI/API', 
                            'Kelly Bushing Elevation', 'Ground Level Elevation', 
                            'Water Table Elevation', 'Bottom Hole Temperature', 
                            'Latitude', 'Longitude', 
                            'Mud resistance', 'Mud Filtrate Resistance'
                        ]
                        
                        # Create 5 rows of inputs
                        for i in range(0, 10, 2):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.session_state.well_info[fields[i]] = st.text_input(
                                    fields[i], 
                                    value=st.session_state.well_info[fields[i]],
                                    help=f'Enter {fields[i]}'
                                )
                            
                            with col2:
                                st.session_state.well_info[fields[i+1]] = st.text_input(
                                    fields[i+1], 
                                    value=st.session_state.well_info[fields[i+1]],
                                    help=f'Enter {fields[i+1]}'
                                )
                        if st.session_state.mudattributedf is None:
                            st.session_state.mudattributedf = pd.DataFrame(
                                [
                                   {"Shoe Depth": None, "MaxMudWeight": 1.0, "Bit Dia":None, "Casing Dia": None, "Section BHT":None, "Mud Motor ID":None},
                               ]
                            )
                        
                        st.write("Casing, Bit and Mud Dataframe")
                        st.session_state.mudattributedf = st.data_editor(st.session_state.mudattributedf, num_rows="dynamic")
                        
                        
                    #st.session_state.data_array[0]
                    #if st.session_state.data_array[0] is not None:
                    #st.session_state.wellobj.location.add_deviation(st.session_state.data_array[0])
                    #fullwell = getwelldev(string_data,st.session_state.data_array[0])
                    step = 5
                    st.session_state.wellobj = getwelldev(wella=resample_well(string_las=string_data,step=step),deva=st.session_state.data_array[0], step=step)#resample_well(fullwell,5)
                    neutron = st.session_state.wellobj.data[st.session_state.alias['neutron']].values
                    corneu = neutron/100 if np.nanmean(neutron)>1 else neutron
                    md = st.session_state.wellobj.data["MD"].values
                    st.session_state.wellobj.data[st.session_state.alias['neutron']] = Curve(corneu, mnemonic=st.session_state.alias['neutron'],units='v/v', index=md, null=-999.25)

                    #st.session_state.wellobj.location
                    traj = st.session_state.wellobj.location.trajectory()
                    
                    # Process form submission
                    if submit_button:
                        if st.session_state.aliasState:
                            st.switch_page("_2_Geomech.py")
                        else:
                            st.write("Minimum data for calculation not available")
                        #st.write(st.session_state.well_info)
                    #st.write(well.location.ekb)
                    
                    # Ensure DEPT column exists and is properly named
                    if 'DEPT' not in curves.columns and curves.index.name == 'DEPT':
                        curves = curves.reset_index()

                    # Save curves to session state
                    #st.session_state.curve_data = curves
        
                    #detected_aliases = auto_detect_aliases(st.session_state.curve_data)
                    #st.session_state.aliases.update(detected_aliases)
                    #st.write("LAS file parsed successfully!")
                    # Prompt user to manually update aliases if any are missing
                    #st.write(st.session_state.aliases)
                    #example st.session_state.aliases = {"GR":["GRCFM","GR"],"DTCO":["DTHM","DTCO"],"RESDEEP":["RACELM","RPCELM","RT_HRLT"],"RESSHAL":["RACEHM","RPCEHM","RXO_HRLT"],"RHOB":["BDCFM","RHO8"],"NPHI":["NPLFM","NPCKLFM","NPCKSFM","NPHI_LIM"]}
                    #st.write(list(curves))
                    #example list(curves) = ["DEPT","DTST","DTSTE","DTCO","GR","DTSM","DCAL","NPHI_LIM","GR_EDTC","VPVS","RD1_PPC1","RD2_PPC1","RD3_PPC1","RD4_PPC1","REA_PPC1","RD1_PPC2","RD2_PPC2","RD3_PPC2","RD4_PPC2","REA_PPC2","MD","C1","C2","CALI","RHOI","HNPO_LIM","RXO_HRLT","RHO8","HGR","HTNP","PEF8","PEFZ","HGR_EDTC","RT_HRLT"]
                       
                    #st.session_state.refresher = st.button("Update Plot")
        #import liblogstress as lsd
        with cols[1]:
            with st.container(height=719):
                if st.session_state.las_file is not None:
                    #st.write(custom_tracks,track_curve_ranges,curve_properties)
                    try:
                        fig = create_well_log_plot(
                            st.session_state.curve_data,
                            custom_tracks,
                            track_curve_ranges,
                            curve_properties,
                            track_grids,
                            None,None,
                            vert_height,
                            style='linear'
                        )
                        
                        #fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
                        fig.update_yaxes(row=2,range = [st.session_state.curve_data.index.max(),st.session_state.curve_data.index.min()],autorange=False)
                        st.plotly_chart(fig, use_container_width=True)
                        #df = lsd.plotPPzhang(st.session_state.wellobj)
                        #df
                    except IndexError:
                        st.write("Not all required aliases for the plot are mapped")
