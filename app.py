import streamlit as st
import pandas as pd
import os
import tempfile
import json

st.title("📄 Generate JSON Files from Template and CSV")

# Upload section
csv_file = st.file_uploader("Upload CSV File", type=["csv"])
json_template_file = st.file_uploader("Upload JSON Template File (.json)", type=["json"])

if csv_file and json_template_file:
    try:
        # Read CSV
        df = pd.read_csv(csv_file)

        # Read template as raw string
        template_str = json_template_file.read().decode("utf-8")

        with tempfile.TemporaryDirectory() as output_dir:
            st.write("🔄 Generating JSON files...")

            for index, row in df.iterrows():
                output_json_str = template_str

                # Replace placeholders
                for col in df.columns:
                    placeholder = f"{{{col}}}"
                    output_json_str = output_json_str.replace(placeholder, str(row[col]))

                # Convert to dictionary to ensure compact JSON output
                try:
                    output_dict = json.loads(output_json_str)
                except json.JSONDecodeError as e:
                    st.error(f"❌ Error parsing JSON for row {index + 1}: {e}")
                    continue

                # File name from first column value
                filename = f"{row['FileName']}.json"
                file_path = os.path.join(output_dir, filename)

                # Save compact JSON
                with open(file_path, 'w') as f:
                    json.dump(output_dict, f, indent=2)

                # Streamlit download button
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label=f"Download {filename}",
                        data=f,
                        file_name=filename,
                        mime="application/json"
                    )

            st.success(f"✅ Generated {len(df)} JSON files successfully!")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
