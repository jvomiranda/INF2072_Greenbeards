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
        import altair as alt
        import solara
        from solara.components.figure_altair import FigureAltair

        df = model.datacollector.get_model_vars_dataframe()
        df = df.reset_index()
        if df.columns[0] != "Step":
            df = df.rename(columns={df.columns[0]: "Step"})

        if df.empty or "All Agents" not in df.columns:
            return solara.Text("Waiting for simulation data...")

        all_zeros_col_reputation = (df["Average Reputation"] == 0).all()
        all_zeros_col_impostors = (df["Impostors"] == 0).all()

        if not all_zeros_col_reputation:
            # Stage 4: Reputation and Trust Dynamics

            # Melt population metrics
            population_df = df.melt(
                id_vars=["Step"],
                value_vars=["All Agents", "Noble Agents", "Outcast Agents"],
                var_name="Metric",
                value_name="Count"
            )
            population_colors = alt.Color("Metric:N", title="Metric", scale=alt.Scale(
                domain=["All Agents", "Noble Agents", "Outcast Agents"],
                range=[
                    "blue", "green", "red",
                ]
            ))

            # Melt reputation/trust metrics
            reputation_df = df.melt(
                id_vars=["Step"],
                value_vars=["Average Reputation", "Average Trust", "Outcast Reputation", "Outcast Trust",
                            "Noble Reputation", "Noble Trust"],
                var_name="Metric",
                value_name="Value"
            )
            reputation_colors = alt.Color("Metric:N", title="Metric", scale=alt.Scale(
                domain=[
                    "Outcast Reputation", "Outcast Trust",
                    "Noble Reputation", "Noble Trust",
                    "Average Reputation", "Average Trust"
                ],
                range=[
                    "red", "orange",  # outcasts (reputation < 50)
                    "green", "lightgreen",  # nobles (reputation >= 50)
                    "blue", "lightblue"  # others (population averages)
                ]
            ))

            if "Cooperate Actions" in df.columns and "Defect Actions" in df.columns:
                actions_df = df.melt(
                    id_vars=["Step"],
                    value_vars=["Cooperate Actions", "Defect Actions"],
                    var_name="Action",
                    value_name="Count"
                )
            # Line chart: population
            population_chart = alt.Chart(population_df).mark_line(point=False).encode(
                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population", scale=alt.Scale(domain=[0, 200])),
                color=population_colors,
                tooltip=["Step", "Metric", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Population Over Time"
            )

            # Line chart: reputation/trust
            reputation_chart = alt.Chart(reputation_df).mark_line(point=True).encode(
                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Value:Q", title="Score"),
                color=reputation_colors,
                tooltip=["Step", "Metric", "Value"]
            ).properties(
                width=600,
                height=300,
                title="Reputation and Trust Dynamics"
            )

            interactions_colors = alt.Color("Action:N", title="Action", scale=alt.Scale(
                domain=[
                    "Cooperate Actions", "Defect Actions",
                    # "CC Interactions", "CD Interactions", "DD Interactions"
                    ],
                range=[
                    "green", "red",
                    # "light green", "yellow", "orange"
                    ]
            ))

            interactions_chart = alt.Chart(actions_df).mark_line(point=True).encode(
                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Number of Actions"),
                color=interactions_colors,
                tooltip=["Step", "Action", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Interactions Over Time"
            )
            # Concatenate with independent Y axes
            with solara.Column():
                solara.FigureAltair(population_chart)
                solara.FigureAltair(reputation_chart)
                if interactions_chart:
                    solara.FigureAltair(interactions_chart)

        elif not all_zeros_col_impostors:
            # Stage 2 & 3: Beard Dynamics
            population_df = df.melt(
                id_vars=["Step"],
                value_vars=["All Agents", "Cooperating Agents"],
                var_name="Metric",
                value_name="Count"
            )

            detailed_population_df = df.melt(
                id_vars=["Step"],
                value_vars=["Impostors", "Cowards", "True Beards", "Suckers"],
                var_name="Metric",
                value_name="Count"
            )
            detailed_population_colors = alt.Color("Metric:N", title="Metric", scale=alt.Scale(
                domain=["Impostors", "True Beards", "Cowards", "Suckers"],
                range=["red", "green", "yellow", "blue"]
            ))

            population_chart = alt.Chart(population_df).mark_line(point=True).encode(
                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population"),
                color=alt.Color("Metric:N", title="Metric", scale=alt.Scale(scheme='category10')),
                tooltip=["Step", "Metric", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Population Dynamics Over Time"
            )

            detailed_population_chart = alt.Chart(detailed_population_df).mark_line(point=True).encode(
                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population"),
                color=detailed_population_colors,
                tooltip=["Step", "Metric", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Classes and Trust Dynamics"
            ).interactive()

            with solara.Column():
                solara.FigureAltair(population_chart)
                solara.FigureAltair(detailed_population_chart)

        else:
            # Stage 1: Basic Population Dynamics
            population_colors = alt.Color("Metric:N", title="Metric", scale=alt.Scale(
                domain=["All Agents", "Cooperating Agents", "Non-Cooperating Agents"],
                range=["blue", "green", "red"]
            ))
            population_df = df.melt(
                id_vars=["Step"],
                value_vars=["All Agents", "Cooperating Agents", "Non-Cooperating Agents"],
                var_name="Metric",
                value_name="Count"
            )

            population_chart = alt.Chart(population_df).mark_line(point=True).encode(
                x=alt.X("Step:Q", title="Step"),
                y=alt.Y("Count:Q", title="Population"),
                color=population_colors,
                tooltip=["Step", "Metric", "Count"]
            ).properties(
                width=600,
                height=300,
                title="Population Dynamics Over Time"
            )

            return FigureAltair(population_chart)

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
plot_all = make_plot_component("All Agents")
plot_component = make_plot_component("Cooperating Agents")

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
