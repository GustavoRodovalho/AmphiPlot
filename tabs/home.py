import streamlit as st

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

        The four most common groups are:

        - Fe–Mg–Mn amphiboles
        - Calcic amphiboles
        - Sodic-calcic amphiboles
        - Sodic amphiboles

        ## Main Features

        AmphiPlot provides:

        - Structural formula calculations
        - Cation normalization
        - Site allocation
        - Amphibole classification
        - Geochemical diagrams
        - Export of processed results

        ## Reference

        Hawthorne, F. C., Oberti, R., Harlow, G. E., Maresch, W. V.,
        Martin, R. F., Schumacher, J. C., & Welch, M. D. (2012).

        *Nomenclature of the amphibole supergroup.*

        Mineralogical Society of America.
        DOI: https://doi.org/10.2138/am.2012.4276
        """)