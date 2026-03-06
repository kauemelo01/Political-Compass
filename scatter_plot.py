import textwrap

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Set page configuration
st.set_page_config(page_title="3D Political Compass Viewer", layout="wide")
st.title("Interactive 3D Scatter Plot Dashboard")

# --- 1. Load Data ---
# Reverted to st.cache for compatibility with older Streamlit versions
@st.cache(allow_output_mutation=True)
def load_data(file_or_path):
    return pd.read_csv(file_or_path)


# --- Helper: Text Wrapper ---
def wrap_text(text, width=50):
    if isinstance(text, str):
        return "<br>".join(textwrap.wrap(text, width=width))
    return text


# --- FILE LOADING LOGIC ---
# Using the absolute path structure from your environment
DEFAULT_FILE_PATH = (
    "/home/kaue.melo/kaue.melo_nfs/streamlit_dashboard/political_compass.csv"
)

# Sidebar for controls
st.sidebar.header("Data Configuration")
uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV (Overrides default)", type=["csv"]
)

df = None

# 1. Try to load the uploaded file first
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.sidebar.success("Successfully loaded uploaded file.")
    except Exception as e:
        st.sidebar.error(f"Error reading uploaded file: {e}")
        st.stop()

# 2. If no upload, try to load the default absolute path
else:
    try:
        df = load_data(DEFAULT_FILE_PATH)
        st.sidebar.success("Automatically loaded local file.")
    except FileNotFoundError:
        st.info(
            f"Could not find **{DEFAULT_FILE_PATH}**. Please upload a CSV file to continue."
        )
        st.stop()  # Stops the app from crashing while waiting for a file

