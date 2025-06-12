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


def pd_agent_portrayal(agent):
    """
    Portrayal function for rendering PD agents in the visualization.
    """
    return {
        "color": "blue" if agent.move == "C" else "red",
        "marker": "s",  # square marker
        "size": 25,
    }


# Model parameters
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "initial_pop": Slider("Initial Population Size", value=50, min=10, max=100, step=1),
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
    components=[plot_all, plot_component],
    model_params=model_params,
    name="Spatial Prisoner's Dilemma",
)
page  # noqa B018
