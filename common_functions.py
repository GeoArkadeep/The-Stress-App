"""
Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED
This file is part of "The Stress App" project and is released under the 
GNU Affero General Public License v3.0 (AGPL-3.0)
See the GNU Affero General Public License for more details: <https://www.gnu.org/licenses/agpl-3.0.html>
"""

import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pint
from welly import Well
import json

def create_well_log_plot(curves, track_curves, track_curve_ranges, curve_properties, track_grids, sparse_points=None, sparse_point_properties=None, vert_height=1000, header_height=150, indexkey='DEPT'):
    """
    Create a well log plot with multiple tracks sharing an inverted depth axis.
    Supports individual scaling, styling, and logarithmic transformation for each curve.
    """
    standardheight = 1000
    num_tracks = len(track_curves)
    annotation_height = header_height/vert_height#0.15
    offset_y = 0.02/(vert_height/standardheight)#0.02
    plot_height = 1 - annotation_height
    maxcurvenum = max(len(track_curve_names) + 1 for track_curve_names in track_curves)
   
    try:
        yindex = curves[indexkey]
    except:
        yindex = curves.index.values
    
    # Create figure
    fig = make_subplots(
        rows=2,
        cols=num_tracks,
        shared_yaxes=True,
        horizontal_spacing=0.00,
        vertical_spacing=0,
        row_heights=[annotation_height, plot_height],
    )
    
    # Plot curves and add annotations for each track
    for track_idx, track_curve_names in enumerate(track_curves):
        print(track_curve_names)
        track_range_dict = track_curve_ranges[track_idx]
        #st.write(maxcurvenum)
        annotation_spacing = annotation_height / maxcurvenum
        
        for curve_idx, curve_name in enumerate(track_curve_names):
            if curve_name in curves.columns:
                # Get curve properties
                props = curve_properties.get(curve_name, {})
                color = props.get('color', '#1f77b4')
                thickness = props.get('thickness', 1.5)
                line_style = props.get('line_style', 'solid')
                is_log = props.get('logarithmic', False)
                
                # Get curve-specific range
                curve_range = track_range_dict.get(curve_name, {})
                left_val = curve_range.get('left', 0)
                right_val = curve_range.get('right', 100)
                
                # Get curve data and apply logarithmic transformation if needed
                curve_data = curves[curve_name].copy()
                if is_log:
                    min_positive = curve_data[curve_data > 0].min() if any(curve_data > 0) else 1e-10
                    curve_data = np.log10(np.maximum(curve_data, min_positive))
                    left_val = np.log10(left_val)
                    right_val = np.log10(right_val)
                
                # Normalize the curve data
                scale = 1.0 / (right_val - left_val)
                normalized_data = (curve_data - left_val) * scale
                
                # Create custom hover text with original values
                original_values = curves[curve_name]
                hover_text = [f"{curve_name}: {val:.4g}" for val in original_values]
                
                # Plot the normalized curve with custom hover text
                fig.add_trace(
                    go.Scattergl(
                        x=normalized_data,
                        y=yindex,
                        name=curve_name,
                        text=hover_text,
                        hoverinfo='text+y',
                        line=dict(
                            color=color,
                            dash=line_style,
                            width=thickness
                        ),
                        line_shape='hv',
                        showlegend=False
                    ),
                    row=2,
                    col=track_idx + 1
                )
                
                # Wrap Curves
                # Plot the original curve data as a two ghost curves
                fig.add_trace(
                    go.Scattergl(
                        x=normalized_data-1,
                        y=yindex,
                        name=f"Ghost {curve_name}",
                        line=dict(
                            color=color,
                            dash=line_style,
                            width=thickness
                        ),
                        line_shape='hv',
                        opacity=0.3,  # Ghost curve transparency
                        hoverinfo='skip',  # Do not show hover text for ghost curve
                        showlegend=False
                    ),
                    row=2,
                    col=track_idx + 1
                )
                
                fig.add_trace(
                    go.Scattergl(
                        x=normalized_data+1,
                        y=yindex,
                        name=f"Ghost {curve_name}",
                        line=dict(
                            color=color,
                            dash=line_style,
                            width=thickness
                        ),
                        line_shape='hv',
                        opacity=0.3,  # Ghost curve transparency
                        hoverinfo='skip',  # Do not show hover text for ghost curve
                        showlegend=False
                    ),
                    row=2,
                    col=track_idx + 1
                )
                
                # Add annotation elements
                annotation_y = 1 - (curve_idx + 1) * annotation_spacing

                # Add curve name
                fig.add_annotation(
                    x=0.5,
                    y=annotation_y + offset_y,
                    text = f"{curve_name[:5]}",
                    showarrow=False,
                    font=dict(color=color),
                    xref=f"x{track_idx + 1}",
                    yref="paper",
                    xanchor="center"
                )
                
                # Add horizontal line
                fig.add_shape(
                    type="line",
                    x0=0,
                    x1=1,
                    y0=annotation_y,
                    y1=annotation_y,
                    line=dict(
                        color=color,
                        dash=line_style,
                        width=thickness
                    ),
                    xref=f"x{track_idx + 1}",
                    yref="paper"
                )
                
                # Add range values as separate annotations
                display_left = 10**left_val if is_log else left_val
                display_right = 10**right_val if is_log else right_val
                
                # Left value
                fig.add_annotation(
                    x=0,
                    y=annotation_y,
                    text=f"{display_left:.2f}",
                    showarrow=False,
                    font=dict(color=color, size=10),
                    xref=f"x{track_idx + 1}",
                    yref="paper",
                    xanchor="left"
                )
                
                # Right value
                fig.add_annotation(
                    x=1,
                    y=annotation_y,
                    text=f"{display_right:.2f}",
                    showarrow=False,
                    font=dict(color=color, size=10),
                    xref=f"x{track_idx + 1}",
                    yref="paper",
                    xanchor="right"
                )
        
        # Add custom grid lines for the track
        track_grid = track_grids[track_idx]
        if track_grid['show'] and track_grid['values']:
            for grid_val in track_grid['values']:
                # Normalize grid value to [0,1] range based on the first curve's range
                first_curve = track_curve_names[0]
                first_range = track_range_dict[first_curve]
                left_val = first_range['left']
                right_val = first_range['right']
                
                if curve_properties.get(first_curve, {}).get('logarithmic', False):
                    grid_val = np.log10(max(grid_val, 1e-10))
                    left_val = np.log10(max(left_val, 1e-10))
                    right_val = np.log10(max(right_val, 1e-10))
                
                norm_grid_val = (grid_val - left_val) / (right_val - left_val)
                
                fig.add_shape(
                    type="line",
                    x0=norm_grid_val,
                    x1=norm_grid_val,
                    y0=yindex.min(),
                    y1=yindex.max(),
                    line=dict(
                        color='rgba(128, 128, 128, 0.25)',
                        dash='solid',
                        width=1
                    ),
                    row=2,
                    col=track_idx + 1
                )
            
    def normalize_sparse_point(point_value, curve_range, is_log=False):
        """
        Normalize a sparse point value based on the curve's range and logarithmic settings.
        
        Args:
            point_value (float): The value to normalize
            curve_range (dict): Dictionary containing 'left' and 'right' keys for normalization
            is_log (bool, optional): Whether to apply logarithmic transformation. Defaults to False.
        
        Returns:
            float: Normalized value between 0 and 1
        """
        left_val = curve_range['left']
        right_val = curve_range['right']
        
        # Apply log transformation if needed
        if is_log:
            point_value = np.log10(max(point_value, 1e-10))
            left_val = np.log10(max(left_val, 1e-10))
            right_val = np.log10(max(right_val, 1e-10))
        
        # Normalize to [0, 1] range
        normalized_value = (point_value - left_val) / (right_val - left_val)
        
        return normalized_value

    # Update the sparse points plotting section in the main function
    # Replace the existing sparse points plotting code with:
    if sparse_points is not None:
        for track_idx, track_points in sparse_points.items():
            # Get the range of the first curve in this track for normalization
            first_curve = track_curves[track_idx][0]
            first_range = track_curve_ranges[track_idx][first_curve]
            is_log = curve_properties.get(first_curve, {}).get('logarithmic', False)
            
            # Iterate through point groups in this track
            for group_key, points in track_points.items():
                # Get properties for this specific group of points
                point_props = sparse_point_properties.get(track_idx, {}).get(group_key, {})
                color = point_props.get('color', '#ff7f0e')
                size = point_props.get('size', 10)
                symbol = point_props.get('symbol', 'circle')

                # Normalize points
                normalized_points = []
                original_points = []
                for point in points:
                    # Unpack x and y values
                    x_val, y_val = point
                    
                    # Normalize x value
                    norm_x_val = normalize_sparse_point(x_val, first_range, is_log)
                    
                    normalized_points.append((norm_x_val, y_val))
                    original_points.append(point)

                # Plot normalized points
                fig.add_trace(
                    go.Scattergl(
                        x=[point[0] for point in normalized_points],
                        y=[point[1] for point in normalized_points],
                        mode='markers',
                        marker=dict(
                            color=color,
                            size=size,
                            symbol=symbol
                        ),
                        text=[f"{group_key}: {orig[0]:.4g}, Depth: {orig[1]:.4g}" 
                              for orig, point in zip(original_points, normalized_points)],
                        hoverinfo='text',
                        showlegend=False
                    ),
                    row=2,
                    col=track_idx + 1
                )

    # Update layout
    fig.update_layout(
        height=vert_height,
        width=200 * num_tracks,
        plot_bgcolor='rgba(0,0,0,0)',#'white',
        paper_bgcolor='rgba(0,0,0,0)',#'white',
        margin=dict(t=0, b=0,l=10,r=10),
        showlegend=False,
        # Lock x-axis zooming
        xaxis=dict(fixedrange=True),
        dragmode='zoom'  # This enables panning instead of box zoom
    )
    
    # Update y-axes
    #for i in range(num_tracks):
        # Only show y-axis title on the first track
    title_text = None
        
    fig.update_yaxes(
        row=2,
        autorange="reversed",
    )
    
    # Hide the annotation area y-axis
    fig.update_yaxes(
        row=1,
        #visible=False
        #showline=True,
        showgrid=False,
        showticklabels=False,
        range=[2, 3]
    )
    
    # Lock all x-axes
    for i in range(num_tracks):
        # First, handle the plot area x-axis
        first_curve = track_curves[i][0]
        first_range = track_curve_ranges[i][first_curve]
        is_log = curve_properties.get(first_curve, {}).get('logarithmic', False)
        
        left_val = first_range['left']
        right_val = first_range['right']
        
        if is_log:
            left_val = 10**left_val
            right_val = 10**right_val
        
        
    fig.update_xaxes(
        row=2,
        #col=i+1,
        range=[0, 1],
        showgrid=False,
        #showline=True,
        linewidth=1,
        linecolor='grey',
        mirror=True,
        showticklabels=False,
        fixedrange=True  # Lock x-axis zooming
    )
    
    # Handle the annotation area x-axis
    fig.update_xaxes(
        row=1,
        #col=i+1,
        #visible=False,
        showgrid=False,
        showline=False,
        showticklabels=False,
        linewidth=1,
        linecolor='grey',
        mirror=True,
        #fixedrange=True  # Lock x-axis zooming
    )
    
    # Get existing shapes (annotation lines) from the figure
    existing_shapes = list(fig.layout.shapes) if fig.layout.shapes else []
    
    # Create border shapes
    border_shapes = [
        # Main outer rectangle
        dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0,
            y0=0,
            x1=1,
            y1=1,
            line=dict(width=1, color="grey")
        ),

    ]
    
    # Add vertical lines at track boundaries
    for i in range(num_tracks + 1):  # +1 to include the rightmost boundary
        x_pos = i / num_tracks  # Calculate position in paper coordinates
        border_shapes.append(
            dict(
                type="line",
                xref="paper",
                yref="paper",
                x0=x_pos,
                y0=-0.1,
                x1=x_pos,
                y1=1,
                line=dict(width=1, color="grey")
            )
        )
    
    # Combine existing shapes with border shapes
    all_shapes = existing_shapes + border_shapes
    
    # Update layout with all shapes
    fig.update_layout(shapes=all_shapes)
    
    return fig



