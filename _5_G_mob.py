"""
Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED
This file is part of "The Stress App" project and is released under the 
GNU Affero General Public License v3.0 (AGPL-3.0)
See the GNU Affero General Public License for more details: <https://www.gnu.org/licenses/agpl-3.0.html>
"""

import streamlit as st
import pandas as pd
import stresslog as lsd
from common_functions import create_well_log_plot, resample_well, getwelldev, load_aliases, save_aliases, get_missing_aliases, get_df_from_user
clearflag=True
df=None
bs=None

if 'constraints' not in st.session_state:
    st.session_state.constraints = pd.DataFrame([{"MD": None, "Value": None, "Type":"Fracture Gradient"},])

if 'outputdata' not in st.session_state:
    st.session_state.outputdata = [None,None,None,None,None,None,None]

if 'lastdoi' not in st.session_state:
    st.session_state.lastdoi = 0
    
@st.dialog("Detailed Analysis",width="large")
def detailed_analysis():
    st.markdown(f'<img src="data:image/png;base64,{st.session_state.outputdata[5]}" style="width:100%;">', unsafe_allow_html=True)
    st.markdown(f'<img src="data:image/png;base64,{st.session_state.outputdata[4]}" style="width:100%;">', unsafe_allow_html=True)
    st.markdown(f'<img src="data:image/png;base64,{st.session_state.outputdata[6]}" style="width:100%;">', unsafe_allow_html=True)
    st.markdown(f'<img src="data:image/png;base64,{st.session_state.outputdata[2]}" style="width:100%;">', unsafe_allow_html=True)
    st.markdown(f'<img src="data:image/png;base64,{st.session_state.outputdata[3]}" style="width:100%;">', unsafe_allow_html=True)
    


