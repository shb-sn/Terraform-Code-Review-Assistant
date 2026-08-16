import difflib
import html as html_lib

import streamlit as st
from pathlib import Path

from config import VALIDATOR_META

@st.cache_data(show_spinner=False)
def _compute_diff_rows(original: str, reviewed: str):
    #Cached so re-rendering (e.g. switching tabs) doesn't recompute the diff

    orig_lines = original.splitlines()
    rev_lines = reviewed.splitlines()

    matcher = difflib.SequenceMatcher(a=orig_lines, b=rev_lines)

    rows = []
    ln_l, ln_r = 1, 1

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():

        if tag == "equal":
            for l, r in zip(orig_lines[i1:i2], rev_lines[j1:j2]):
                esc = html_lib.escape(l)
                rows.append((ln_l, esc, "equal", ln_r, esc, "equal"))
                ln_l += 1
                ln_r += 1

        elif tag == "replace":
            left_block = orig_lines[i1:i2]
            right_block = rev_lines[j1:j2]

            for k in range(max(len(left_block), len(right_block))):
                l = html_lib.escape(left_block[k]) if k < len(left_block) else ""
                r = html_lib.escape(right_block[k]) if k < len(right_block) else ""

                l_num = ln_l if k < len(left_block) else ""
                r_num = ln_r if k < len(right_block) else ""

                rows.append(
                    (
                        l_num,
                        l,
                        "chg" if l else "",
                        r_num,
                        r,
                        "chg" if r else "",
                    )
                )

                if k < len(left_block):
                    ln_l += 1

                if k < len(right_block):
                    ln_r += 1

        elif tag == "delete":
            for l in orig_lines[i1:i2]:
                rows.append(
                    (
                        ln_l,
                        html_lib.escape(l),
                        "del",
                        "",
                        "",
                        "",
                    )
                )
                ln_l += 1

        elif tag == "insert":
            for r in rev_lines[j1:j2]:
                rows.append(
                    (
                        "",
                        "",
                        "",
                        ln_r,
                        html_lib.escape(r),
                        "add",
                    )
                )
                ln_r += 1

    return rows

def inject_css(dark: bool):
    if dark:
        bg, panel, text, subtext, border = "#0F1117", "#1A1D27", "#F1F3F5", "#A6A9B4", "#2A2E3A"
    else:
        bg, panel, text, subtext, border = "#F7F8FC", "#FFFFFF", "#1A1D27", "#5C5F6A", "#E4E6EF"

    css = Path("style.css").read_text(encoding="utf-8")
 
    css = css.replace("{BG}", bg)
    css = css.replace("{PANEL}", panel)
    css = css.replace("{TEXT}", text)
    css = css.replace("{SUBTEXT}", subtext)
    css = css.replace("{BORDER}", border)
 
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def category_badge(key: str) -> str:
    meta = VALIDATOR_META.get(key, {"label": key.title(), "color": "#868E96"})
    return f'<span class="badge" style="background:{meta["color"]}">{meta["label"]}</span>'


def severity_badge(severity) -> str:
    colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    return colors.get(str(severity).lower(), "⚪")


def render_side_by_side_diff(original: str, reviewed: str, dark: bool) -> str:
    #Build an HTML two-column, line-aligned diff view (like a code review tool)
    if dark:
        bg, border, text, gutter = "#12141C", "#2A2E3A", "#E9ECEF", "#5C5F6A"
        del_bg, add_bg, chg_bg = "#3B1A22", "#123A2A", "#3B2E12"
    else:
        bg, border, text, gutter = "#FFFFFF", "#E4E6EF", "#1A1D27", "#8A8D99"
        del_bg, add_bg, chg_bg = "#FFE3E3", "#D3F9D8", "#FFF3BF"

    orig_lines = original.splitlines()
    rev_lines = reviewed.splitlines()
    matcher = difflib.SequenceMatcher(a=orig_lines, b=rev_lines)

    rows = _compute_diff_rows(original, reviewed)  

    row_html = []
    for l_num, l_text, l_bg, r_num, r_text, r_bg in rows:
        color_map = {
            "add": add_bg,
            "del": del_bg,
            "chg": chg_bg,
            "equal": "",
            "": ""
        }
 
        l_bg = color_map.get(l_bg, "")
        r_bg = color_map.get(r_bg, "")
        l_style = f"background:{l_bg};" if l_bg else ""
        r_style = f"background:{r_bg};" if r_bg else ""
        row_html.append(
            f'<tr>'
            f'<td style="color:{gutter};text-align:right;padding:0 8px;user-select:none;width:40px;">{l_num}</td>'
            f'<td style="{l_style}padding:1px 10px;white-space:pre;">{l_text}</td>'
            f'<td style="color:{gutter};text-align:right;padding:0 8px;user-select:none;width:40px;">{r_num}</td>'
            f'<td style="{r_style}padding:1px 10px;white-space:pre;">{r_text}</td>'
            f'</tr>'
        )

    legend = f"""
    <div style="margin-bottom:8px;font-size:0.8rem;color:{text};">
      <span style="background:{del_bg};padding:1px 8px;border-radius:4px;">removed</span>
      &nbsp;
      <span style="background:{add_bg};padding:1px 8px;border-radius:4px;">added</span>
      &nbsp;
      <span style="background:{chg_bg};padding:1px 8px;border-radius:4px;">changed</span>
    </div>
    """

    table = f"""
    {legend}
    <div style="max-height:600px;overflow:auto;border:1px solid {border};border-radius:12px;">
    <table style="width:100%;border-collapse:collapse;font-family:'Source Code Pro',monospace;
                   font-size:0.85rem;color:{text};background:{bg};">
      <thead>
        <tr style="position:sticky;top:0;background:{bg};border-bottom:1px solid {border};">
          <th colspan="2" style="text-align:left;padding:6px 10px;">Original</th>
          <th colspan="2" style="text-align:left;padding:6px 10px;">Reviewed</th>
        </tr>
      </thead>
      <tbody>
        {''.join(row_html)}
      </tbody>
    </table>
    </div>
    """
    return table