def resample_well(string_las = None, well=None, step=5):
    """
    Resample all curves in a Welly Well object to a common depth basis.

    Parameters:
        well (Well): A Welly Well object containing curves to be resampled.
        step (float): The step size for the resampled depth basis (default is 5).

    Returns:
        Well: The modified Well object with all curves resampled in-place.
    """
    if well is None:
        well = Well.from_las(string_las, index = "m")
    
    if step==0 or step is None:
        return well
    # Determine the maximum depth from all curves
    max_depth = max(curve.basis[-1] for curve in well.data.values() if hasattr(curve, 'basis'))
    

    # Resample each curve to the new depth basis
    for curve_name, curve in well.data.items():
        #if hasattr(curve, 'to_basis'):  # Ensure the curve has the to_basis method

        well.data[curve_name] = curve.to_basis(start=0,stop=max_depth,
                step=step, undefined=np.nan, interp_kind='linear'
            )
    
    return well

#Function to get well deviation
def getwelldev(string_las=None,wella=None,deva=None,step=None):
    if wella is None:
        wella = Well.from_las(string_las, index = "m")
    depth_track = wella.df().index
    if deva is not None:
        #deva=pd.read_csv(devpath, sep=r'[ ,	]',skipinitialspace=True)
        #print(deva)
        start_depth = wella.df().index[0]
        final_depth = wella.df().index[-1]
        spacing = ((wella.df().index.values[-1]-wella.df().index.values[0])/len(wella.df().index.values))
        if step is not None:
            spacing = step
        #print("Sample interval is :",spacing)
        padlength = int(start_depth/spacing)
        #print(padlength)
        padval = np.zeros(padlength)
        i = 1
        while(i<padlength):
            padval[-i] = start_depth-(spacing*i)
            i+=1
        #print("pad depths: ",padval)
        md = depth_track
        md =  np.append(padval,md)
        mda = pd.to_numeric(deva["MD"], errors='coerce')
        inca = pd.to_numeric(deva["INC"], errors='coerce')
        azma = pd.to_numeric(deva["AZIM"], errors='coerce')
        inc = np.interp(md,mda,inca)
        azm = np.interp(md,mda,azma)
        #i = 1
        #while md[i]<final_depth:
        #    if md[i]
        z = deva.to_numpy(na_value=0)
        dz = [md,inc,azm]
    else:
        start_depth = wella.df().index[0]
        final_depth = wella.df().index[-1]
        spacing = ((wella.df().index.values[-1]-wella.df().index.values[0])/len(wella.df().index.values))
        if step is not None:
            spacing = step
        #print("Sample interval is :",spacing)
        padlength = int(start_depth/spacing)
        #print(padlength)
        padval = np.zeros(padlength)
        i = 1
        while(i<padlength):
            padval[-i] = start_depth-(spacing*i)
            i+=1
        #print("pad depths: ",padval)
        
        md = depth_track
        md =  np.append(padval,md)
        #md[0] = 0
        #md[0:padlength-1] = padval[0:padlength-1]
        inc = np.zeros(len(depth_track)+padlength)
        azm = np.zeros(len(depth_track)+padlength)
        dz = [md,inc,azm]



    dz = np.transpose(dz)
    dz = pd.DataFrame(dz)
    dz = dz.dropna()
    #print(dz)
    finaldepth = dz.to_numpy()[-1][0]
    #print("Final depth is ",finaldepth)
    wella.location.add_deviation(dz, wella.location.td)
    tvdg = wella.location.tvd
    md = wella.location.md
    from welly import curve
    MD = curve.Curve(md, mnemonic='MD',units='m', index = md)
    wella.data['MD'] =  MD
    TVDM = curve.Curve(tvdg, mnemonic='TVDM',units='m', index = md)
    wella.data['TVDM'] =  TVDM
    wella.unify_basis(keys=None, alias=None, step=spacing)
    
    print("Great Success!! :D")

    return wella




