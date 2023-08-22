import streamlit as st
from stratclust.stratclust import ConstrainedHierarchicalClustering
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
filein = st.sidebar.file_uploader("Upload your data", type="csv")
chc = ConstrainedHierarchicalClustering()

if filein:
    chc.import_data_csv(filein)
    constraintcolumn = st.sidebar.selectbox(
        "Select constraint column", chc.data.columns
    )

    constraintcolumn = [constraintcolumn]
    compositioncolumns = st.sidebar.multiselect(
        "Select composition columns", chc.data.columns
    )
    chc.set_constraint_composition(constraintcolumn, compositioncolumns)

    with st.sidebar.expander("Cleaning notes", expanded=False):
        if len(chc.warnings) > 0:
            for v in chc.warnings.values():
                st.write(v)

    with st.expander("Table view", expanded=False):
        st.dataframe(chc.data)

    with st.sidebar.form("Plotting"):
        mdlname = st.text_input("Model name", "model1")
        yaxisunit = st.text_input("Y axis unit", "M")
        yaxisinterval = st.number_input(
            "Y axis interval", min_value=1, max_value=len(chc.data)
        )
        yaxislabel = st.text_input("Y axis label", "Depth")
        title = st.text_input("Title", "Default Title")
        btnResult0 = st.form_submit_button("Plot dendrogram")

    if btnResult0:
        with st.expander("Dendrogram", expanded=False):
            chc.make_plot(mdlname)
            _ = chc.format_plot(mdlname, yaxisinterval, yaxisunit, yaxislabel, title)  # type: ignore
            displayplot = chc.fullmodel[mdlname]["fig"]
            if chc not in st.session_state:
                st.session_state["chc"] = chc
            st.pyplot(displayplot, use_container_width=True)

    with st.sidebar.form("Downhole"):
        elemstoplot = st.multiselect(
            "Choose elements to plot downhole", compositioncolumns
        )
        mdlnamedh = st.text_input("Model name", "model1")
        btnResult1 = st.form_submit_button("Plot downhole data")

    if btnResult1:
        with st.expander("Downhole data", expanded=False):
            figx, axx = plt.subplots(
                nrows=1,
                ncols=len(elemstoplot),
                figsize=(10, 10),
                sharey=False,
            )
            for elem, axis in zip(elemstoplot, figx.axes):
                axis.plot(chc.data[elem], chc.data[constraintcolumn[0]])
                axis.set_xlabel(elem)
                axis.invert_xaxis()
                axis.invert_yaxis()
            st.pyplot(figx)

    with st.sidebar.form("DendroDownhole"):
        subrange = st.slider(
            "Select a range of values",
            min_value=chc.data[constraintcolumn[0]].min(),
            max_value=chc.data[constraintcolumn[0]].max(),
            value=(
                chc.data[constraintcolumn[0]].min(),
                chc.data[constraintcolumn[0]].max(),
            ),
        )
        elemstoplot = st.multiselect(
            "Choose elements to plot downhole", compositioncolumns
        )
        mdlnameboth = st.text_input("Model name", "model1")
        yaxisunit = st.text_input("Y axis unit", "M")
        yaxisinterval = st.number_input(
            "Y axis interval", min_value=1, max_value=len(chc.data)
        )
        yaxislabel = st.text_input("Y axis label", "Depth")
        title = st.text_input("Title", "Default Title")
        btnResult2 = st.form_submit_button("Plot dendrogram and downhole data")

    if btnResult2:
        with st.expander("Dendrogram and downhole", expanded=False):
            figx, axx = plt.subplots(
                nrows=1,
                ncols=len(elemstoplot) + 1,
                figsize=(10, 10),
                sharey=False,
            )

            chc.make_plot(mdlnameboth, fig=figx, ax=axx[-1])

            _ = chc.format_plot(mdlnameboth, yaxisinterval, yaxisunit, yaxislabel, "")  # type: ignore

            difftop = np.abs(min(chc.data[constraintcolumn[0]]) - subrange[0] + 2) * 10
            diffbot = np.abs(max(chc.data[constraintcolumn[0]]) - subrange[1]) * 10

            oldylim = axx[-1].get_ylim()

            axx[-1].set_ylim(
                top=oldylim[1] - difftop,
                bottom=oldylim[0] + diffbot,
            )

            for elem, axis in zip(elemstoplot, axx[:-1]):
                axis.set_ylim(
                    axx[-1].get_ylim()
                )  # this has to go first or else it reorders the y axis
                axis.plot(chc.data[elem], np.arange(5, len(chc.data) * 10, 10))
                axis.yaxis.tick_right()
                axis.invert_yaxis()
                axis.invert_xaxis()
                axis.set_xlabel(elem)
                plt.setp(axis.get_yticklabels(), visible=False)
            figx.suptitle(title, fontsize=16)
            figx.tight_layout()

            st.pyplot(figx)
