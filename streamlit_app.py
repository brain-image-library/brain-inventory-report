import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime
import humanize
import matplotlib.pyplot as plt

# App Title
st.title("🧠 Brain Image Library Inventory Report")

# Introduction
st.markdown("""
The **Brain Image Library (BIL)** is a national public resource that supports the storage, sharing, and analysis of large-scale brain imaging datasets. 
This report provides a snapshot of the current dataset inventory, highlighting key metadata including file counts, sizes, and organizational structure.
""")

# Subtitle with today's date
today_str = datetime.today().strftime("%B %d, %Y")
st.markdown(f"### 📅 Report Date: {today_str}")

# Load data
URL = "https://download.brainimagelibrary.org//inventory/daily/reports/today.json"
st.caption(f"Loading data from: {URL}")

try:
    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)

    # Extract collection from bildirectory
    def extract_collection(path):
        match = re.search(r"/bil/data/([a-f0-9]{2})/", path)
        return match.group(1) if match else None

    df["collection"] = df["bildirectory"].apply(extract_collection)

    # Compute pretty_size from size
    df["pretty_size"] = df["size"].apply(lambda s: humanize.naturalsize(s, binary=True) if pd.notnull(s) else None)

    # Sort by number_of_files in descending order
    df_sorted = df.sort_values(by="number_of_files", ascending=False)

    # Select and rename columns for preview
    preview_df = df_sorted[["collection", "bildid", "number_of_files", "pretty_size"]].rename(columns={
        "collection": "Collection",
        "bildid": "Brain ID",
        "number_of_files": "Number of Files",
        "pretty_size": "Size"
    })

    # Display table preview
    st.subheader("Preview: Sorted by Number of Files (Descending)")
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────────
    # 📁 Collections Section
    # ─────────────────────────────────────────────
    st.subheader("📁 Collections")
    unique_collections = sorted(df["collection"].dropna().unique())
    selected_collection = st.selectbox("Select a Collection:", unique_collections)
    st.markdown(f"You selected: **{selected_collection}**")

    # Filtered table for selected collection
    filtered_df = df[df["collection"] == selected_collection][["collection", "bildid", "number_of_files", "pretty_size"]].rename(columns={
        "collection": "Collection",
        "bildid": "Brain ID",
        "number_of_files": "Number of Files",
        "pretty_size": "Size"
    })

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    # Pie Chart of all datasets in selected collection
    st.subheader("📈 File Distribution in Selected Collection")
    pie_data = df[df["collection"] == selected_collection].set_index("bildid")["number_of_files"]
    pie_data = pie_data[pie_data > 0].sort_values(ascending=False)

    fig3, ax3 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax3.pie(
        pie_data,
        labels=None,
        autopct="%1.1f%%",
        startangle=140
    )
    ax3.axis("equal")
    ax3.set_title("Number of Files per Dataset")

    # Legend in columns of 25 entries
    labels = list(pie_data.index)
    num_cols = (len(labels) - 1) // 25 + 1

    ax3.legend(
        wedges,
        labels,
        title="Brain ID",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize="small",
        ncol=num_cols
    )

    st.pyplot(fig3)

except Exception as e:
    st.error(f"Failed to load or process data: {e}")
