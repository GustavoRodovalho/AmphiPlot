import numpy as np
import pandas as pd
from calculations.parameters import oxide_info

class AmphiboleCalculator:

    def __init__(self, dataframe):

        self.df = dataframe.copy()
        if not self.df.columns.is_unique:
            raise ValueError("Duplicate oxide column names are not allowed.")
        self.oxides = self.df.columns.tolist()

        # Validate oxide names and reorder metadata dataframe rows to match input DataFrame
        unknown_oxides = self.df.columns.difference(oxide_info.index)

        if not unknown_oxides.empty:
            raise ValueError(
                f"Unknown oxide compositions: {unknown_oxides.tolist()}"
            )

        # Reproduce the notebook's complete oxide set, independently of input order.
        # Missing compositions are treated as zero, just as the notebook treats NaN.
        self.df = self.df.apply(pd.to_numeric, errors="raise").fillna(0.0)
        self.df = self.df.reindex(columns=oxide_info.index, fill_value=0.0)
        self.oxides = self.df.columns.tolist()
        self.oxide_info = oxide_info.loc[self.oxides].copy()

        # Extract parameters
        self.weights = self.oxide_info["weight"]
        self.n_cations = self.oxide_info["n_cations"]
        self.n_anions = self.oxide_info["n_anions"]
        self.cations_names = self.oxide_info["cations_names"].tolist()
        self.anions_names = self.oxide_info["anions_names"].tolist()

    def convert_to_moles(self):

        # 1. Convert wt.% into oxide moles
        samples_df = self.df.copy()

        ox_mols = samples_df.div(self.weights, axis=1)

        # Calculate total iron expressed as FeO
        ox_mols["FeOT"] = (
            samples_df["FeO"] + 0.8998 * samples_df["Fe2O3"]
        ) / self.weights["FeO"]

        # 2. Calculate cation moles
        n_cations = pd.concat([
            self.n_cations,
            pd.Series({"FeOT": 1})
        ])

        elem_mols = ox_mols.mul(n_cations, axis=1)
        elem_mols.columns = self.cations_names + ["Fe: FeOT"]

        # 3. Calculate anion moles
        n_anions = pd.concat([
            self.n_anions,
            pd.Series({"FeOT": 1})
        ])

        oxy_mols = ox_mols.mul(n_anions, axis=1)
        oxy_mols.columns = self.anions_names + ["O: FeOT"]

        return elem_mols, oxy_mols

    def distribute_moles(self, scenario, sites_order, amphi_elems, correction_anions):
        # Get the maximum number of elements in each site
        site_capacities = {"OH": 2, "T": 8, "C": 5, "B": 2, "A": 1}

        # Create a pool from which elements will be drawn to fill the sites
        available = amphi_elems.copy()

        # Create a dictionary containing the translation between the name of the current element being distributed and its name in the amphi_elems dataframe
        # Preserve the notebook's Mn mapping for numerical equivalence.
        # Its "MnO" key does not match the converted column labels, so Mn is
        # not distributed; correcting this would change notebook results.
        elem_cols = {"OH": "OH", "Cl": "Cl: Cl", "F": "F: F", "Si": "Si: SiO2", "Al": "Al: Al2O3", "Ti": "Ti: TiO2", "Fe3+": "FeIII: Fe2O3", "V": "V: V2O3", "Sc": "Sc: Sc2O3", "Cr": "Cr: Cr2O3", "Mn3+": "MnO", "Zr": "Zr: ZrO2", "Mg": "Mg: MgO", "Zn": "Zn: ZnO", "Ni": "Ni: NiO", "Co": "Co: CoO", "Fe2+": "FeII: FeO", "Mn2+": "MnO", "Li": "Li: Li2O", "Ca": "Ca: CaO", "Sr": "Sr: SrO", "Ba": "Ba: BaO", "Na": "Na: Na2O", "K": "K: K2O", "Rb": "Rb: Rb2O", "Cs": "Cs: Cs2O"}

        for site, site_elements in sites_order.items():

            remaining = pd.Series(
                site_capacities[site],
                index=amphi_elems.index,
                dtype=float
            )

            # Follow the order in site_elements
            for elem in site_elements:

                # OH is the last to be verified in the OH sites
                if elem == "OH":
                    continue

                if elem not in elem_cols:
                    print(f"{elem} not in elem_cols")
                    continue

                col = elem_cols[elem]

                if col not in available.columns:
                    continue

                # Fe3 is considered only in some scenarios
                if elem == "Fe3+":
                    norm_factor = correction_anions.sum(axis=1)
                    allocation = (23 - correction_anions.sum(axis=1))*2
                    scenario[(site, elem)] = allocation
                    remaining -= allocation

                else:
                    allocation = np.minimum(available[col], remaining)
                    scenario[(site, elem)] = allocation
                    available[col] -= allocation
                    remaining -= allocation

            # Fill OH site with residual occupancy
            if site == "OH":
                scenario[("OH", "OH")] = remaining

        return scenario

    def scenario_analysis(self, elem_mols, oxy_mols):
        """
        To calculate the amphibole formula, we need to consider different scenarios for the distribution of cations in the crystal structure ("OH": 2, "T": 8, "C": 5, "B": 2, "A": 1). Each scenario will have a specific order of site occupancy and will be evaluated based on the available cation moles and the anion correction.

        All the scenarios considers an initial normalization step to distribute the available moles for an amphibole structure with 23 elements (indicated by the amphi_elems variable). Then, each scenario is calculated by adjusting the order of distribution with Fe3+ in the C site. The scenarios are as follows:
        
        1. All Fe is Fe2+ (normalization A)
        2. Fe3+ is present in the C site
            2.1. Minimum Fe3+ in C site (normalization A + normalization B)
            2.2. Maximum Fe3+ in C site (normalization A + normalization C)
            2.3. Mean Fe3+ in C site (normalization A + normalization D)
        
        """

        def normalization_without_fe3(elem_mols, oxy_mols):
            """Calculate the normalized values for no Fe3+ (normalization A)"""
            # The O in Cl and F (anions, just like the O) must be corrected
            # For that, we will multiply their mols for -0.5 and subtract when summing the total moles of oxygen
            correction_anions = oxy_mols.drop(columns="O: FeOT").copy()
            correction_anions["O: F"] = elem_mols["F: F"]*-0.5
            correction_anions["O: Cl"] = elem_mols["Cl: Cl"]*-0.5

            # Calculate the normalization factor of each sample
            norm_ox = correction_anions.sum(axis=1)
            norm_factor = 23 / norm_ox

            # Multiply every element by the normalization factor based on an amphibole structure with 23 oxygens
            amphi_elems = elem_mols.mul(norm_factor, axis=0)
    
            return amphi_elems, correction_anions

        def normalization_with_fe3(amphi_elems):
            """Calculate the normalized values for Fe3+ min (normalization B), Fe3+ max (normalization C) and Fe3+ mean (normalization D)"""
            norm_sums = pd.DataFrame(columns=[
                "ΣSi (≤8)",
                "ΣAl (≥8)",
                "ΣMn (≥13)",
                "ΣCa (≤15)",
                "ΣNa (≥15)",
                "ΣK (≤16)"
            ])

            norm_sums["ΣSi (≤8)"] = amphi_elems["Si: SiO2"]
            norm_sums["ΣAl (≥8)"] = amphi_elems[["Si: SiO2", "Al: Al2O3"]].sum(axis=1)
            norm_sums["ΣMn (≥13)"] = amphi_elems[["Si: SiO2", "Ti: TiO2", "Al: Al2O3", "Fe: FeOT", "Mn: MnO", "Mg: MgO", "Li: Li2O", "Sc: Sc2O3", "Cr: Cr2O3", "V: V2O3", "Zn: ZnO", "Ni: NiO", "Zr: ZrO2", "Mn: Mn2O3"]].sum(axis=1)
            norm_sums["ΣCa (≤15)"] = norm_sums["ΣMn (≥13)"] + amphi_elems["Ca: CaO"]
            norm_sums["ΣNa (≥15)"] = norm_sums["ΣCa (≤15)"] + amphi_elems[["Na: Na2O", "Ba: BaO", "Sr: SrO"]].sum(axis=1)
            norm_sums["ΣK (≤16)"] = norm_sums["ΣNa (≥15)"] + amphi_elems[["K: K2O", "Cs: Cs2O", "Rb: Rb2O"]].sum(axis=1)

            # Calculate the normalization factors for Fe3+ min (normalization B)
            norm_factor_fe_min = pd.DataFrame(columns=[
                "8Si",
                "16CAT",
                "all-ferrous-iron",
                "15eNK"
            ])

            norm_factor_fe_min["8Si"] = np.full(amphi_elems.shape[0], 8.0) / norm_sums['ΣSi (≤8)']
            norm_factor_fe_min["16CAT"] = np.full(amphi_elems.shape[0], 16.0) / norm_sums['ΣK (≤16)']
            norm_factor_fe_min["all-ferrous-iron"] = np.full(amphi_elems.shape[0], 1.0)
            norm_factor_fe_min["15eNK"] = np.full(amphi_elems.shape[0], 15.0) / norm_sums["ΣCa (≤15)"]

            amphi_elems_fe_min = amphi_elems.copy()
            amphi_elems_fe_min = amphi_elems_fe_min.mul(norm_factor_fe_min.min(axis=1), axis=0)

            # Explicitly align each oxygen/cation ratio by oxide identity.
            oxygen_ratios = (
                self.oxide_info["n_anions"]
                / self.oxide_info["n_cations"]
            )
            oxygen_ratios.index = self.oxide_info["cations_names"]

            def oxygen_equivalents(normalized_cations):
                return normalized_cations.drop(columns="Fe: FeOT").mul(
                    oxygen_ratios, axis=1
                )

            oxy_mols_fe_min = oxygen_equivalents(amphi_elems_fe_min)
            correction_anions_fe_min = oxy_mols_fe_min.copy()
            correction_anions_fe_min["O: F"] = amphi_elems_fe_min["F: F"]*-0.5
            correction_anions_fe_min["O: Cl"] = amphi_elems_fe_min["Cl: Cl"]*-0.5

            # Calculate the normalization factors for Fe3+ max (normalization C)
            norm_factor_fe_max = pd.DataFrame(columns=[
                "15eK",
                "13eCNK",
                "all-ferric-iron",
                "10ΣFe3+",
                "8SiAl"
            ])

            norm_factor_fe_max["15eK"] = np.full(amphi_elems.shape[0], 15.0) / norm_sums['ΣNa (≥15)']
            norm_factor_fe_max["13eCNK"] = np.full(amphi_elems.shape[0], 13.0) / norm_sums['ΣMn (≥13)']
            norm_factor_fe_max["all-ferric-iron"] = np.full(amphi_elems.shape[0], 23.0) / (np.full(amphi_elems.shape[0], 23.0) + 0.5*amphi_elems['Fe: FeOT'])
            norm_factor_fe_max["10ΣFe3+"] = np.full(amphi_elems.shape[0], 36.0) / (np.full(amphi_elems.shape[0], 46.0) - scenario_1[[("T", "Si"), ("T", "Al"), ("C", "Al"), ("C", "Ti"), ("C", "V"), ("C", "Sc"), ("C", "Cr"), ("C", "Mn3+"), ("C", "Zr")]].sum(axis=1))
            norm_factor_fe_max["8SiAl"] = np.full(amphi_elems.shape[0], 8.0) / norm_sums['ΣAl (≥8)']

            amphi_elems_fe_max = amphi_elems.copy()
            amphi_elems_fe_max = amphi_elems_fe_max.mul(norm_factor_fe_max[["15eK", "13eCNK", "all-ferric-iron", "8SiAl"]].max(axis=1), axis=0)

            oxy_mols_fe_max = oxygen_equivalents(amphi_elems_fe_max)
            correction_anions_fe_max = oxy_mols_fe_max.copy()
            correction_anions_fe_max["O: F"] = amphi_elems_fe_max["F: F"]*-0.5
            correction_anions_fe_max["O: Cl"] = amphi_elems_fe_max["Cl: Cl"]*-0.5

            # Calculate the normalization factors for mean Fe3+ content (normalization D)
            amphi_elems_fe_mean = amphi_elems.copy()
            mean_norm_factor = (norm_factor_fe_max[["15eK", "13eCNK", "all-ferric-iron", "8SiAl"]].max(axis=1) + norm_factor_fe_min.min(axis=1)) / 2
            amphi_elems_fe_mean = amphi_elems_fe_mean.mul(mean_norm_factor, axis=0)

            oxy_mols_fe_mean = oxygen_equivalents(amphi_elems_fe_mean)
            correction_anions_fe_mean = oxy_mols_fe_mean.copy()
            correction_anions_fe_mean["O: F"] = amphi_elems_fe_mean["F: F"]*-0.5
            correction_anions_fe_mean["O: Cl"] = amphi_elems_fe_mean["Cl: Cl"]*-0.5

            return amphi_elems_fe_min, correction_anions_fe_min, amphi_elems_fe_max, correction_anions_fe_max, amphi_elems_fe_mean, correction_anions_fe_mean

        # SCENARIO 1: All Fe is Fe2+ (normalization A) -------------------------------------------------------
        amphi_elems, correction_anions = normalization_without_fe3(elem_mols, oxy_mols)

        # Let's organize the sites model without Fe3+ in a multicolumn pandas dataframe
        sites_no_fe3 = {
            "OH": ["OH", "Cl", "F"],

            "T": ["Si", "Al", "Ti"],

            "C": [
                "Al", "Ti", "V", "Sc", "Cr", "Mn3+", "Zr",
                "Mg", "Zn", "Ni", "Co", "Fe2+", "Mn2+", "Li"
            ],

            "B": [
                "Li", "Mn2+", "Fe2+", "Co", "Ni", "Zn",
                "Mg", "Ca", "Sr", "Ba", "Na"
            ],

            "A": [
                "Na", "Ba", "Sr", "Ca", "K", "Rb", "Cs"
            ]
        }

        columns = pd.MultiIndex.from_tuples(
            [(site, element) for site, elements in sites_no_fe3.items() for element in elements],
            names=["Site", "Element"]
        )
        sites_model = pd.DataFrame(index=amphi_elems.index, columns=columns, dtype=float)

        scenario_1 = self.distribute_moles(sites_model.copy(), sites_no_fe3, amphi_elems, correction_anions)

        # SCENARIO 2: Fe3+ is present in the C site -------------------------------------------------------
        (
            amphi_elems_fe_min,
            correction_anions_fe_min,
            amphi_elems_fe_max,
            correction_anions_fe_max,
            amphi_elems_fe_mean,
            correction_anions_fe_mean
        ) = normalization_with_fe3(amphi_elems)

        # We will distribute the elements considering the existence of Fe3+ in the formula
        sites_fe3 = {
            "OH": ["OH", "Cl", "F"],

            "T": ["Si", "Al", "Ti"],

            "C": [
                "Al", "Ti", "Fe3+", "V", "Sc", "Cr", "Mn3+", "Zr",
                "Mg", "Zn", "Ni", "Co", "Fe2+", "Mn2+", "Li"
            ],

            "B": [
                "Li", "Mn2+", "Fe2+", "Co", "Ni", "Zn",
                "Mg", "Ca", "Sr", "Ba", "Na"
            ],

            "A": [
                "Na", "Ba", "Sr", "Ca", "K", "Rb", "Cs"
            ]
        }

        columns = pd.MultiIndex.from_tuples(
            [(site, element) for site, elements in sites_fe3.items() for element in elements],
            names=["Site", "Element"]
        )
        sites_model_fe3 = pd.DataFrame(index=amphi_elems.index, columns=columns, dtype=float)

        scenario_2_min = self.distribute_moles(sites_model_fe3.copy(), sites_fe3, amphi_elems_fe_min, correction_anions_fe_min)

        scenario_2_max = self.distribute_moles(sites_model_fe3.copy(), sites_fe3, amphi_elems_fe_max, correction_anions_fe_max)

        scenario_2_mean = self.distribute_moles(sites_model_fe3.copy(), sites_fe3, amphi_elems_fe_mean, correction_anions_fe_mean)

        return {
            "scenario_1": scenario_1.round(3),
            "scenario_2_min": scenario_2_min.round(3),
            "scenario_2_max": scenario_2_max.round(3),
            "scenario_2_mean": scenario_2_mean.round(3)
        }


    def classify(self, scenarios):
        """
        Classify amphiboles into compositional groups based on
        the occupancy of the B crystallographic site.

        Reproduces the classification rules for amphiboles.
        """

        classified_scenarios = {}

        for scenario_name, formula_df in scenarios.items():

            result = formula_df.copy()

            # B-site occupancy
            b_site = result["B"].fillna(0)

            # NaB
            na_b = b_site["Na"]

            # (Ca + Na)B
            ca_na_b = b_site[["Ca", "Na"]].sum(axis=1)

            # Sum of L-type cations in the B site
            l_type_b = b_site[
                ["Li", "Mn2+", "Fe2+", "Co", "Ni", "Zn", "Mg"]
            ].sum(axis=1)

            # Classification conditions
            conditions = [
                l_type_b >= 1.5,

                (l_type_b <= 0.5) &
                (ca_na_b >= 1.0) &
                (na_b < 0.5),

                (l_type_b <= 0.5) &
                (ca_na_b >= 1.0) &
                (na_b >= 0.5) &
                (na_b < 1.5),

                (l_type_b <= 0.5) &
                (ca_na_b >= 1.0) &
                (na_b >= 1.5),

                (l_type_b > 0.5) &
                (l_type_b < 1.5) &
                (ca_na_b >= 0.5) &
                (ca_na_b <= 1.5)
            ]

            groups = [
                "Mg-Fe-Mn-Li",
                "Ca",
                "Na-Ca",
                "Na",
                "Na-Ca-Mg-Fe-Mn-Li"
            ]

            # Classify samples
            result[("Classification", "Group")] = np.select(
                conditions,
                groups,
                default=""
            )

            classified_scenarios[scenario_name] = result

        return classified_scenarios
