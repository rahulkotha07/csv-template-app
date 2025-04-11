import streamlit as st
import pandas as pd
import os
import tempfile
import json
import io
import zipfile

st.title("📄 Generate JSON Files from Template and CSV")

# Upload section
csv_file = st.file_uploader("Upload CSV File", type=["csv"])
json_template_file = st.file_uploader("Upload JSON Template File (.json)", type=["json"])

# Delimiter selection
delimiter = st.selectbox(
    "Select CSV Delimiter",
    options=[", (Comma)", "; (Semicolon)"],
    index=0
)

# Map selection to actual delimiter
delimiter_map = {
    ", (Comma)": ",",
    "; (Semicolon)": ";"
}
selected_delimiter = delimiter_map[delimiter]

if csv_file and json_template_file:
    try:
        # Read file content
        csv_bytes = csv_file.read()
        csv_text = csv_bytes.decode("utf-8")

        # Read CSV with selected delimiter
        df = pd.read_csv(io.StringIO(csv_text), delimiter=selected_delimiter)

        # Read template as raw string
        template_str = json_template_file.read().decode("utf-8")

        with tempfile.TemporaryDirectory() as output_dir:
            st.write("🔄 Generating JSON files...")

            json_file_paths = []

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

                # File name from 'FileName' column
                filename = f"{row['FileName']}.json"
                file_path = os.path.join(output_dir, filename)

                # Save compact JSON
                with open(file_path, 'w') as f:
                    json.dump(output_dict, f, indent=2)

                json_file_paths.append(file_path)

                # Individual download button
                with open(file_path, 'rb') as f:
                    st.download_button(
                        label=f"Download {filename}",
                        data=f,
                        file_name=filename,
                        mime="application/json"
                    )

            # Create zip file of all JSONs
            zip_path = os.path.join(output_dir, "json_files.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in json_file_paths:
                    zipf.write(file_path, os.path.basename(file_path))

            # Download button for zip
            with open(zip_path, 'rb') as zip_file:
                st.download_button(
                    label="📦 Download All as ZIP",
                    data=zip_file,
                    file_name="json_files.zip",
                    mime="application/zip"
                )

            st.success(f"✅ Generated {len(json_file_paths)} JSON files successfully!")

    except Exception as e:
        st.error(f"Something went wrong: {e}")

st.markdown(
    """
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <div style="text-align: center; color: gray;">
        Developed by <strong>Rahul Kotha</strong>
    </div>
    """,
    unsafe_allow_html=True
)