# Function to load aliases from JSON file
def load_aliases():
    try:
        with open("aliases.json", "r") as jsonfile:
            daliases = json.load(jsonfile)
            return daliases
    except:
        # Default aliases if no file exists
        return {
            'sonic': ['none', 'DTC', 'DT24', 'DTCO', 'DT', 'AC', 'AAC', 'DTHM'],
            'shearsonic': ['none', 'DTSM'],
            'gr': ['none', 'GR', 'GRD', 'CGR', 'GRR', 'GRCFM'],
            'resdeep': ['none', 'HDRS', 'LLD', 'M2RX', 'MLR4C', 'RD', 'RT90', 'RLA1', 'RDEP', 'RLLD', 'RILD', 'ILD', 'RT_HRLT', 'RACELM'],
            'resshal': ['none', 'LLS', 'HMRS', 'M2R1', 'RS', 'RFOC', 'ILM', 'RSFL', 'RMED', 'RACEHM'],
            'density': ['none', 'ZDEN', 'RHOB', 'RHOZ', 'RHO', 'DEN', 'RHO8', 'BDCFM'],
            'neutron': ['none', 'CNCF', 'NPHI', 'NEU'],
            'pe': ['none','PE'],
            'ROP': ['none','ROPAVG'],
            'RPM': ['none','SURFRPM'],
            'WOB': ['none','WOBAVG'],
            'ECD': ['none','ACTECDM'],
            'BIT': ['none','BIT'],
            'TORQUE': ['none','TORQUE','TORQUEAV'],
            'FLOWRATE': ['none','FLOWRATE','FLOWIN'],

        }

