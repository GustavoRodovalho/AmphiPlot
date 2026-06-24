import pandas as pd
import streamlit as st

EXPECTED_OXIDES = [
    "SiO2",
    "TiO2",
    "Al2O3",
    "Fe2O3",
    "FeO",
    "MnO",
    "MgO",
    "CaO",
    "Na2O",
    "Li2O",
    "K2O",
    "BaO",
    "Cs2O",
    "Rb2O",
    "F",
    "Cl",
    "Sc2O3",
    "Cr2O3",
    "V2O3",
    "ZnO",
    "NiO",
    "CoO",
    "ZrO2",
    "SrO",
    "Mn2O3"
]

def load_file(uploaded_file):

    st.subheader("⚙️ Import settings")

    header_row = st.number_input(
        "Header row",
        min_value=0,
        value=0
    )

    index_column = st.number_input(
        "Index column",
        min_value=0,
        value=0
    )

    decimal_sep = st.selectbox(
        "Decimal separator",
        [".", ","]
    )

    if uploaded_file.name.endswith(".csv"):

        separator = st.selectbox(
            "Column separator",
            [";", ",", "\t", "|"]
        )

        return pd.read_csv(
            uploaded_file,
            sep=separator,
            header=header_row,
            index_col=index_column,
            decimal=decimal_sep
        )

    return pd.read_excel(
        uploaded_file,
        header=header_row,
        index_col=index_column,
        decimal=decimal_sep,
        engine="openpyxl"
    )

def define_structure(df):

    st.subheader("📊 Data Structure Definition")

    st.write("Preview of uploaded data:")
    st.dataframe(df, use_container_width=True)

    # -----------------------------------------
    # 1. Oxide location
    # -----------------------------------------

    st.markdown("Oxide location")

    oxide_mode = st.radio(
        "Where are the oxides names?",
        ["Columns (headers)", "Rows (indices)"]
    )

    if oxide_mode == "Columns (headers)":

        oxide_candidates = [
            c for c in df.columns
            if str(c).strip() in EXPECTED_OXIDES
        ]

        selected_oxides = st.multiselect(
            "Detected oxide columns (adjust if needed)",
            df.columns,
            default=oxide_candidates
        )

        oxides_slice = df.loc[:,selected_oxides]

    else:

        oxide_candidates = [
            c for c in df.index
            if str(c).strip() in EXPECTED_OXIDES
        ]

        selected_oxides = st.multiselect(
            "Detected oxide rows (adjust if needed)",
            df.index,
            default=oxide_candidates
        )

        oxides_slice = df.loc[selected_oxides,:]

    # -----------------------------------------
    # 2. Sample location
    # -----------------------------------------

    st.markdown("Sample names")

    sample_mode = st.radio(
        "Where are sample names?",
        ["None", "Columns (headers)", "Rows (indices)"]
    )

    if sample_mode == "Columns (headers)":

        sample_names = [
            c for c in df.columns
        ]

        selected_samples = st.multiselect(
            "Analyzed samples (adjust if needed)",
            df.columns,
            default=sample_names
        )

        samples_slice = oxides_slice.loc[:,selected_samples]

    elif sample_mode == "Rows (indices)":

        sample_names = [
            c for c in df.index
        ]

        selected_samples = st.multiselect(
            "Analyzed samples (adjust if needed)",
            df.index,
            default=sample_names
        )

        samples_slice = oxides_slice.loc[selected_samples,:]

    else:

        samples_slice = oxides_slice

    # -----------------------------------------
    # 3. Return configuration with oxides as columns and samples as indices
    # -----------------------------------------

    st.markdown("Structured dataset:")

    if oxide_mode == "Columns (headers)":
        st.dataframe(samples_slice, use_container_width=True)
        return samples_slice
    
    else:
        st.dataframe(samples_slice.T, use_container_width=True)
        return samples_slice.T
