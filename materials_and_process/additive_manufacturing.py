import streamlit as st
import yaml
import re
import os
import base64
from streamlit.components.v1 import html

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Minimal CSS for clean appearance
st.markdown("""
    <style>
    .main {
        font-family: 'Arial', sans-serif;
    }
    .stSelectbox > div > div {
        border: 1px solid #007bff;
        border-radius: 5px;
        padding: 8px;
        font-size: 16px;
    }
    .data-section {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Functions ---

# Parse YAML with unit comments
def load_yaml_with_units(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        units = {}
        key_stack = []
        for line in lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            while key_stack and key_stack[-1][0] >= indent:
                key_stack.pop()
            match_key = re.match(r'^\s*([\w\-]+)\s*:', line)
            if match_key:
                key = match_key.group(1)
                full_key = ".".join([k[1] for k in key_stack] + [key])
                key_stack.append((indent, key))
            else:
                full_key = ".".join([k[1] for k in key_stack]) if key_stack else ""

            match_comment = re.search(r'#\s*(\S+)', line)
            if match_comment and full_key:
                units[full_key] = match_comment.group(1)
        return data, units
    except Exception as e:
        return {"error": f"Failed to load {file_path}: {str(e)}"}, {}

# Recursively format YAML data
def format_data(data, units):
    result = []

    def recurse(key, value, path=""):
        full_key = f"{path}.{key}" if path else key
        display_key = key.replace("-", " ").title()
        level = path.count(".")
        if isinstance(value, dict):
            result.append((level, f"**{display_key}**", ""))
            for sub_key, sub_val in value.items():
                recurse(sub_key, sub_val, full_key)
        else:
            unit = units.get(full_key, "")
            result.append((level, display_key, f"{value} {unit}".strip()))

    for key, val in data.items():
        recurse(key, val)
    return result

# Display zoomable image
def display_zoomable_image(image_path):
    if not os.path.exists(image_path):
        st.write(f"Image not found: {image_path}")
        return
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    html(f"""
        <div style="overflow:hidden; border-radius:10px; border:1px solid #ccc">
            <img src="data:image/jpeg;base64,{encoded}" style="width:100%; transition:0.3s ease"
                 onmouseover="this.style.transform='scale(1.05)'"
                 onmouseout="this.style.transform='scale(1)'">
        </div>
    """, height=300)

# --- UI App ---

st.title("Material and Process Data Viewer")
st.write("Explore LPBF of TiB2-modified Al-Mg-Si-Zr alloys.")

# File and image mapping
file_map = {
    "Process": {
        "yaml": os.path.join(SCRIPT_DIR, "lpbf_process.yaml"),
        "image": os.path.join(SCRIPT_DIR, "lpbf-process.jpg"),
        "description": "Laser powder bed fusion parameters."
    },
    "Alloy Matrix": {
        "yaml": os.path.join(SCRIPT_DIR, "base_materials.yaml"),
        "image": os.path.join(SCRIPT_DIR, "base-alloy.jpg"),
        "description": "Base aluminum alloy chemistry and properties."
    },
    "Composite Blend": {
        "yaml": os.path.join(SCRIPT_DIR, "composite_powder.yaml"),
        "image": os.path.join(SCRIPT_DIR, "composite-powder.jpg"),
        "description": "Details of powder blends with TiB₂."
    }
}

# Dropdown
selected_option = st.selectbox(
    "Select Data",
    list(file_map.keys()),
    index=0,
    help="Choose which dataset to explore: Process, Matrix, or Composite."
)
st.caption(file_map[selected_option]["description"])

# Load data
file_path = file_map[selected_option]["yaml"]
image_path = file_map[selected_option]["image"]
data, units = load_yaml_with_units(file_path)

# Layout: two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader(selected_option)
    formatted = format_data(data, units)
    if formatted:
        section = []
        for level, key, val in formatted:
            if level == 0 and section:
                st.markdown(f'<div class="data-section">{"<br>".join(section)}</div>', unsafe_allow_html=True)
                section = []
            if level == 0:
                section.append(f"{key}")
            else:
                indent = level * 12
                section.append(f'<div style="margin-left:{indent}px">- <strong>{key}</strong>: {val}</div>')
        if section:
            st.markdown(f'<div class="data-section">{"<br>".join(section)}</div>', unsafe_allow_html=True)
    else:
        st.write("No data available.")

with col2:
    display_zoomable_image(image_path)
