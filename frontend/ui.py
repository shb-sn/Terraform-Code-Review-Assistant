import requests
import streamlit as st
import re
from st_keyup import st_keyup
from config import VALIDATOR_META
from theme import inject_css, category_badge, severity_badge, render_side_by_side_diff
from auth import signup_user, login_user, logout_user, is_valid_email
from api import upload_file, apply_recommendations

def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        dark = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode)
        st.session_state.dark_mode = dark

        st.divider()
        if st.session_state.authenticated:
            st.markdown(f"**👤 {st.session_state.current_user['name']}**")
            st.caption(st.session_state.current_user["email"])
            if st.button("Log out", use_container_width=True):
                logout_user()
                st.rerun()

    inject_css(st.session_state.dark_mode)



def render_auth_gate():
    #Renders login/signup UI. Returns True if the app should stop here
    #(i.e. the user is not yet authenticated).
    if st.session_state.authenticated:
        return False

    st.title("🛠️ Terraform Code Review Assistant")
    st.caption("Sign in to upload and review your Terraform configurations.")

    left, right = st.columns([1, 1])
    with left:
        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])

            with tab_login:
                login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
                login_password = st.text_input("Password", type="password", key="login_password")
                if st.button("Log In", type="primary", use_container_width=True):
                    ok, msg = login_user(login_email, login_password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            with tab_signup:
                su_name = st.text_input("Full name", key="su_name")
                su_email = st.text_input("Email", key="su_email", placeholder="you@example.com")

                email_typed = st.session_state.get("su_email", "")
                if email_typed:
                    if is_valid_email(email_typed):
                        st.caption("✅ Valid email format")
                    else:
                        st.caption("❌ Invalid email format")

                #su_password = st.text_input("Password", type="password", key="su_password")
                su_password = st_keyup(
                    "Password", key="su_password", debounce=200, placeholder="Type a password"
                ) or ""
                pw_checks= [
                        ("At least 8 characters", len(su_password) >= 8),
                        ("One uppercase letter", bool(re.search(r"[A-Z]", su_password))),
                        ("One lowercase letter", bool(re.search(r"[a-z]", su_password))),
                        ("One number", bool(re.search(r"\d" , su_password))),
                        ("One special character ", bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]" , su_password))),
                         ]
                password_valid = all(ok for _, ok in pw_checks)
                checklist_html="<br>".join(  
                            f"{'✅'if ok else '❌' }{label}" for label, ok in pw_checks)                
                st.markdown(f'<div class="subtext">{checklist_html}</div>' , unsafe_allow_html=True)                    
                if su_password and not password_valid:
                    st.warning("⚠️ Password does not meet all the requirements.")
               
                su_confirm = st.text_input("Confirm password", type="password", key="su_confirm")
               
                if st.button("Create Account", type="primary", use_container_width=True):
                    if not password_valid:
                        pass
                    elif su_password != su_confirm:
                        st.error("❌ Passwords do not match.")
                    else:
                       
                        ok, msg = signup_user(su_name, su_email, su_password, su_confirm)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
   

    return True



def render_upload_section():
    st.title("🛠️ Terraform Code Review Assistant")
    st.caption("Upload a `.tf` file to run it through syntax, formatting, security, "
               "configuration, best-practice, and cost-optimization validators.")

    with st.container(border=True):
        st.subheader("1. Upload Terraform File")
        uploaded_file = st.file_uploader("Choose a .tf file", type=["tf"])

        col1, _ = st.columns([1, 5])
        with col1:
            run_review = st.button("🚀 Run Review", type="primary", disabled=uploaded_file is None)

        if run_review and uploaded_file is not None:
            with st.spinner("Uploading and running validators..."):
                try:
                    raw_bytes = uploaded_file.getvalue()
                    st.session_state.original_tf = raw_bytes.decode("utf-8", errors="replace")
                    st.session_state.original_filename = uploaded_file.name

                    result = upload_file(uploaded_file)
                    st.session_state.validation_results = result
                    st.session_state.file_id = result.get("file_id")
                    st.session_state.recommendations = [
                        {**rec, "status": "pending"}
                        for rec in result.get("recommendations", [])
                    ]
                    st.session_state.reviewed_tf = None
                    st.session_state.review_summary = None
                    st.success("Validation complete.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Upload failed: {e}")


def render_validation_results():
    results = st.session_state.validation_results
    if not results:
        return

    st.subheader("2. Validation Results & Recommendations")
    recs=st.session_state.get("recommendations") or []
    if recs:
        bulk_col1, bulk_col2, _= st.columns([1,1,4])
        with bulk_col1:
            if st.button("✅ Accept All"):
                for r in recs:
                    r["status"]="accepted"
        with bulk_col2:
            if st.button("❌ Reject All"):
                for r in recs:
                    r["status"]="rejected"
    tabs= st.tabs([f"{m['icon']} {m['label']}" for m in VALIDATOR_META.values()])
    shown_rec_indices=set()
   
   
    for tab,(key,meta) in zip(tabs, VALIDATOR_META.items()):
        with tab:
            report = results.get(f"{key}_report") or results.get(key) or {}
            issues = report.get("issues",[]) if isinstance(report,dict) else []
           
            if not issues:
                st.info(f"No issues found by the {meta['label']} validator.")
            else:
                for issue in issues:
                    sev= severity_badge(issue.get("severity","medium"))
                    st.markdown(
                        f"{sev} {category_badge(key)} **{issue.get('title','Issue')}**"
                        f"- {issue.get('description','')}",
                        unsafe_allow_html=True,
                    )
                    if issue.get("line"):
                        st.markdown(f'<span class="subtext">Line {issue["line"]}</span>' , unsafe_allow_html=True)
                    st.divider()
           
            cat_recs=[(i,r) for i,r in enumerate(recs) if r.get("category", "general") == key]
            if cat_recs:
                st.markdown(f"**Suggested fixes- {meta['label']}**")
                for i, rec in cat_recs:
                    shown_rec_indices.add(i)
                    with st.container(border=True):
                        c1,c2=st.columns([5,2])
                        with c1:
                            st.markdown(
                                f"{category_badge(rec.get('category', 'general'))} {rec.get('message', '')}",
                                unsafe_allow_html=True,
                            )  
                            if rec.get("fix_preview"):
                                st.code(rec["fix_preview"], language="hcl")
                        with c2:
                            choice=st.radio(
                                "Decision",
                                ["Pending", "Accept", "Reject"],
                                index=["pending", "accepted", "rejected"].index(rec.get("status", "pending").strip().lower()),
                                key=f"rec_{i}",
                                horizontal=True,
                                label_visibility="collapsed",
                            )
                            st.session_state.recommendations[i]["status"]= (
                                choice.lower().replace("accept","accepted").replace("reject", "rejected")
                            )
    leftover = [(i,r) for i, r in enumerate(recs) if i not in shown_rec_indices]
    if leftover:
        st.markdown("**Other recommendations**")
        for i, rec in leftover:
            with st.container(border=True):
                c1,c2=st.columns([5,2])
                with c1:
                            st.markdown(
                                f"{category_badge(rec.get('category', 'general'))} {rec.get('message', '')}",
                                unsafe_allow_html=True,
                            )  
                            if rec.get("fix_preview"):
                                st.code(rec["fix_preview"], language="hcl")
                with c2:
                            choice=st.radio(
                                "Decision",
                                ["Pending", "Accept", "Reject"],
                                index=["pending", "accepted", "rejected"].index(rec.get("status", "pending").strip().lower()),
                                key=f"rec_{i}",
                                horizontal=True,
                                label_visibility="collapsed",
                            )
                            st.session_state.recommendations[i]["status"]= (
                                choice.lower().replace("accept","accepted").replace("reject", "rejected")
                            )
    if recs:
        st.divider()
        if st.button("Apply Selected Recommendations",type="primary"):
            decisions=[
                {"id": r.get("id",idx), "status": r["status"]}
                for idx,r in enumerate(recs)
                if r["status"] in ("accepted","rejected")
                ]
            with st.spinner("Applying changes..."):
                try:
                    st.write("Current File ID:", st.session_state.file_id)
                    apply_result = apply_recommendations(st.session_state.file_id,decisions)
                    st.session_state.reviewed_tf= apply_result.get("reviewed_tf")
                    st.write("Apply Result:", apply_result)
                    st.write("Reviewed TF:", st.session_state.reviewed_tf)
                    st.session_state.review_summary = apply_result.get("summary")
                    st.success("Recommendations applied.")
                except Exception as e:
                    st.error(f"Failed to apply recommendations: {e}")
               
                               
                           


def render_recommendations():
   return


def render_reviewed_output():
    if not st.session_state.reviewed_tf:
        return

    st.subheader("3. Reviewed Terraform File")

    if st.session_state.review_summary:
        with st.expander("📊 Change summary", expanded=False):
            st.json(st.session_state.review_summary)

    view_tab, diff_tab = st.tabs(["📄 Reviewed File", "🔀 Side-by-Side Comparison"])

    with view_tab:
        st.code(st.session_state.reviewed_tf, language="hcl")
        st.download_button(
            label="⬇️ Download reviewed file",
            data=st.session_state.reviewed_tf,
            file_name=st.session_state.original_filename,
            mime="text/plain",
            type="primary",
        )

    with diff_tab:
        if not st.session_state.original_tf:
            st.info("Original file content isn't available for comparison in this session.")
        else:
            if st.session_state.original_tf.strip() == st.session_state.reviewed_tf.strip():
                st.success("No differences — the reviewed file matches the original.")
            diff_html = render_side_by_side_diff(
                st.session_state.original_tf,
                st.session_state.reviewed_tf,
                st.session_state.dark_mode,
            )
            st.markdown(diff_html, unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Download reviewed.tf",
                data=st.session_state.reviewed_tf,
                file_name="reviewed.tf",
                mime="text/plain",
                key="diff_download",
            )


def render_footer():
    st.divider()
    st.caption("Files are stored temporarily and deleted after processing. "
               "The original uploaded file is never modified.")