aimport streamlit as st
import pandas as pd
import json
import os
import streamlit.components.v1 as components

# Title of the app
st.title("Mechanical Properties Table Viewer")

# Path to the JSON file (assumed to be in the same directory as the script)
json_file_path = "mechanical_properties_of_samples.json"

# Check if the JSON file exists
if os.path.exists(json_file_path):
    # Load JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Flatten nested structure: Extract value ± error without units for table
    formatted_data = []
    labels = []
    ys_values = []
    uts_values = []
    elongation_values = []

    for entry in data:
        # Format label as "Condition (Sample)" to distinguish samples
        label = f"{entry['Condition']} ({entry['Sample']})"
        labels.append(label)
        ys_values.append(entry["Yield Strength"]["value"])
        uts_values.append(entry["Ultimate Tensile Strength"]["value"])
        elongation_values.append(entry["Elongation"]["value"])

        row = {
            "Sample": entry["Sample"],
            "Condition": entry["Condition"],
            "Yield Strength (MPa)": f'{entry["Yield Strength"]["value"]} ± {entry["Yield Strength"]["error"]}',
            "Ultimate Tensile Strength (MPa)": f'{entry["Ultimate Tensile Strength"]["value"]} ± {entry["Ultimate Tensile Strength"]["error"]}',
            "Elongation (%)": f'{entry["Elongation"]["value"]} ± {entry["Elongation"]["error"]}'
        }
        formatted_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(formatted_data)

    # Display formatted table
    st.subheader("Formatted Table (value ± error)")
    st.dataframe(df, use_container_width=True)

    # Optional: Sample filtering
    sample_types = df['Sample'].unique()
    selected_samples = st.multiselect("Filter by Sample", options=sample_types, default=sample_types)

    # Filter DataFrame based on selected samples
    filtered_df = df[df["Sample"].isin(selected_samples)]

    # Filter chart data based on selected samples
    filtered_labels = []
    filtered_ys = []
    filtered_uts = []
    filtered_elongation = []
    for i, entry in enumerate(data):
        if entry["Sample"] in selected_samples:
            filtered_labels.append(labels[i])
            filtered_ys.append(ys_values[i])
            filtered_uts.append(uts_values[i])
            filtered_elongation.append(elongation_values[i])

    # Display filtered table
    st.subheader("Filtered Table")
    st.dataframe(filtered_df, use_container_width=True)

    # Chart.js bar chart
    st.subheader("Mechanical Properties Visualization")
    chart_html = f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <canvas id="myChart"></canvas>
        <script>
            const ctx = document.getElementById('myChart').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(filtered_labels)},
                    datasets: [
                        {{
                            label: 'Yield Strength (MPa)',
                            data: {json.dumps(filtered_ys)},
                            backgroundColor: '#1f77b4',
                            borderColor: '#1f77b4',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Ultimate Tensile Strength (MPa)',
                            data: {json.dumps(filtered_uts)},
                            backgroundColor: '#ff7f0e',
                            borderColor: '#ff7f0e',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Elongation (%)',
                            data: {json.dumps(filtered_elongation)},
                            backgroundColor: '#2ca02c',
                            borderColor: '#2ca02c',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Value'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Condition (Sample)'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true
                        }},
                        title: {{
                            display: true,
                            text: 'Mechanical Properties by Condition'
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(chart_html, height=400)

else:
    st.error(f"JSON file not found at {json_file_path}. Please ensure 'mechanical_properties_of_samples.json' is in the same directory as the script.")
