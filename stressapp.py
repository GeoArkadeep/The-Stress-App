"""
Copyright (c) 2024-2025 ROCK LAB PRIVATE LIMITED
This file is part of "The Stress App" project and is released under the 
GNU Affero General Public License v3.0 (AGPL-3.0)
See the GNU Affero General Public License for more details: <https://www.gnu.org/licenses/agpl-3.0.html>
"""

import streamlit as st
st.set_page_config(layout="wide")


input_page = st.Page("_1_Import.py", title="Import Data", icon=":material/upload_file:")
geomech_page = st.Page("_2_Geomech.py", title="Calculate Stresses", icon=":material/modeling:")
export_page = st.Page("_3_Export.py", title="Export Data", icon=":material/file_save:")

pg = st.navigation([input_page, geomech_page, export_page])

pg.run()