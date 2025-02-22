import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO

# Set Page Config First
st.set_page_config(page_title="Data Sweeper", layout='wide')

# Inject Custom CSS for Aesthetic 3D-Themed UI
st.markdown("""
    <style>
        .stButton>button {
            background: linear-gradient(90deg, #ff7eb3, #ff758c);
            color: white;
            border-radius: 12px;
            padding: 12px 20px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0px 4px 10px rgba(255, 118, 136, 0.5);
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0px 6px 14px rgba(255, 118, 136, 0.8);
        }
        .stFileUploader {
            border: 2px dashed #ff758c !important;
            padding: 12px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            text-align: center;
            color: white;
        }
        .success-message {
            color: #ff758c;
            font-size: 20px;
            text-align: center;
            font-weight: bold;
        }

    </style>
    <div class="background"></div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">📂 Data Sweeper - Advanced File Converter</h1>', unsafe_allow_html=True)
st.write("Easily convert CSV, Excel, and JSON files with built-in data cleaning and visualization.")

# File Uploader
upload_files = st.file_uploader("Upload your files (CSV, Excel, JSON):", type=["csv", "xlsx", "json"], accept_multiple_files=True)

# Process Files
if upload_files:
    converted_files = []
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        
        try:
            # Read file based on extension
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file)
            elif file_ext == ".json":
                df = pd.read_json(file)
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")
            continue
        
        # Display file info
        st.subheader(f"📂 File: {file.name}")
        st.write(f"Size: {file.size / 1024:.2f} KB")
        
        # Preview Data
        st.write("📊 Data Preview")
        st.dataframe(df.head())
        
        # Data Cleaning Options
        st.subheader("🛠 Data Cleaning")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Remove Duplicates from {file.name}", key=f"remove_dup_{file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicates Removed!")
        
        with col2:
            missing_value_strategy = st.selectbox(f"Fill Missing Values ({file.name})", ["Mean", "Median", "Mode", "None"], key=f"missing_val_{file.name}")
            if missing_value_strategy != "None":
                num_cols = df.select_dtypes(include=['number']).columns
                if missing_value_strategy == "Mean":
                    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
                elif missing_value_strategy == "Median":
                    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
                elif missing_value_strategy == "Mode" and not df[num_cols].mode().empty:
                    df[num_cols] = df[num_cols].fillna(df[num_cols].mode().iloc[0])
                st.success(f"Missing values filled using {missing_value_strategy} method!")
        
        # Column Selection & Renaming
        st.subheader("📝 Select & Rename Columns")
        selected_columns = st.multiselect(f"Select Columns for {file.name}", df.columns, default=df.columns, key=f"select_col_{file.name}")
        df = df[selected_columns]
        
        rename_cols = {col: st.text_input(f"Rename {col}", col, key=f"rename_{col}_{file.name}") for col in selected_columns}
        df.rename(columns=rename_cols, inplace=True)
        
        # File Conversion
        st.subheader("🔄 File Conversion")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel", "JSON"], key=f"convert_{file.name}")
        buffer = BytesIO()
        
        if st.button(f"Convert {file.name}", key=f"convert_btn_{file.name}"):
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                new_ext = ".csv"
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
                new_ext = ".xlsx"
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif conversion_type == "JSON":
                df.to_json(buffer, orient="records", indent=2)
                new_ext = ".json"
                mime_type = "application/json"
            
            buffer.seek(0)
            st.download_button(label=f"Download {file.name.replace(file_ext, new_ext)}", data=buffer, file_name=file.name.replace(file_ext, new_ext), mime=mime_type)
            st.success(f"{file.name} converted to {conversion_type}!")