def mobile_geomech(defaults):
    st.title("MODEL TUNING")
    if st.button('Back to Well Data QC',type="primary", use_container_width=True):
        st.switch_page("_1_Import.py")

    with st.form(key='model_parameters'):
        has_changed = False
        
        # Check for changes
        for key in defaults.keys():
            if st.session_state.get(f"{key}_input", st.session_state[key]) != st.session_state[key]:
                st.session_state[key] = st.session_state[f"{key}_input"]
                has_changed = True

        # Form submit 1
        if st.form_submit_button(label='Recalculate', use_container_width=True) or has_changed or st.session_state.outputdata[0] is None:
            if st.session_state.mudattributedf is not None:
                mwvalues = st.session_state.mudattributedf[["MaxMudWeight", "Shoe Depth", "Bit Dia", "Casing Dia", "Mud Motor ID", "Section BHT"]].apply(
                    lambda col: (
                        col.astype(float).fillna(1.0) if col.name == "Max MudWeight"
                        else col.astype(float).fillna(0.0)
                        if col.name != "Mud Motor ID"
                        else col.replace({None: "0"}).fillna("0")
                    )
                ).values.tolist()
            else:
                mwvalues = [[1.0, 0.0, 0.0, 0.0, 0.0, 0]]
            attrib = [float(st.session_state.well_info.get(key, "0") or "0") for key in [
                "Kelly Bushing Elevation",
                "Ground Level Elevation",
                "Water Table Elevation",
                "Latitude",
                "Longitude",
                "Bottom Hole Temperature",
                "Mud resistance",
                "Mud Filtrate Resistance"
            ]]

            st.session_state.outputdata[0], st.session_state.outputdata[1], st.session_state.outputdata[2], st.session_state.outputdata[3], st.session_state.outputdata[4], st.session_state.outputdata[5], st.session_state.outputdata[6],st.session_state.lastdoi = lsd.plotPPzhang(
                st.session_state.wellobj, rhoappg=st.session_state.rhoappg, lamb=st.session_state.lamb,
                ul_exp=st.session_state.lamb if st.session_state.ul_depth == 0 else st.session_state.ul_exp,
                ul_depth=st.session_state.ul_depth, a=st.session_state.a,
                nu=st.session_state.nu, sfs=st.session_state.sfs, window=1, zulu=0, tango=20000,
                dtml=st.session_state.dtml, dtmt=st.session_state.dtmt, water=st.session_state.water,
                underbalancereject=st.session_state.underbalancereject, tecb=st.session_state.tecb,
                doi=0.0, lala=st.session_state.lala, lalb=st.session_state.lalb,
                lalm=st.session_state.lalm, lale=st.session_state.lale, lall=st.session_state.lall,
                horsuda=st.session_state.horsuda, horsude=st.session_state.horsude,
                offset=st.session_state.offset, strike=st.session_state.strike, dip=st.session_state.dip, mudtemp=st.session_state.mudtemp,
                mwvalues=mwvalues, forms=st.session_state.data_array[1],
                flags=st.session_state.data_array[4], lithos=st.session_state.data_array[3],writeFile=False,attrib=attrib,aliasdict={key: [value] for key, value in st.session_state.alias.items()},
                program_option=[300,st.session_state.program_option,0,0,0],
                res0=st.session_state.res0, be=st.session_state.be, ne=st.session_state.ne,
                dex0=st.session_state.dex0, de=st.session_state.de, nde=st.session_state.nde,
            )

        with st.expander("Pore Pressure Zhang Parameters", expanded=False):
            # Compaction Parameters
            ppoptions = [
                "Zhang", "Eaton", "Dexp", "Average of All",
                "Zhang > Eaton > Dexp", "Zhang > Dexp > Eaton",
                "Eaton > Zhang > Dexp", "Eaton > Dexp > Zhang",
                "Dexp > Zhang > Eaton", "Dexp > Eaton > Zhang"
            ]

            st.session_state.program_option = st.selectbox("Pore Pressure Algorithm", range(len(ppoptions)), format_func=lambda x: ppoptions[x], index=4, key = "program_option_input")
         
            lamb = st.number_input("Compaction exponent (lambda)", 
                                   value=st.session_state.lamb, 
                                   format="%.6f", 
                                   key="lamb_input")
            ul_exp = st.number_input("Unloading compaction exponent (ul_exp)", 
                                     value=st.session_state.ul_exp, 
                                     format="%.6f", 
                                     key="ul_exp_input")
            ul_depth = st.number_input("Max velocity depth (ul_depth)", 
                                       value=st.session_state.ul_depth, 
                                       format="%.2f", 
                                       key="ul_depth_input")

            # Sonic travel times
            dtml = st.number_input("Sonic travel time at mudline (dtml)", 
                                   value=st.session_state.dtml, 
                                   format="%.1f", 
                                   key="dtml_input")
            dtmt = st.number_input("Sonic travel time of matrix (dtmt)", 
                                   value=st.session_state.dtmt, 
                                   format="%.1f", 
                                   key="dtmt_input")
            
            # Eatons Parameters
            res0 = st.number_input("Resistivity at mudline (res0)", 
                                   value=st.session_state.get("res0", 0.98), 
                                   format="%.2f", 
                                   key="res0_input")
            be = st.number_input("Compaction exponent resistivity (be)", 
                                 value=st.session_state.get("be", 0.00014), 
                                 format="%.6f", 
                                 key="be_input")
            ne = st.number_input("Eaton's parameter (ne)", 
                                 value=st.session_state.get("ne", 0.6), 
                                 format="%.2f", 
                                 key="ne_input")
            
            # Dexp Parameters
            dex0 = st.number_input("D.Exp at mudline (dex0)", 
                                   value=st.session_state.get("dex0", 0.5), 
                                   format="%.2f", 
                                   key="dex0_input")
            de = st.number_input("Compaction exponent D.exp (de)", 
                                 value=st.session_state.get("de", 0.00014), 
                                 format="%.6f", 
                                 key="de_input")
            nde = st.number_input("D.exp fitting parameter (nde)", 
                                  value=st.session_state.get("nde", 0.5), 
                                  format="%.2f", 
                                  key="nde_input")
              
            # Water-related parameter
            water = st.number_input("Water density (water)", 
                                    value=st.session_state.water, 
                                    format="%.2f", 
                                    key="water_input")

            # Underbalance rejection
            underbalancereject = st.number_input("Minimum PP gradient (underbalancereject)", 
                                                 value=st.session_state.underbalancereject, 
                                                 format="%.1f", 
                                                 key="underbalancereject_input")

            # Shear failure slope
            sfs = st.number_input("Shale flag cutoff (sfs)", 
                                  value=st.session_state.sfs, 
                                  format="%.2f", 
                                  key="sfs_input")


        with st.expander("Stress Tensor Parameters", expanded=False):
            # Apparent density
            rhoappg = st.number_input("Density at Mudline (rhoappg)", 
                                      value=st.session_state.rhoappg, 
                                      format="%.2f", 
                                      key="rhoappg_input")

            # Biot coefficient and Poisson's ratio
            a = st.number_input("Exponent (a)", 
                                value=st.session_state.a, 
                                format="%.3f", 
                                key="a_input")
            nu = st.number_input("Poisson's ratio (nu)", 
                                 value=st.session_state.nu, 
                                 format="%.3f", 
                                 key="nu_input")

            # Tensile failure threshold (Fixed Float Issue)
            tecb = st.number_input("Daine's Tectonic Factor b (tecb)", 
                                   value=st.session_state.tecb, 
                                   format="%.2f", 
                                   key="tecb_input")
        with st.expander("Stress Tensor Orientation", expanded=False):
            # Offset, strike, and dip
            offset = st.number_input("Azimuth of Max Horizontal Stress (offset)", 
                                     value=st.session_state.offset, 
                                     format="%.2f", 
                                     key="offset_input")
            strike = st.number_input("Dip Direction (strike)", 
                                     value=st.session_state.strike, 
                                     format="%.2f", 
                                     key="strike_input")
            dip = st.number_input("Dip Angle (dip)", 
                                  value=st.session_state.dip, 
                                  format="%.2f", 
                                  key="dip_input")
            

        with st.expander("Rock Strength Parameters", expanded=False):
            # LALA-related Parameters
            lala = st.number_input("Parameter A (lala)", 
                                   value=st.session_state.lala, 
                                   format="%.2f", 
                                   key="lala_input")
            lalb = st.number_input("Parameter B (lalb)", 
                                   value=st.session_state.lalb, 
                                   format="%.2f", 
                                   key="lalb_input")
            lalm = st.number_input("Parameter M (lalm)", 
                                   value=st.session_state.lalm, 
                                   format="%.2f", 
                                   key="lalm_input")
            lale = st.number_input("Parameter E (lale)", 
                                   value=st.session_state.lale, 
                                   format="%.2f", 
                                   key="lale_input")
            lall = st.number_input("Parameter L (lall)", 
                                   value=st.session_state.lall, 
                                   format="%.2f", 
                                   key="lall_input")

            # Horizontal Stress
            horsuda = st.number_input("Horsud Parameter A", 
                                      value=st.session_state.horsuda, 
                                      format="%.2f", 
                                      key="horsuda_input")
            horsude = st.number_input("Horsud Parameter E", 
                                      value=st.session_state.horsude, 
                                      format="%.2f", 
                                      key="horsude_input")

        with st.expander("Depth of Interest", expanded=True):
            # Depth of Interest
            doi = st.number_input("Depth of Interest (doi)", 
                                  value=st.session_state.doi, 
                                  format="%.2f", 
                                  key="doi_input")
            mudtemp = st.number_input("Mud Temperature", 
                                  value=st.session_state.mudtemp, 
                                  format="%.2f", 
                                  key="mudtemp_input")
        plotheight = st.number_input("Plot Height in pixels", 
                                  value=3000)

    st.write("Constraints")
    st.session_state.constraints = st.data_editor(
        st.session_state.constraints,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=False,  # Hide the index
        column_config={
            "Type": st.column_config.SelectboxColumn(
                "Constraint Type",
                options=[
                    "Fracture Gradient", 
                    "Pore Pressure Gradient", 
                    "Fracture Pressure", 
                    "Pore Pressure"
                ],
                required=True,
            ),
        },
    )
    #if st.session_state.constraints is not None:
        #st.write(st.session_state.constraints)
    point_tracks = {'Fracture Pressure': 4, 'Pore Pressure': 4, 'Fracture Gradient': 3, 'Pore Pressure Gradient': 3}

    # Point Data Dict for plotting
    result_dict = {}

    # Iterate through the constraints dataframe
    for _, row in st.session_state.constraints.iterrows():
        point_track = point_tracks[row[2]]  # Get the track for the type
        key = row[2]  # Use the type as the key (e.g., 'Fracture Pressure')
        
        # Create the structure if it doesn't exist
        if point_track not in result_dict:
            result_dict[point_track] = {}
        if key not in result_dict[point_track]:
            result_dict[point_track][key] = []
        
        # Add the depth and value as a tuple
        try:
            result_dict[point_track][key].append((float(row[1]), float(row[0])))
        except:
            pass

    # Process the st.session_state.data_array[5] dataframe
    point_track = 2  # UCS point track
    key = 'UCS'  # Key for UCS

    # Ensure the structure exists in the result_dict
    if point_track not in result_dict:
        result_dict[point_track] = {}
    if key not in result_dict[point_track]:
        result_dict[point_track][key] = []

    # Iterate through the data_array[5] dataframe
    try:    
        for _, row in st.session_state.data_array[5].iterrows():
        
            result_dict[point_track][key].append((float(row['UCS']), float(row['MD'])))
    except:
            pass
    #st.session_state.data_array[5]
    #result_dict
    # Form submit 2
    if st.button(label=f"Detailed Analysis", use_container_width=True) or has_changed or st.session_state.outputdata[3] is None:
        if st.session_state.mudattributedf is not None:
            mwvalues = st.session_state.mudattributedf[["MaxMudWeight", "Shoe Depth", "Bit Dia", "Casing Dia", "Mud Motor ID", "Section BHT"]].apply(
                lambda col: (
                    col.astype(float).fillna(1.0) if col.name == "Max MudWeight"
                    else col.astype(float).fillna(0.0)
                    if col.name != "Mud Motor ID"
                    else col.replace({None: "0"}).fillna("0")
                )
            ).values.tolist()
        else:
            mwvalues = [[1.025, 0.0, 0.0, 0.0, 0.0, 0]]
        #st.session_state.lastdoi
        if st.session_state.lastdoi != st.session_state.doi and has_changed:
            st.session_state.outputdata[0], st.session_state.outputdata[1], st.session_state.outputdata[2], st.session_state.outputdata[3], st.session_state.outputdata[4], st.session_state.outputdata[5], st.session_state.outputdata[6],st.session_state.lastdoi = lsd.plotPPzhang(
                st.session_state.wellobj, rhoappg=st.session_state.rhoappg, lamb=st.session_state.lamb,
                ul_exp=st.session_state.lamb if st.session_state.ul_depth == 0 else st.session_state.ul_exp,
                ul_depth=st.session_state.ul_depth, a=st.session_state.a,
                nu=st.session_state.nu, sfs=st.session_state.sfs, window=1, zulu=0, tango=20000,
                dtml=st.session_state.dtml, dtmt=st.session_state.dtmt, water=st.session_state.water,
                underbalancereject=st.session_state.underbalancereject, tecb=st.session_state.tecb,
                doi=0.0, lala=st.session_state.lala, lalb=st.session_state.lalb,
                lalm=st.session_state.lalm, lale=st.session_state.lale, lall=st.session_state.lall,
                horsuda=st.session_state.horsuda, horsude=st.session_state.horsude,
                offset=st.session_state.offset, strike=st.session_state.strike, dip=st.session_state.dip, mudtemp=st.session_state.mudtemp,
                mwvalues=mwvalues, forms=st.session_state.data_array[1],
                flags=st.session_state.data_array[4], lithos=st.session_state.data_array[3],writeFile=False,attrib=attrib,aliasdict={key: [value] for key, value in st.session_state.alias.items()},
                program_option=[300,st.session_state.program_option,0,0,0],
                res0=st.session_state.res0, be=st.session_state.be, ne=st.session_state.ne,
                dex0=st.session_state.dex0, de=st.session_state.de, nde=st.session_state.nde,
            )
            if st.session_state.outputdata[2] is not None:
                detailed_analysis()
        else:
            if st.session_state.outputdata[2] is not None:
                detailed_analysis()
    
    
    if st.button("Load/Edit UCS Calibration data", use_container_width=True):
        get_df_from_user(["MD","UCS"],5,["m","MPa"])
    #if st.button("Load/Edit RFT/BHS/well activity related data", use_container_width=True):
    #    get_df_from_user(["MD","GRADIENT","PRESSURE"],6,["m","gcc","psi"])
    #if st.button("Load/Edit Minifrac/(x)LOT/mudloss related data", use_container_width=True):
    #    get_df_from_user(["MD","GRADIENT","PRESSURE"],7,["m","gcc","psi"])
    if st.button("Load/Edit Formations", use_container_width=True):
        get_df_from_user(["Top TVD", "Number", "Formation Name", "GR Cut", "Struc.Top", "Struc.Bottom", "CentroidRatio", "OWC", "GOC", "Coeff.Vol.Therm.Exp.","SHMax Azim.", "SVDip", "SVDipAzim","Tectonic Factor","InterpretedSH/Sh","Biot","Dt_NCT","Res_NCT","DXP_NCT"],1,["m","","","","m","m","","m","m","","","","","","","","","",""])
    if st.button("Load/Edit Lithology", use_container_width=True):
        get_df_from_user(["Top MD", "Lithology Type","Interpreted Nu","Interpreted Mu","Interpreted UCS"],3,["m","","","",""])
    if st.button("Load/Edit Image Log Interpretation", use_container_width=True):
        get_df_from_user(["Top MD", "Observation"],4, ["m",""])
    if st.button('Proceed to Data Export',type="primary", use_container_width=True):
        st.switch_page("_3_Export.py")
    #df
    #with cols[1]:
    if st.session_state.outputdata[0] is not None:
        #with st.container(height=719):
        default_tracks = [[st.session_state.alias['gr'],"Poisson_Ratio"],#"Poisson_Ratio"],
                                  [st.session_state.alias['sonic'],"DTCT"],
                                  ["UCS_Horsud"],
                                  ["OBG_AMOCO","PP_GRADIENT","SHmin_DAINES","FracGrad"],
                                  ["MUD_PRESSURE","SHmin_PRESSURE","SHmax_PRESSURE","OVERBURDEN_PRESSURE","GEOPRESSURE","FracPressure"],
                                  
        ]
        #st.write(default_tracks)
        default_curve_ranges = [{st.session_state.alias['gr']:{"left":0,"right":150},
                                "Poisson_Ratio":{"left":0.1,"right":0.4}},
                                {st.session_state.alias['sonic']:{"left":240,"right":40},
                                 "DTCT":{"left":240,"right":40}},
                                {"UCS_Horsud":{"left":0,"right":100}},
                                {"OBG_AMOCO":{"left":0,"right":3},
                                 "PP_GRADIENT":{"left":0,"right":3},
                                 "SHmin_DAINES":{"left":0,"right":3},
                                 "FracGrad":{"left":0,"right":3},
                                 #"RHO":{"left":0,"right":3}
                                 },
                                {"GEOPRESSURE":{"left":0,"right":10000},
                                 "FracPressure":{"left":0,"right":10000},
                                 #"SHmin_PRESSURE":{"left":0,"right":5000},
                                 #"SHmax_PRESSURE":{"left":0,"right":5000},
                                 "MUD_PRESSURE":{"left":0,"right":10000},
                                 "SHmin_PRESSURE":{"left":0,"right":10000},
                                 "SHmax_PRESSURE":{"left":0,"right":10000},
                                 "HYDROSTATIC_PRESSURE":{"left":0,"right":10000},
                                 "OVERBURDEN_PRESSURE":{"left":0,"right":10000}
                                 },
                                
        ]
        default_curve_properties = {st.session_state.alias['gr']:{"color":"#276b02","thickness":2.0,"line_style":"solid","logarithmic":False},
                                    #"Poisson_Ratio":{"color":"#818181","thickness":1.0,"line_style":"solid","logarithmic":False},
                                    "RHO":{"color":"#b9602e","thickness":2.0,"line_style":"solid","logarithmic":False},
                                    st.session_state.alias['sonic']:{"color":"#818181","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "DTCT":{"color":"#818181","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "OBG_AMOCO":{"color":"#276b02","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "PP_GRADIENT":{"color":"#c71b1b","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "SHmin_DAINES":{"color":"#1c34aa","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    #"FracPressure":{"color":"#276b02","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "GEOPRESSURE":{"color":"#c71b1b","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "MUD_PRESSURE":{"color":"#1c34aa","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "SHmin_PRESSURE":{"color":"hotpink","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "SHmax_PRESSURE":{"color":"salmon","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "UCS_Horsud":{"color":"salmon","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    "FracPressure":{"thickness":1.5,"line_style":"dot","logarithmic":False},
                                    "OVERBURDEN_PRESSURE":{"color":"#276b02","thickness":1.5,"line_style":"solid","logarithmic":False},
                                    
                                    
                                    
        }
        tgs=[{"show":False,"values":[]},{"show":False,"values":[]},{"show":False,"values":[]},{"show":False,"values":[]},{"show":False,"values":[]}]
        vert_height=719
        fig = create_well_log_plot(
                    st.session_state.outputdata[0],
                    default_tracks,
                    default_curve_ranges,
                    default_curve_properties,
                    tgs,
                    result_dict,
                    {
                        3: {'Pore Pressure Gradient':{'color': 'red', 'size': 12, 'symbol': 'arrow-right'},
                         'Fracture Gradient':{'color': 'blue', 'size': 12, 'symbol': 'arrow-left'}},
                        4: {'Pore Pressure':{'color': 'orangered', 'size': 12, 'symbol': 'arrow-right'},
                         'Fracture Pressure':{'color': 'cornflowerblue', 'size': 12, 'symbol': 'arrow-left'}},
                        2: {'UCS':{'color': 'green', 'size': 5, 'symbol': 'circle'}},

                    },
                    plotheight,
                    header_height = 200,
                    indexkey='TVDM',
                    halftrack=0.65,
                    depthtext='DEPTH<br>metres<br>TVD<br>KB',
                    gap=7
                )
                
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(
                    dragmode=False,
                    xaxis=dict(fixedrange=True),
                    yaxis=dict(fixedrange=True)
                )
        #fig.update_yaxes(range = [curves.index.max(),curves.index.min()],autorange=False)
        st.plotly_chart(fig, use_container_width=True)
