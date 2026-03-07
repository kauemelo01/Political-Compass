import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# --- Page Config ---
st.set_page_config(
    page_title="4D Political Compass",
    layout="wide",
    initial_sidebar_state="collapsed",  # collapsed by default for mobile
)

# --- Minimal CSS: tighten padding on mobile, style tabs ---
st.markdown("""
<style>
    /* Tighten main padding on small screens */
    @media (max-width: 768px) {
        .block-container { padding: 0.5rem 0.75rem 1rem; }
        .stTabs [data-baseweb="tab"] { font-size: 0.75rem; padding: 6px 8px; }
        h1 { font-size: 1.3rem !important; }
    }
    /* Make number inputs compact */
    div[data-testid="stNumberInput"] input { font-size: 0.85rem; }
    /* Remove extra gap above title */
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("4D Political Compass")

# --- Helper: Text Wrapper ---
def wrap_text(text, width=50):
    if isinstance(text, str):
        return "<br>".join(textwrap.wrap(text, width=width))
    return text

# --- Helper: default column index ---
def get_index(lst, val):
    return lst.index(val) if val in lst else 0

# --- Helper: wrap long chart titles for mobile ---
def wrap_title(x, y, z, max_len=28):
    """Inserts a <br> before each axis name if the full title exceeds max_len chars."""
    parts = [x, y, z]
    full = "  ×  ".join(parts)
    if len(full) <= max_len:
        return full
    return "<br>".join(parts)

# ── DATA LOADING ─────────────────────────────────────────────────────────────

DEFAULT_FILE_PATH = "political_compass.csv"

@st.cache_data
def load_local_data(file_path):
    return pd.read_csv(file_path)

df = None

# File uploader lives in a compact expander so it doesn't dominate the screen
with st.expander("📂 Data Source", expanded=False):
    uploaded_file = st.file_uploader("Upload CSV (overrides default)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Loaded uploaded file.", icon="✅")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    try:
        df = load_local_data(DEFAULT_FILE_PATH)
    except FileNotFoundError:
        st.info(f"No local **{DEFAULT_FILE_PATH}** found. Upload a CSV above to continue.")
        st.stop()

# ── CONTROLS (tabbed layout — works great on mobile) ─────────────────────────

if df is not None:
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns.tolist()
    all_cols = df.columns.tolist()

    x_def = numeric_cols[0] if len(numeric_cols) > 0 else None
    y_def = numeric_cols[1] if len(numeric_cols) > 1 else None
    z_def = numeric_cols[2] if len(numeric_cols) > 2 else None

    # Four tabs replace the sidebar
    tab_axes, tab_filter, tab_display, tab_data = st.tabs(
        ["📐 Axes", "🔍 Filter", "🎨 Display", "📋 Data"]
    )

    # ── Tab 1: Axes ───────────────────────────────────────────────────────────
    with tab_axes:
        col1, col2, col3 = st.columns(3)
        with col1:
            x_axis = st.selectbox("X-Axis", numeric_cols, index=get_index(numeric_cols, x_def))
        with col2:
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=get_index(numeric_cols, y_def))
        with col3:
            z_axis = st.selectbox("Z-Axis", numeric_cols, index=get_index(numeric_cols, z_def))

        color_col = st.selectbox("Color by", all_cols, index=get_index(all_cols, "Reformist_Revolutionary"))
        label_col = st.selectbox("Label column", all_cols, index=0)

    # ── Tab 2: Filter ─────────────────────────────────────────────────────────
    with tab_filter:
        # Octant filter
        octant_options = [
            "All Data",
            "+X +Y +Z", "-X +Y +Z", "-X -Y +Z", "+X -Y +Z",
            "+X +Y -Z", "-X +Y -Z", "-X -Y -Z", "+X -Y -Z",
        ]
        selected_octant = st.selectbox("Octant / Region", octant_options)

        st.divider()

        # Dynamic column filter
        filter_col = st.selectbox("Filter by column", ["None"] + all_cols)

        if filter_col != "None":
            if pd.api.types.is_numeric_dtype(df[filter_col]):
                min_val = float(df[filter_col].min())
                max_val = float(df[filter_col].max())
                step = (max_val - min_val) / 100 if max_val > min_val else 0.1
                rng = st.slider(f"{filter_col} range", min_val, max_val, (min_val, max_val), step=step)
            else:
                unique_vals = df[filter_col].unique().tolist()
                selected_vals = st.multiselect(f"{filter_col} values", unique_vals, default=unique_vals)

    # ── Tab 3: Display ────────────────────────────────────────────────────────
    with tab_display:
        col_a, col_b = st.columns(2)
        with col_a:
            axis_min = st.number_input("Axis Min", value=-1.0, step=0.1)
            dot_size  = st.slider("Dot size", 1, 20, 5)
        with col_b:
            axis_max   = st.number_input("Axis Max", value=1.0, step=0.1)
            text_size  = st.slider("Text size", 6, 24, 10)

        show_walls  = st.checkbox("Show zero-planes (octant walls)", value=True)

        # Chart height — key for mobile: portrait screens need a shorter plot
        chart_height = st.slider("Chart height (px)", 350, 900, 520, step=10)

    # ── Tab 4: Raw data ───────────────────────────────────────────────────────
    with tab_data:
        st.caption("Filtered data will appear here after applying settings.")
        show_raw = st.checkbox("Show raw data table", value=False)

    # ── Apply filters ─────────────────────────────────────────────────────────
    df_filtered = df.copy()

    # Octant
    if selected_octant != "All Data":
        show_pos_x = "+X" in selected_octant
        show_pos_y = "+Y" in selected_octant
        show_pos_z = "+Z" in selected_octant
        df_filtered = df_filtered[df_filtered[x_axis] >= 0] if show_pos_x else df_filtered[df_filtered[x_axis] < 0]
        df_filtered = df_filtered[df_filtered[y_axis] >= 0] if show_pos_y else df_filtered[df_filtered[y_axis] < 0]
        df_filtered = df_filtered[df_filtered[z_axis] >= 0] if show_pos_z else df_filtered[df_filtered[z_axis] < 0]

    # Column filter
    if filter_col != "None":
        if pd.api.types.is_numeric_dtype(df[filter_col]):
            df_filtered = df_filtered[(df_filtered[filter_col] >= rng[0]) & (df_filtered[filter_col] <= rng[1])]
        else:
            df_filtered = df_filtered[df_filtered[filter_col].isin(selected_vals)]

    # ── Build Plot ────────────────────────────────────────────────────────────
    st.divider()

    if not (x_axis and y_axis and z_axis):
        st.warning("Please select axes in the Axes tab.")
    elif len(df_filtered) == 0:
        st.warning("No data matches the current filters.")
    else:
        df_plot = df_filtered.copy()

        # Wrap hover text
        for col in all_cols:
            if col in df_plot.columns and df_plot[col].dtype == object:
                df_plot[col] = df_plot[col].apply(lambda x: wrap_text(x, width=50))

        fig = px.scatter_3d(
            df_plot,
            x=x_axis, y=y_axis, z=z_axis,
            color=color_col,
            text=label_col,
            hover_data=all_cols,
            title=wrap_title(x_axis, y_axis, z_axis),
        )

        # Zero-plane walls
        if show_walls:
            wall_kwargs = dict(
                color="gray", opacity=0.18, hoverinfo="skip",
                i=[0, 0], j=[1, 2], k=[2, 3],
            )
            lo, hi = axis_min, axis_max
            fig.add_trace(go.Mesh3d(x=[0,0,0,0], y=[lo,hi,hi,lo], z=[lo,lo,hi,hi], name="X=0", **wall_kwargs))
            fig.add_trace(go.Mesh3d(x=[lo,hi,hi,lo], y=[0,0,0,0], z=[lo,lo,hi,hi], name="Y=0", **wall_kwargs))
            fig.add_trace(go.Mesh3d(x=[lo,hi,hi,lo], y=[lo,lo,hi,hi], z=[0,0,0,0], name="Z=0", **wall_kwargs))

        fig.update_traces(
            marker=dict(size=dot_size),
            textposition="top center",
            textfont=dict(size=text_size, color="black"),
            mode="markers+text",
            selector=dict(type="scatter3d"),
        )

        fig.update_layout(
            height=chart_height,
            scene=dict(
                xaxis=dict(title=dict(text=x_axis, font=dict(size=10)), range=[axis_min, axis_max]),
                yaxis=dict(title=dict(text=y_axis, font=dict(size=10)), range=[axis_min, axis_max]),
                zaxis=dict(title=dict(text=z_axis, font=dict(size=10)), range=[axis_min, axis_max]),
                aspectmode="cube",
                # Slightly adjusted default camera angle — better on portrait screens
                camera=dict(eye=dict(x=1.4, y=1.4, z=0.8)),
            ),
            margin=dict(l=0, r=0, b=80, t=36),
            coloraxis_colorbar=dict(
                orientation="h",       # horizontal bar below the chart
                x=0.5, xanchor="center",
                y=-0.12, yanchor="top",
                len=0.6,               # 60% of plot width
                thickness=12,
                title=dict(side="bottom", font=dict(size=9)),
                tickfont=dict(size=8),
            ),
            legend=dict(
                orientation="h",       # horizontal legend — saves vertical space on mobile
                yanchor="bottom", y=1.01,
                xanchor="right",  x=1,
                font=dict(size=9),
            ),
        )

        # Render as raw HTML so Plotly owns the touch events directly —
        # st.plotly_chart wraps in an iframe that intercepts pinch gestures.
        chart_html = fig.to_html(
            include_plotlyjs="cdn",
            full_html=True,
            config={"scrollZoom": True, "responsive": True},
        )
        components.html(chart_html, height=chart_height + 60, scrolling=False)

        # Raw data (optional)
        if show_raw:
            with tab_data:
                st.dataframe(df_filtered, use_container_width=True)

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.caption(f"Showing **{len(df_filtered)}** of **{len(df)}** entries")
