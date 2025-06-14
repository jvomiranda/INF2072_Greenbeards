"""
Solara-based visualization.
"""
from mesa.examples.advanced.pd_grid.model import PdGrid
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)
from model import Model
import solara
import altair as alt


def pd_agent_portrayal(agent):
    """
    Portrayal function for rendering PD agents in the visualization.
    """
    return {
        "color": "blue" if agent.move == "C" else "red",
        "marker": "s",  # square marker
        "size": 25,
    }

def AltairLinePlotWrapper(model):
    @solara.component
    def AltairLinePlot():
        df = model.datacollector.get_model_vars_dataframe()
        df = df.reset_index()
        if df.columns[0] != "Step":
            df = df.rename(columns={df.columns[0]: "Step"})

        if df.empty or "All_Agents" not in df.columns:
            return solara.Text("Waiting for simulation data...")

        all_zeros_col_reputation = (df["Average Reputation"] == 0).all()

        if not all_zeros_col_reputation:
            melted_df = df.melt(
                id_vars=["Step"],
                value_vars=["All_Agents"],
                var_name="Metric",
                value_name="Count"
                )

            melted_df2 = df.melt(
                id_vars=["Step"],
                value_vars=["Average Reputation", "Average Trust"],
                var_name="Metric",
                value_name="Count"
                )
            
            chart1 = alt.Chart(melted_df).mark_line().encode(

                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population"),
                color=alt.Color("Metric:N", title="Metric"),
                tooltip=["Step", "Count"]
                ).properties(
                    width=600,
                    height=300,
                    title="Population Over Time")

            chart2 = alt.Chart(melted_df2).mark_bar().encode(

                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population"),
                color=alt.Color("Metric:N", title="Metric").scale(scheme="lighttealblue-3"),
                tooltip=["Step", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Reputation and Trust Dynamics"
            )
            chart = chart1 + chart2

        else:
            melted_df = df.melt(
                id_vars=["Step"],
                value_vars=["All_Agents", "Cooperating_Agents"],
                var_name="Metric",
                value_name="Count"
            )

            chart = alt.Chart(melted_df).mark_line(point=True).encode(

                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population"),
                color=alt.Color("Metric:N", title="Metric"),
                tooltip=["Step", "Metric", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Population Dynamics Over Time"
            )

        from solara.components.figure_altair import FigureAltair
        return FigureAltair(chart)

    return AltairLinePlot()


# Model parameters
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "initial_pop": Slider("Initial Population Size", value=100, min=10, max=100, step=1),
    "activation_order": {
        "type": "Select",
        "value": "Simultaneous",
        "values": PdGrid.activation_regimes,
        "label": "Activation Regime",
    },
    "distribution": Slider(
        "Cooperation Distribution",
        value=0.5,
        min=0.0,
        max=1.0,
        step=0.1,
    ),
    "stage": {
        "type": "Select",
        "value": "Simple",
        "values": Model.simulation_stages,
        "label": "Stage",
    },
    "child_cost": Slider(
        "Child Cost",
        value=1,
        min=0.25,
        max=4,
        step=0.25,
    ),
}


# TODO: Change space model to something more appropriate
# grid_viz = make_space_component(agent_portrayal=pd_agent_portrayal)

# TODO: Create more/better plots for tracking population dynamics
plot_all = make_plot_component("All_Agents")
plot_component = make_plot_component("Cooperating_Agents")

# Initialize model
initial_model = Model()


# Create visualization with all components
page = SolaraViz(
    model=initial_model,
    components=[
        lambda model: AltairLinePlotWrapper(model),
    ],
    model_params=model_params,
    name="Greenbeards Simulations",
)

page  # noqa B018
