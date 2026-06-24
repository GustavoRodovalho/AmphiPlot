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

        # Show original file
        st.subheader("Original File")

        standardized_df = define_structure(df)

        # Run calculations
        st.subheader("Calculations")

        st.markdown("""First, we assume there is no Fe_2O_3 content and we must distribute the total content of Fe, indicated in the FeO content. For that, we perform 4 different normalizations for the following scenarios:
        
        - All Fe is Fe$^{2+}$
        - Minimum Fe$^{3+}$ content
        - Maximum Fe$^{3+}$ content
        - Mean Fe$^{3+}$ content
        """
        )

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