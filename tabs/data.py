import io
import hashlib
import pandas as pd
import streamlit as st

from utils.file_loader import load_file, define_structure
from calculations.amphibole import AmphiboleCalculator

class DataTab:

    @staticmethod
    def create_excel(scenarios):
        """Export all scenarios to an Excel workbook."""

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for name, df in scenarios.items():
                df.to_excel(
                    writer,
                    sheet_name=name,
                    index=True
                )

        return output.getvalue()

    @staticmethod
    def create_csv(df):
        """Export one scenario to CSV."""
        return df.to_csv(index=True).encode("utf-8-sig")

    def show(self):

        st.header("Data Upload and Calculations")

        uploaded_file = st.file_uploader(
            "Upload a CSV or Excel file",
            type=["csv", "xlsx"]
        )

        if uploaded_file is None:
            st.session_state.pop("amphibole_results", None)
            st.session_state.pop("amphibole_file_id", None)
            return

        # Detect file changes
        file_bytes = uploaded_file.getvalue()
        file_id = hashlib.sha256(file_bytes).hexdigest()

        if st.session_state.get("amphibole_file_id") != file_id:
            st.session_state["amphibole_file_id"] = file_id
            st.session_state.pop("amphibole_results", None)

        # Load file
        df = load_file(uploaded_file)

        if df is None:
            return

        st.success("File loaded successfully.")

        standardized_df = define_structure(df)

        # Run calculations
        st.subheader("🧮 Calculations")

        if st.button("Run Calculations", type="primary"):

            try:
                with st.spinner("Initializing parameters..."):
                    calculator = AmphiboleCalculator(
                        standardized_df
                    )

                with st.spinner("Converting to moles..."):
                    elem_mols, oxy_mols = calculator.convert_to_moles()

                with st.spinner("Calculating amphibole formulae..."):
                    scenarios = calculator.scenario_analysis(
                        elem_mols, oxy_mols
                    )

                # Classify amphiboles for each scenario
                with st.spinner("Classifying amphiboles..."):
                    scenarios = calculator.classify(scenarios)

                # Store classified results
                st.session_state["amphibole_results"] = scenarios

                st.success(
                    "Calculations and classifications "
                    "completed successfully."
                )

            except Exception as e:
                st.session_state.pop("amphibole_results", None)
                st.error(f"Calculation failed: {e}")
                return

        # Display results
        scenarios = st.session_state.get("amphibole_results")

        if scenarios is None:
            return

        st.subheader("Amphibole Structural Formulae")

        scenario_names = {
            "scenario_1": "All Fe²⁺",
            "scenario_2_min": "Minimum Fe³⁺",
            "scenario_2_max": "Maximum Fe³⁺",
            "scenario_2_mean": "Mean Fe³⁺"
        }

        tabs = st.tabs([
            scenario_names.get(name, name)
            for name in scenarios
        ])

        for (name, result_df), tab in zip(scenarios.items(), tabs):

            with tab:

                st.caption(
                    f"{len(result_df)} samples | "
                    f"{len(result_df.columns)} variables"
                )

                # ----------------------------------------
                # Complete structural formula
                # ----------------------------------------

                st.markdown("#### Structural Formula and Classification")

                st.dataframe(
                    result_df,
                    use_container_width=True
                )

                # ----------------------------------------
                # Export scenario
                # ----------------------------------------

                st.download_button(
                    label="Download CSV",
                    data=self.create_csv(result_df),
                    file_name=f"{name}.csv",
                    mime="text/csv",
                    key=f"download_{name}"
                )

        # Export all scenarios to Excel
        st.download_button(
            label="Download All Scenarios (Excel)",
            data=self.create_excel(scenarios),
            file_name="amphibole_formulae.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            type="primary"
        )