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

def select_oxide_location(df):

    st.subheader("1. Data Preview")

    st.dataframe(df, use_container_width=True)

    st.subheader("2. Select elements")

    min_row = st.number_input(
        "First row of the analyses",
        min_value=0,
        value=0
    )

    min_col = st.number_input(
        "First column of the analyses",
        min_value=0,
        value=0
    )

    nrows, ncols = df.shape

    col1, col2 = st.columns(2)

    with col1:

        row_start = st.number_input(
            "Start row",
            min_value=min_row,
            max_value=nrows - 1,
            value=0
        )

        row_end = st.number_input(
            "End row",
            min_value=row_start,
            max_value=nrows - 1,
            value=nrows - 1
        )

    with col2:

        col_start = st.number_input(
            "Start column",
            min_value=min_col,
            max_value=ncols - 1,
            value=0
        )

        col_end = st.number_input(
            "End column",
            min_value=col_start,
            max_value=ncols - 1,
            value=ncols - 1
        )

    sliced = df.iloc[
        row_start:row_end + 1,
        col_start:col_end + 1
    ]

    st.subheader("3. Selected block")

    st.dataframe(sliced, use_container_width=True)

    return {
        "row_start": row_start,
        "row_end": row_end,
        "col_start": col_start,
        "col_end": col_end
    }

