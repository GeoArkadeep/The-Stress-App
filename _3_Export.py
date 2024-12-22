"""
Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED
This file is part of "The Stress App" project and is released under the 
GNU Affero General Public License v3.0 (AGPL-3.0)
See the GNU Affero General Public License for more details: <https://www.gnu.org/licenses/agpl-3.0.html>
"""

import streamlit as st

if 'las_file' not in st.session_state or st.session_state.las_file is None or 'outputdata' not in st.session_state:
    st.switch_page("_1_Import.py")

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")
if 'outputdata' in st.session_state and st.session_state.outputdata[0] is not None:
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
                
    with cols[1]:
        with st.container(height=724):
            
            st.session_state.outputdata[0]
st.markdown("""
<div class="bottom-banner-container">
    <div class="bottom-banner-copyright">Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED</div>
</div>

<style>
    /* Load the fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron&family=Oxanium:wght@400&display=swap');

    /* Styling for the bottom banner container */
    .bottom-banner-container {
        position: fixed; /* Sticks to the bottom of the viewport */
        bottom: 5%; /* Positioned at 5% from the bottom of the viewport */
        left: 47.5%;
        #text-align: center; /* Center the content */
        z-index: 9999; /* Ensure it appears above other content */
    }

    /* Styling for the subtitle text */
    .bottom-banner-subtitle {
        font-family: 'Oxanium', sans-serif;
        font-size: 3vw; /* Dynamically adjusts to 3% of the viewport width */
        color: rgba(128, 128, 128, 0.8); /* Slightly higher opacity for visibility */
        margin: 0;
        #text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* Add subtle shadow for better contrast */
    }

    /* Styling for the copyright text */
    .bottom-banner-copyright {
        font-family: 'Oxanium', sans-serif;
        font-size: 1.5vw; /* Dynamically adjusts to 1.5% of the viewport width */
        color: rgba(128, 128, 128, 0.7); /* Slightly less opacity for distinction */
        margin: 0;
        margin-top: 5px; /* Add spacing between lines */
        #text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5); /* Subtle shadow for visibility */
    }

    /* Media queries for fine-tuning font sizes */
    @media (max-width: 600px) {
        .bottom-banner-subtitle {
            font-size: 4vw; /* Slightly larger for smaller screens */
        }
        .bottom-banner-copyright {
            font-size: 2.5vw; /* Adjust copyright size for small screens */
        }
    }

    @media (min-width: 1200px) {
        .bottom-banner-subtitle {
            font-size: 20px; /* Fixed size for larger screens */
        }
        .bottom-banner-copyright {
            font-size: 15px; /* Fixed size for larger screens */
        }
    }
</style>

""", unsafe_allow_html=True)