# Function to save aliases to JSON file
def save_aliases(aliases):
    with open("aliases.json", "w") as jsonfile:
        json.dump(aliases, jsonfile, indent=4)



# Function to get aliases
missing_aliases = []
@st.dialog("Aliases")
def get_missing_aliases():
    if missing_aliases:
        st.write("The following aliases are missing or unassigned. Please map them:")
        for alias in missing_aliases:
            # Get the current selections or initialize as empty list
            current_selection = st.session_state.aliases.get(alias, [])
            
            # Display multiselect and add current selections
            new_selection = st.multiselect(
                f"Select curve for {alias}", 
                options=["None"] + list(st.session_state.curve_data.columns),
                default=["None"]
            )
            
            # Update the alias with new and existing selections, avoiding duplicates
            updated_selection = list(set(current_selection + new_selection))
            st.session_state.aliases[alias] = updated_selection
        
        # Save updated aliases to JSON
        save_aliases(st.session_state.aliases)
        
        #st.write(st.session_state.aliases)
    
    if st.button("Show Aliases"):
        st.write(st.session_state.alias)
# File uploader



@st.dialog("Dataset Editor")
def get_df_from_user(headers, array_num, units=None):
    """
    Interactive DataFrame loader and processor with optional unit conversion.
    
    Parameters:
    - headers: List of required column headers
    - array_num: index denoting which session_memory DataFrame to process
    - units: Optional list of expected units for each header
    
    
    Returns:
    - Nothing, writes in place as this is a dialogbox
    """
    # Validate units parameter
    if units is not None and len(units) != len(headers):
        st.error("Length of headers and units must match!")
        return None
    df = st.session_state.data_array[array_num]
    processed_df=df
    
    # If no DataFrame is provided, upload file
    if df is None:
        if st.button("Manual Entry", use_container_width=True):
            #manualentry = st.form(f"data_entry_form_{array_num}")
            #with st.form(key=f'data_entry_form_{array_num}'):
                #st.session_state.data_array[array_num] = pd.DataFrame(columns=headers)
            st.session_state.data_array[array_num] = pd.DataFrame(columns=headers)#st.data_editor(pd.DataFrame(columns=headers),num_rows="dynamic", use_container_width=True)
            st.data_editor(st.session_state.data_array[array_num],num_rows="dynamic", use_container_width=True, hide_index=False)
            #manualsave = manualentry.form_submit_button(label='Save', use_container_width=True)
            #if manualsave:
            #    st.rerun()

            
        uploaded_file = st.file_uploader(
            "Upload a spreadsheet file", 
            type=["csv", "xls", "xlsx"]
        )
        if uploaded_file is None:
            return None
        # Read the file based on file type
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        
        # Column mapping and unit conversion section
        st.subheader("Column Mapping and Unit Conversion")
        
        # Create a ureg (unit registry) for conversion
        ureg = pint.UnitRegistry()
        
        # Processed DataFrame to return
        processed_df = pd.DataFrame(columns=headers)
        
        # Column mapping and unit conversion for each required header
        for i, header in enumerate(headers):
            # Column selection
            default_column = df.columns[i] if i < len(df.columns) else "None"
            available_columns = list(df.columns)
            available_columns.insert(0, "None")
            
            selected_column = st.selectbox(
                f"Select column for {header}", 
                available_columns,
                index=available_columns.index(default_column)
            )
                
            # Unit conversion if units are specified
            if selected_column != "None":
                # Check if unit conversion is applicable
                current_unit = None
                if units is not None and i < len(units):
                    unit = units[i]
                    # Only prompt for unit if a unit is specified and not empty/None/NaN
                    if unit and not pd.isna(unit) and unit != "":
                        current_unit = st.text_input(
                            f"Current units for {header}", 
                            value=str(unit)
                        )
                
                try:
                    # If current_unit is set and conversion is possible
                    if current_unit:
                        # Convert units using pint
                        converted_series = df[selected_column].apply(
                            lambda x: (x * ureg(current_unit)).to(ureg(units[i])).magnitude
                        )
                        processed_df[header] = converted_series
                    else:
                        # Direct assignment if no conversion needed
                        processed_df[header] = df[selected_column]
                
                except Exception as e:
                    st.error(f"Error processing {header}: {e}")
                    processed_df[header] = np.nan
            else:
                # Fill with NaN if no column selected
                processed_df[header] = np.nan
    
        #submit_button = st.form_submit_button(label='Update Dataframe')
        #if submit_button:
        #    pass
    if st.button("Clear Data and Return",use_container_width=True):
        st.session_state.data_array[array_num]=None
        st.rerun()
        return None
    if st.button("Save and Return",use_container_width=True):
        st.session_state.data_array[array_num] = processed_df
        st.rerun()
    st.session_state.data_array[array_num] = st.data_editor(processed_df,num_rows="dynamic", use_container_width=True, hide_index=False)