# --- MAIN DASHBOARD LOGIC ---
if df is not None:
    # --- 2. Axis Selection ---
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns.tolist()
    all_cols = df.columns.tolist()

    def get_index(lst, val):
        return lst.index(val) if val in lst else 0

    x_def = numeric_cols[0] if len(numeric_cols) > 0 else None
    y_def = numeric_cols[1] if len(numeric_cols) > 1 else None
    z_def = numeric_cols[2] if len(numeric_cols) > 2 else None

    st.sidebar.subheader("Axis Mapping")
    x_axis = st.sidebar.selectbox("X-Axis", numeric_cols, index=get_index(numeric_cols, x_def))
    y_axis = st.sidebar.selectbox("Y-Axis", numeric_cols, index=get_index(numeric_cols, y_def))
    z_axis = st.sidebar.selectbox("Z-Axis", numeric_cols, index=get_index(numeric_cols, z_def))

    color_col = st.sidebar.selectbox("Color Dimension", all_cols, index=0)

    # --- 3. Filter Octants ---
    st.sidebar.subheader("Filter Octants")

    octant_options = [
        "All Data",
        "+X +Y +Z (Top-Right-Front)",
        "-X +Y +Z (Top-Left-Front)",
        "-X -Y +Z (Bottom-Left-Front)",
        "+X -Y +Z (Bottom-Right-Front)",
        "+X +Y -Z (Top-Right-Back)",
        "-X +Y -Z (Top-Left-Back)",
        "-X -Y -Z (Bottom-Left-Back)",
        "+X -Y -Z (Bottom-Right-Back)",
    ]

    selected_octant = st.sidebar.selectbox("Select Region", octant_options)

    # Apply Octant Filtering
    if selected_octant != "All Data":
        show_pos_x = "+X" in selected_octant
        show_pos_y = "+Y" in selected_octant
        show_pos_z = "+Z" in selected_octant

        if show_pos_x:
            df = df[df[x_axis] >= 0]
        else:
            df = df[df[x_axis] < 0]

        if show_pos_y:
            df = df[df[y_axis] >= 0]
        else:
            df = df[df[y_axis] < 0]

        if show_pos_z:
            df = df[df[z_axis] >= 0]
        else:
            df = df[df[z_axis] < 0]

    # --- 4. Dynamic Column Filter ---
    st.sidebar.subheader("Dynamic Data Filter")

    # Add "None" as the first option so filtering is optional
    filter_col = st.sidebar.selectbox("Filter by Column", ["None"] + all_cols)

    if filter_col != "None":
        # Check if column is numeric
        if pd.api.types.is_numeric_dtype(df[filter_col]):
            min_val = float(df[filter_col].min())
            max_val = float(df[filter_col].max())
            # Ensure step is non-zero
            step = (max_val - min_val) / 100 if max_val > min_val else 0.1

            # Create a double-ended slider
            rng = st.sidebar.slider(
                f"Range for {filter_col}",
                min_val,
                max_val,
                (min_val, max_val),
                step=step,
            )
            df = df[(df[filter_col] >= rng[0]) & (df[filter_col] <= rng[1])]
        else:
            # Categorical/Text column
            unique_vals = df[filter_col].unique().tolist()
            selected_vals = st.sidebar.multiselect(
                f"Select values for {filter_col}",
                unique_vals,
                default=unique_vals,
            )
            df = df[df[filter_col].isin(selected_vals)]

    # --- 5. Label Settings ---
    st.sidebar.subheader("Label Settings")
    label_col = st.sidebar.selectbox("Label Column (Text)", all_cols, index=0)
    text_size = st.sidebar.slider("Text Size", min_value=6, max_value=24, value=10)

    # --- 6. Graph Range & Walls ---
    st.sidebar.subheader("Graph Range & Walls")
    col1, col2 = st.sidebar.columns(2)

    with col1:
        axis_min = st.number_input("Axis Min", value=-1.0, step=0.1)
    with col2:
        axis_max = st.number_input("Axis Max", value=1.0, step=0.1)

    show_walls = st.sidebar.checkbox("Show Zero Walls (Quadrants)", value=True)
    dot_size = st.sidebar.slider("Dot Size", 1, 20, 5)

    # Define hover data (Defaulting to all columns since UI was removed)
    hover_data = all_cols

    # --- 7. Data Preparation ---
    df_plot = df.copy()

    # Apply text wrapping to all hover columns if they are strings
    for col in hover_data:
        if col in df_plot.columns and df_plot[col].dtype == object:
            df_plot[col] = df_plot[col].apply(lambda x: wrap_text(x, width=50))

    # --- 8. Generate Plot ---
    if x_axis and y_axis and z_axis:
        if len(df_plot) == 0:
            st.warning("No data found with the current filters.")
        else:
            # 8a. Create Base Scatter
            fig = px.scatter_3d(
                df_plot,
                x=x_axis,
                y=y_axis,
                z=z_axis,
                color=color_col,
                text=label_col,
                hover_data=hover_data,
                title=f"3D Scatter: {x_axis} vs {y_axis} vs {z_axis}",
            )

            # 8b. Add Zero Walls
            if show_walls:
                i_idx = [0, 0]
                j_idx = [1, 2]
                k_idx = [2, 3]

                # Wall Style
                wall_style = dict(
                    color="gray",
                    opacity=0.2,
                    hoverinfo="skip",
                    i=i_idx,
                    j=j_idx,
                    k=k_idx,
                )

                # X=0 Plane
                fig.add_trace(
                    go.Mesh3d(
                        x=[0, 0, 0, 0],
                        y=[axis_min, axis_max, axis_max, axis_min],
                        z=[axis_min, axis_min, axis_max, axis_max],
                        **wall_style,
                        name="X=0",
                    )
                )

                # Y=0 Plane
                fig.add_trace(
                    go.Mesh3d(
                        x=[axis_min, axis_max, axis_max, axis_min],
                        y=[0, 0, 0, 0],
                        z=[axis_min, axis_min, axis_max, axis_max],
                        **wall_style,
                        name="Y=0",
                    )
                )

                # Z=0 Plane
                fig.add_trace(
                    go.Mesh3d(
                        x=[axis_min, axis_max, axis_max, axis_min],
                        y=[axis_min, axis_min, axis_max, axis_max],
                        z=[0, 0, 0, 0],
                        **wall_style,
                        name="Z=0",
                    )
                )

            # 8c. Update Layout
            fig.update_traces(
                marker=dict(size=dot_size),
                textposition="top center",
                textfont=dict(size=text_size, color="black"),
                mode="markers+text",
                selector=dict(type="scatter3d"),
            )

            fig.update_layout(
                scene=dict(
                    xaxis=dict(title=x_axis, range=[axis_min, axis_max]),
                    yaxis=dict(title=y_axis, range=[axis_min, axis_max]),
                    zaxis=dict(title=z_axis, range=[axis_min, axis_max]),
                    aspectmode="cube",
                ),
                margin=dict(l=0, r=0, b=0, t=40),
            )

            st.plotly_chart(fig, use_container_width=True)

            # Show filtered raw data
            with st.expander("View Raw Data"):
                st.dataframe(df)