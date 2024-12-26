"""
Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED
This file is part of "The Stress App" project and is released under the 
GNU Affero General Public License v3.0 (AGPL-3.0)
See the GNU Affero General Public License for more details: <https://www.gnu.org/licenses/agpl-3.0.html>
"""

import streamlit as st
import io
from _6_E_mob import mobile_export

if 'las_file' not in st.session_state or st.session_state.las_file is None or 'outputdata' not in st.session_state:
    st.switch_page("_1_Import.py")

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")
if 'outputdata' in st.session_state and st.session_state.outputdata[0] is not None:
    if st.session_state.mobile_version:
        mobile_export()
    else:
        cols = st.columns([1,2])
        with cols[0]:
            with st.container(height=724):
                if st.session_state.outputdata[1] is not None:
                    st.title("EXPORT DATA")
                    if st.button('Back to Calculations',type="primary", use_container_width=True):
                                st.switch_page("_2_Geomech.py")
                    csv = convert_df(st.session_state.outputdata[0])

                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name="large_df.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    buffer = io.BytesIO()
                    st.session_state.outputdata[0].to_excel(buffer, index=False)
                    buffer.seek(0)
                    excel_data = buffer.getvalue()

                    st.download_button(
                        label="Download data as Excel",
                        data=excel_data,
                        file_name="WellData.xslx",
                        mime="text/csv",
                        use_container_width=True
                    )
                   
                    # Streamlit download button
                    #st.session_state.outputdata[1]
                    las_content = st.session_state.outputdata[1]

                    st.download_button(
                        label="Download Processed LAS File",
                        data=las_content,
                        file_name="well_data.las",
                        mime="text/plain",
                        use_container_width=True
                    )
                    "---"
                    if st.button("Start over fresh", type="primary", use_container_width=True):
                        for key in st.session_state.keys():
                            del st.session_state[key]
                        st.rerun()
                    
        with cols[1]:
            with st.container(height=724):
                
                st.session_state.outputdata[0]
