import numpy as np
import pandas as pd

oxide_weights = pd.Series(
    {
        "SiO2": 60.08,
        "TiO2": 79.87,
        "Al2O3": 101.96,
        "Fe2O3": 159.688,
        "FeO": 71.84,
        "MnO": 70.94,
        "MgO": 40.30,
        "CaO": 56.08,
        "Na2O": 61.98,
        "Li2O": 29.88,
        "K2O": 94.196,
        "BaO": 153.33,
        "Cs2O": 281.81,
        "Rb2O": 186.94,
        "F": 18.998,
        "Cl": 35.453,
        "Sc2O3": 137.91,
        "Cr2O3": 151.99,
        "V2O3": 149.88,
        "ZnO": 81.39,
        "NiO": 74.69,
        "CoO": 74.93,
        "ZrO2": 123.22,
        "SrO": 103.619,
        "Mn2O3": 157.8743,
    },
    name="weight"
)

n_cations = np.array([1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 2])

n_anions = np.array([2, 2, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 3, 3, 3, 1, 1, 1, 2, 1, 3])

cations_names = [
    "Si: SiO2",
    "Ti: TiO2",
    "Al: Al2O3",
    "FeIII: Fe2O3",
    "FeII: FeO",
    "Mn: MnO",
    "Mg: MgO",
    "Ca: CaO",
    "Na: Na2O",
    "Li: Li2O",
    "K: K2O",
    "Ba: BaO",
    "Cs: Cs2O",
    "Rb: Rb2O",
    "F: F",
    "Cl: Cl",
    "Sc: Sc2O3",
    "Cr: Cr2O3",
    "V: V2O3",
    "Zn: ZnO",
    "Ni: NiO",
    "Co: CoO",
    "Zr: ZrO2",
    "Sr: SrO",
    "Mn: Mn2O3"
    ]

anions_names = [f"O: {item}" for item in list(oxide_weights.index)]

oxide_info = pd.DataFrame({
    "weight": oxide_weights,
    "n_cations": n_cations,
    "n_anions": n_anions,
    "cations_names": cations_names,
    "anions_names": anions_names
})

class AmphiboleCalculator:

    def __init__(self, dataframe):

        self.df = dataframe.copy()
        self.oxides = list(dataframe.columns)
        self.weights = oxide_info.loc[self.oxides, "weight"]
        self.n_cations = oxide_info.loc[self.oxides, "n_cations"].to_numpy()
        self.n_anions = oxide_info.loc[self.oxides, "n_anions"].to_numpy()
        self.cations_names = oxide_info.loc[self.oxides, "cations_names"].tolist()
        self.anions_names = oxide_info.loc[self.oxides, "anions_names"].tolist()

    def calculate_formula(self):

        # 1. Convert the unit from % of weight to moles of each oxide/element
        ox_mols = self.df.div(self.weights, axis=1)
        ox_mols["FeOT"] = (self.df["FeO"] + 0.8998*self.df["Fe2O3"])/ np.full(self.df.shape[0], self.weights["FeO"])
        
        # 2. Obtain the number of moles of each cation and anion
        elem_mols = ox_mols.mul(self.n_cations.append(1), axis=1)
        elem_mols.columns = self.cations_names.append("Fe: FeOT")
        oxy_mols = ox_mols.mul(self.n_anions.append(1), axis=1)
        oxy_mols.columns = self.anions_names.append("O: FeOT")

        # 3. Scenario analysis

        return self.df

    def classify(self):

        return self.df