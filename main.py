import streamlit as st

from tabs.home import HomeTab
from tabs.data import DataTab
from tabs.plots import PlotsTab

st.set_page_config(
    page_title="AmphiPlot",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 AmphiPlot")
st.subheader(
    "Plotting compositions of amphiboles from electron microprobe analyses"
)

tab_home, tab_data, tab_plots = st.tabs(
    [
        "🪨 Home",
        "📊 Data & Calculations",
        "📈 Plots"
    ]
)

with tab_home:
    HomeTab().show()

with tab_data:
    DataTab().show()

with tab_plots:
    PlotsTab().show()