import streamlit as st
from utils.file_loader import EXPECTED_OXIDES
import pandas as pd

class HomeTab:

    def show(self):

        st.header("Welcome to AmphiPlot")

        st.markdown("""
        **AmphiPlot** is an open-source application designed to calculate,
        classify, and visualize amphibole compositions obtained from
        **Electron Probe Micro-Analyzer (EPMA)** data.

        Amphiboles are among the most important rock-forming minerals and exhibit
        a complex crystal chemistry that allows extensive cation substitutions.
        """)

        st.latex(
            r"A_{0-1}B_2C_5T_8O_{22}W_2"
        )

        st.markdown("""
        where:

        - **A site:** Na, K, Ca, Pb, Li
        - **B site:** Na, Ca, Mn²⁺, Fe²⁺, Mg, Li
        - **C site:** Mg, Fe²⁺, Mn²⁺, Al, Fe³⁺, Mn³⁺, Ti⁴⁺, Li
        - **T site:** Si, Al, Ti⁴⁺
        - **W site:** OH, F, Cl, O²⁻

        ## Amphibole Classification

        According to Hawthorne et al. (2012),
        the current amphibole nomenclature recognizes
        eight major amphibole groups based on site occupancy and composition.

        The five most common groups are:

        - Mg-Fe-Mn-Li amphiboles
        - Na-Ca-Mg-Fe-Mn-Li amphiboles
        - Calcic amphiboles
        - Sodic-calcic amphiboles
        - Sodic amphiboles
        """)

        st.subheader("Classification Flowchart")

        st.markdown("""
        The following flowchart summarizes the classification rules
        implemented in AmphiPlot. The classification is based on the
        occupancy of the **B crystallographic site**, expressed in
        atoms per formula unit (apfu).
        """)

        flowchart = """
        digraph AmphiboleClassification {

            graph [
                rankdir=TB,
                bgcolor="transparent",
                nodesep=0.4,
                ranksep=0.55
            ];

            node [
                shape=box,
                style="rounded,filled",
                fillcolor="#EAF2F8",
                color="#7F8C8D",
                fontname="Arial",
                fontsize=11
            ];

            edge [
                fontname="Arial",
                fontsize=10
            ];

            start [label="B-site cation occupancies"];

            l_high [
                label="L ≥ 1.5?",
                shape=diamond,
                fillcolor="#FFF2CC"
            ];

            l_low [
                label="L ≤ 0.5?",
                shape=diamond,
                fillcolor="#FFF2CC"
            ];

            ca_na_high [
                label="(Ca + Na) ≥ 1.0?",
                shape=diamond,
                fillcolor="#FFF2CC"
            ];

            na_low [
                label="Na < 0.5?",
                shape=diamond,
                fillcolor="#FFF2CC"
            ];

            na_mid [
                label="Na < 1.5?",
                shape=diamond,
                fillcolor="#FFF2CC"
            ];

            mixed [
                label="0.5 < L < 1.5\\nAND\\n0.5 ≤ (Ca + Na) ≤ 1.5?",
                shape=diamond,
                fillcolor="#FFF2CC"
            ];

            mg_group [
                label="Mg-Fe-Mn-Li",
                fillcolor="#D5F5E3"
            ];

            calcic [
                label="Calcic",
                fillcolor="#D5F5E3"
            ];

            sodic_calcic [
                label="Sodic-calcic",
                fillcolor="#D5F5E3"
            ];

            sodic [
                label="Sodic",
                fillcolor="#D5F5E3"
            ];

            mixed_group [
                label="Na-Ca-Mg-Fe-Mn-Li",
                fillcolor="#D5F5E3"
            ];

            unclassified [
                label="Unclassified",
                fillcolor="#FADBD8"
            ];

            start -> l_high;

            l_high -> mg_group [label="Yes"];
            l_high -> l_low [label="No"];

            l_low -> ca_na_high [label="Yes"];
            l_low -> mixed [label="No"];

            ca_na_high -> na_low [label="Yes"];
            ca_na_high -> unclassified [label="No"];

            na_low -> calcic [label="Yes"];
            na_low -> na_mid [label="No"];

            na_mid -> sodic_calcic [label="Yes"];
            na_mid -> sodic [label="No"];

            mixed -> mixed_group [label="Yes"];
            mixed -> unclassified [label="No"];
        }
        """

        # Center the flowchart and reduce its width
        left, center, right = st.columns([1, 2, 1])

        with center:
            st.graphviz_chart(
                flowchart,
                width='stretch',
            )

        st.markdown(r"""
        **Classification parameters**

        - $L_B = Li_B + Mn^{2+}_B + Fe^{2+}_B + Co_B + Ni_B + Zn_B + Mg_B$
        - $(Ca+Na)_B = Ca_B + Na_B$
        - $Na_B$ = sodium occupancy in the B site

        The decision sequence follows the classification conditions
        implemented in `AmphiboleCalculator.classify()`.

        Samples that do not satisfy any of the five group definitions
        are assigned to the **Unclassified** category.
        """)

        # ============================================================
        # INPUT DATA FORMAT
        # ============================================================

        st.header("Input Data Format")

        st.markdown("""
        AmphiPlot accepts geochemical data obtained from
        **Electron Probe Micro-Analyzer (EPMA)** analyses.

        The uploaded CSV or Excel file should follow these conventions:

        - **Rows/columns:** Individual amphibole analyses (samples) and oxide or element concentrations.
        - **Units:** Weight percent (wt.%).
        - **Oxides/element names:** Use the exact oxide/element names listed below.
        - **Missing measurements:** Leave cells empty if an oxide was not measured.

        Fluorine (**F**) and chlorine (**Cl**) should be reported
        as elemental weight percentages rather than oxides.

        The expected oxide/element column names are:
        """)

        # Display expected columns
        st.code(
            ", ".join(EXPECTED_OXIDES),
            language=None
        )

        # ============================================================
        # EXAMPLE CSV TABLE
        # ============================================================

        st.subheader("Example Input Table")

        # Example data structure
        example_df = pd.DataFrame(
            0.0,
            index=["Sample_1", "Sample_2", "Sample_3"],
            columns=EXPECTED_OXIDES
        )

        example_df.index.name = "Sample"

        st.dataframe(
            example_df,
            width="stretch"
        )

        st.caption(
            "Illustrative template showing the expected column names. "
            "Zero values are placeholders, not actual EPMA measurements."
        )

        # ============================================================
        # DOWNLOAD CSV TEMPLATE
        # ============================================================

        st.download_button(
            label="Download CSV Template",
            data=example_df.to_csv().encode("utf-8"),
            file_name="amphiplot_template.csv",
            mime="text/csv"
        )

        # ============================================================
        # MAIN FEATURES AND REFERENCE
        # ============================================================

        st.markdown("""
        ## Main Features

        AmphiPlot provides:

        - Structural formula calculations
        - Cation normalization
        - Site allocation
        - Amphibole classification
        - Simple geochemical diagrams
        - Export of processed results

        ## Reference

        Hawthorne, F. C., Oberti, R., Harlow, G. E., Maresch, W. V.,
        Martin, R. F., Schumacher, J. C., & Welch, M. D. (2012).

        *Nomenclature of the amphibole supergroup.*

        Mineralogical Society of America.
        DOI: https://doi.org/10.2138/am.2012.4276
        """)