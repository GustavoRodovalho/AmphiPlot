import io

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


class PlotsTab:

    SCENARIO_NAMES = {
        "scenario_1": "All Fe²⁺",
        "scenario_2_min": "Minimum Fe³⁺",
        "scenario_2_max": "Maximum Fe³⁺",
        "scenario_2_mean": "Mean Fe³⁺",
    }

    DIAGRAMS = {
        "Si vs Mg/(Mg + Fe²⁺)": {
            "denominator": "Fe2+",
            "ylabel": "Mg/(Mg + Fe²⁺)",
        },
        "Si vs Mg/(Mg + Mn²⁺)": {
            "denominator": "Mn2+",
            "ylabel": "Mg/(Mg + Mn²⁺)",
        },
    }

    CLASSIFICATION_COLORS = {
        "Mg-Fe-Mn-Li": "tab:purple",
        "Ca": "tab:blue",
        "Na-Ca": "tab:green",
        "Na": "tab:orange",
        "Na-Ca-Mg-Fe-Mn-Li": "tab:red",
        "Unclassified": "gray",
    }

    @staticmethod
    def get_site_element(df, site, element):
        """Retrieve an element from a MultiIndex column."""

        col = (site, element)

        if col not in df.columns:
            return pd.Series(
                0.0, index=df.index, dtype=float
            )

        return pd.to_numeric(
            df[col], errors="coerce"
        )

    @staticmethod
    def calculate_ratio(df, denominator_element):
        """Calculate Mg/(Mg + X) using B and C sites."""

        mg = (
            PlotsTab.get_site_element(df, "B", "Mg")
            + PlotsTab.get_site_element(df, "C", "Mg")
        )

        other = (
            PlotsTab.get_site_element(
                df, "B", denominator_element
            )
            + PlotsTab.get_site_element(
                df, "C", denominator_element
            )
        )

        denominator = (mg + other).replace(0, np.nan)

        return mg / denominator

    @staticmethod
    def get_silicon(df):
        """Get Si occupancy from the tetrahedral site."""

        col = ("T", "Si")

        if col not in df.columns:
            raise KeyError(
                "Missing structural formula column: ('T', 'Si')"
            )

        return pd.to_numeric(
            df[col], errors="coerce"
        )

    @staticmethod
    def draw_classification_grid(ax):
        """Draw the seven user-defined Si–Mg# fields."""
        line_style = dict(color="0.45", linewidth=1.0, zorder=1)

        # Vertical boundaries and Mg# = 0.5 across all fields
        ax.plot([6.5, 6.5], [0, 1], **line_style)
        ax.plot([7.5, 7.5], [0, 1], **line_style)
        ax.plot([5.5, 8.1], [0.5, 0.5], **line_style)

        # Mg# = 0.9 only in the Si > 7.5 fields
        ax.plot([7.5, 8.1], [0.9, 0.9], **line_style)

        fields = [
            ("Tremolite", 7.8, 0.95),
            ("Actinolite", 7.8, 0.70),
            ("Fe-Actinolite", 7.8, 0.25),
            ("Mg-Hornblende", 7.0, 0.75),
            ("Fe-Hornblende", 7.0, 0.25),
            ("Tschermakite", 6.0, 0.75),
            ("Fe-Tschermakite", 6.0, 0.25),
        ]

        for name, x, y in fields:
            ax.text(
                x, y, name,
                ha="center", va="center",
                fontsize=8, color="0.25",
                bbox=dict(facecolor="white", alpha=0.65,
                          edgecolor="none", pad=1.5),
                zorder=2,
            )

    @staticmethod
    def create_scatter(
        df,
        x,
        y,
        xlabel,
        ylabel,
        title,
        show_labels=False,
        show_formula=False,
        show_legend=False,
        show_classification_grid=False,
        aspect_ratio=1.3
    ):
        """Create a scatter plot colored by amphibole classification."""

        fig_height = 7
        fig_width = fig_height * aspect_ratio

        fig, ax = plt.subplots(
            figsize=(fig_width, fig_height)
        )

        x_values = pd.to_numeric(x, errors="coerce")
        y_values = pd.to_numeric(y, errors="coerce")

        groups = (
            df[("Classification", "Group")]
            .replace("", "Unclassified")
            .fillna("Unclassified")
        )

        valid = x_values.notna() & y_values.notna()

        if show_classification_grid:
            PlotsTab.draw_classification_grid(ax)

        for group in groups[valid].unique():

            mask = valid & (groups == group)

            ax.scatter(
                x_values[mask],
                y_values[mask],
                label=group,
                color=PlotsTab.CLASSIFICATION_COLORS.get(
                    group, "gray"
                ),
                s=55,
                alpha=0.85,
                edgecolors="black",
                linewidths=0.5,
                zorder=3,
            )

        # ----------------------------------------
        # Sample annotations
        # ----------------------------------------

        formula_col = ("Classification", "Formula")

        if show_labels or show_formula:

            for i in np.flatnonzero(valid.to_numpy()):

                annotations = []

                # Sample identifier
                if show_labels:
                    annotations.append(str(df.index[i]))

                # Structural formula
                if show_formula and formula_col in df.columns:

                    formula = df[formula_col].iloc[i]

                    if pd.notna(formula):
                        annotations.append(
                            PlotsTab.formula_to_mathtext(formula)
                        )

                if not annotations:
                    continue

                label = "\n".join(annotations)

                ax.annotate(
                    label,
                    (
                        x_values.iloc[i],
                        y_values.iloc[i],
                    ),
                    xytext=(5, 5),
                    textcoords="offset points",
                    fontsize=7 if show_formula else 8,
                    ha="left",
                    va="bottom",
                    annotation_clip=False,
                    zorder=4,
                )

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        # Add padding so points never touch the axes.
        valid_x = x_values[valid].to_numpy(dtype=float)
        valid_y = y_values[valid].to_numpy(dtype=float)
        if valid_x.size and valid_y.size:
            xmin, xmax = valid_x.min(), valid_x.max()
            ymin, ymax = valid_y.min(), valid_y.max()
            xpad = max((xmax - xmin) * 0.05, 0.10)
            ypad = max((ymax - ymin) * 0.06, 0.05)
            if show_classification_grid:
                # Preserve the full classification grid and any outlying data.
                ax.set_xlim(max(8.1, xmax + xpad), min(5.5, xmin - xpad))
                ax.set_ylim(min(0.0, ymin - ypad), max(1.0, ymax + ypad))
            else:
                # Reverse the Si axis for both diagrams.
                ax.set_xlim(xmax + xpad, xmin - xpad)
                ax.set_ylim(ymin - ypad, ymax + ypad)

        ax.grid(alpha=0.2)

        if ax.get_legend_handles_labels()[0]:
            if show_legend:
                ax.legend(
                    title="Amphibole Group",
                    loc="upper left",
                    bbox_to_anchor=(1.02, 1.0),
                    borderaxespad=0,
                    fontsize=9,
                )

                # Reserve space for the legend outside the axes
                fig.subplots_adjust(
                    left=0.12,
                    right=0.67,
                    bottom=0.12,
                    top=0.92,
                )

            else:
                # Use more space when the legend is hidden
                fig.subplots_adjust(
                    left=0.12,
                    right=0.95,
                    bottom=0.12,
                    top=0.92,
                )

        return fig

    @staticmethod
    def figure_to_bytes(fig, fmt="png"):
        """Convert a Matplotlib figure to bytes."""

        buffer = io.BytesIO()

        fig.savefig(
            buffer,
            format=fmt,
            dpi=300,
            bbox_inches="tight",
        )

        buffer.seek(0)

        return buffer.getvalue()

    @staticmethod
    def formula_to_mathtext(formula):
        """Convert a plain-text amphibole formula into Matplotlib MathText."""

        import re

        # Match crystallographic sites
        site_pattern = r"(OH|A|B|C|T)\(([^()]*)\)"

        # Match elements, oxidation states and occupancies
        element_pattern = (
            r"([A-Z][a-z]?|OH)"
            r"(\d+\+)?"
            r"(\d+(?:\.\d+)?)"
        )

        def format_site(match):

            site = match.group(1)
            contents = match.group(2)

            formatted_elements = []

            for element, oxidation, occupancy in re.findall(
                element_pattern, contents
            ):

                # Format oxidation state as superscript
                if oxidation:
                    element = (
                        f"{element}^{{{oxidation}}}"
                    )

                # Format occupancy as subscript
                formatted_elements.append(
                    f"{element}_{{{occupancy}}}"
                )

            formatted_site = "".join(formatted_elements)

            return (
                f"^{{\\mathrm{{{site}}}}}"
                f"\\left({formatted_site}\\right)"
            )

        parts = []

        for match in re.finditer(site_pattern, str(formula)):
            parts.append(format_site(match))

        if not parts:
            return str(formula)

        return "$" + r"\,".join(parts) + "$"

    def show(self):

        st.header("Amphibole Plots")

        scenarios = st.session_state.get(
            "amphibole_results"
        )

        if not scenarios:
            st.warning(
                "Run the amphibole calculations "
                "in the Data tab first."
            )
            return

        st.subheader("Plot Settings")

        # ----------------------------------------
        # Scenario selection
        # ----------------------------------------

        scenario = st.selectbox(
            "Fe estimation scenario",
            options=list(scenarios.keys()),
            format_func=lambda name:
                self.SCENARIO_NAMES.get(name, name),
        )

        results = scenarios[scenario].copy()

        # ----------------------------------------
        # Sample selection
        # ----------------------------------------

        sample_ids = list(
            dict.fromkeys(results.index.tolist())
        )

        selected_samples = st.multiselect(
            "Select samples",
            options=sample_ids,
            default=sample_ids,
        )

        if not selected_samples:
            st.info("Select at least one sample.")
            return

        results = results.loc[
            results.index.isin(selected_samples)
        ].copy()

        st.caption(
            f"{len(results)} analyses selected"
        )

        # ----------------------------------------
        # Diagram selection
        # ----------------------------------------

        diagram = st.selectbox(
            "Select diagram",
            options=list(self.DIAGRAMS.keys()),
        )

        diagram_config = self.DIAGRAMS[diagram]

        show_classification_grid = False
        if diagram == "Si vs Mg/(Mg + Fe²⁺)":
            show_classification_grid = st.checkbox(
                "Show calcic amphibole classification",
                value=False,
            )

        show_labels = st.checkbox(
            "Show sample labels",
            value=False,
        )

        show_formula = st.checkbox(
            "Show sample formula",
            value=False,
        )

        show_legend = st.checkbox(
            "Show legend",
            value=False,
        )

        aspect_ratio = st.slider(
            "Plot width/height ratio",
            min_value=1.0,
            max_value=3.0,
            value=1.3,
            step=0.1,
        )

        # ----------------------------------------
        # Calculate diagram variables
        # ----------------------------------------

        try:
            si = self.get_silicon(results)

        except KeyError as error:
            st.error(str(error))
            return

        ratio = self.calculate_ratio(
            results,
            diagram_config["denominator"],
        )

        if ratio.notna().sum() == 0:
            st.warning(
                "No valid values were calculated "
                "for the selected diagram."
            )
            return

        # ----------------------------------------
        # Create diagram
        # ----------------------------------------

        fig = self.create_scatter(
            df=results,
            x=si,
            y=ratio,
            xlabel="Si (apfu)",
            ylabel=diagram_config["ylabel"],
            title=diagram,
            show_labels=show_labels,
            show_formula=show_formula,
            show_legend=show_legend,
            show_classification_grid=show_classification_grid,
            aspect_ratio=aspect_ratio
        )

        st.subheader("Diagram")
        st.pyplot(fig)

        # ----------------------------------------
        # Export
        # ----------------------------------------

        col1, col2 = st.columns(2)

        filename = (
            f"{scenario}_"
            f"{diagram.replace(' ', '_').replace('/', '_')}"
        )

        with col1:
            st.download_button(
                "Download PNG",
                data=self.figure_to_bytes(fig, "png"),
                file_name=f"{filename}.png",
                mime="image/png",
                width='stretch',
            )

        with col2:
            st.download_button(
                "Download SVG",
                data=self.figure_to_bytes(fig, "svg"),
                file_name=f"{filename}.svg",
                mime="image/svg+xml",
                width='stretch',
            )

        plt.close(fig)