import streamlit as st

from utils.file_loader import load_file, define_structure
from calculations.amphibole import AmphiboleCalculator
# from utils.oxide_mapper import 


class DataTab:

    def show(self):

        st.header("Data Upload and Calculations")

        uploaded_file = st.file_uploader(
            "Upload a CSV or Excel file",
            type=["csv", "xlsx"]
        )

        if uploaded_file is None:
            return

        # Load file
        df = load_file(uploaded_file)

        if df is None:
            return

        st.success("File loaded successfully.")

        standardized_df = define_structure(df)

        # Run calculations
        st.subheader("🧮 Calculations")

        if st.button(
            "Run Calculations",
            type="primary"
        ):

            with st.spinner(
                "Calculating amphibole formulae..."
            ):

                calculator = AmphiboleCalculator(
                    standardized_df
                )

                results = (
                    calculator
                    .calculate_formula()
                )

                st.session_state["results"] = results

            st.success(
                "Calculation finished."
            )

            st.subheader(
                "Results Preview"
            )

            st.dataframe(
                results,
                use_container_width=True
            )