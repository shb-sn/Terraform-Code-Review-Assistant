import streamlit as st

from c_ui import (
    render_sidebar,
    render_auth_gate,
    render_upload_section,
    render_validation_results,
    render_recommendations,
    render_reviewed_output,
    render_footer,
)

st.set_page_config(
    page_title="Terraform Code Review Assistant",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

_defaults = {
    "dark_mode": True,
    "authenticated": False,
    "current_user": None,
    "validation_results": None,
    "file_id": None,
    "original_tf": None,
    "original_filename": None,
    "recommendations": [],
    "reviewed_tf": None,
    "review_summary": None,
}
for _key, _val in _defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val


render_sidebar()

if render_auth_gate():
    st.stop()  # not authenticated yet — nothing below renders

render_upload_section()
render_validation_results()
render_recommendations()
render_reviewed_output()
render_footer()