import streamlit as st
import matplotlib.pyplot as plt

class PlotsTab:

    def show(self):

        st.header("Plots")

        if "results" not in st.session_state:

            st.warning(
                "Run calculations first."
            )

            return

        results = st.session_state["results"]

        plot_type = st.selectbox(
            "Select diagram",
            [
                "Si vs Mg",
                "Custom Scatter Plot"
            ]
        )

        if plot_type == "Si vs Mg":

            fig, ax = plt.subplots()

            ax.scatter(
                results["Si"],
                results["Mg"]
            )

            ax.set_xlabel("Si")
            ax.set_ylabel("Mg")

            st.pyplot(fig)

        elif plot_type == "Custom Scatter Plot":

            x = st.selectbox(
                "X axis",
                results.columns
            )

            y = st.selectbox(
                "Y axis",
                results.columns
            )

            fig, ax = plt.subplots()

            ax.scatter(
                results[x],
                results[y]
            )

            ax.set_xlabel(x)
            ax.set_ylabel(y)

            st.pyplot(fig)