import streamlit as st
import yaml
import re
import os

# Light CSS for clean, pleasing appearance
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
    .stImage > img {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        max-width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Function to read YAML file and extract units from comments
def load_yaml_with_units(file_path):
    try:
        # Read raw file to parse comments
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Parse YAML for data
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        
        # Extract units from comments
        units = {}
        current_key = None
        for line in lines:
            line = line.strip()
            # Match key-value lines
            if ':' in line and not line.startswith('#'):
                key = line.split(':')[0].strip()
                current_key = key
            # Match comments with units (e.g., "# mm")
            if line.startswith('#') and current_key:
                match = re.search(r'#\s*(\S+)', line)
                if match:
                    units[current_key] = match.group(1)
        return data, units
    except Exception as e:
        return {"error": f"Failed to load {file_path}: {str(e)}"}, {}

# Function to format YAML data into grouped, readable sections
def format_data(data, units):
    result = []
    def process_item(key, value, parent_key="", level=0):
        display_key = key.replace("-", " ").title()
        if isinstance(value, dict):
            # Group nested items under a section
            result.append((level, f"**{display_key}**", ""))
            for sub_key, sub_value in value.items():
                process_item(sub_key, sub_value, f"{parent_key}.{key}" if parent_key else key, level + 1)
        elif isinstance(value, list):
            # Handle lists (e.g., laser_power)
            unit = units.get(key, "[]")
            result.append((level, display_key, f"{value} {unit}"))
        else:
            # Handle scalar values
            unit = units.get(key, "[]")
            result.append((level, display_key, f"{value} {unit}"))
    
    for key, value in data.items():
        process_item(key, value)
    return result

# Streamlit app
st.title("Material and Process Data Viewer")
st.write("Explore LPBF of TiB2-modified Al-Mg-Si-Zr alloys.")

# Mapping of display names to YAML files and images
file_map = {
    "Process": {"yaml": "lpbf_process.yaml", "image": "lpbf-process.jpg"},
    "Alloy Matrix": {"yaml": "base_materials.yaml", "image": "base-alloy.jpg"},
    "Composite Blend": {"yaml": "composite_powder.yaml", "image": "composite-powder.jpg"}
}

# Dropdown to select data
selected_option = st.selectbox(
    "Select Data",
    list(file_map.keys()),
    index=0,  # Default to "Process"
    key="data_select"
)

# Load and display data
file_path = file_map[selected_option]["yaml"]
image_path = file_map[selected_option]["image"]
data, units = load_yaml_with_units(file_path)

# Create two columns for inline display
col1, col2 = st.columns([3, 2])

# Display data in the first column
with col1:
    st.subheader(selected_option)
    formatted_data = format_data(data, units)
    if formatted_data:
        current_level = 0
        section_content = []
        for level, key, value in formatted_data:
            if level == 0 and section_content:
                # Display previous section
                st.markdown(f'<div class="data-section">{"<br>".join(section_content)}</div>', unsafe_allow_html=True)
                section_content = []
            if level == 0:
                section_content.append(f"{key}")
            else:
                indent = "&nbsp;" * (level * 4)
                section_content.append(f"{indent}- {key}: {value}")
        # Display last section
        if section_content:
            st.markdown(f'<div class="data-section">{"<br>".join(section_content)}</div>', unsafe_allow_html=True)
    else:
        st.write("No data available.")

# Display image in the second column
with col2:
    if os.path.exists(image_path):
        st.image(image_path, caption=f"{selected_option} Visualization", use_column_width=True)
    else:
        st.write(f"Image not found: {image_path}")
