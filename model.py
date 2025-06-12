from mesa import DataCollector, Model as MesaModel
from mesa.discrete_space import OrthogonalMooreGrid
from agents import SimpleAgent, BeardAgent, ReputationAgent

class Model(MesaModel):
    """Model class for iterated, spatial prisoner's dilemma model."""

    activation_regimes = ["Sequential", "Random", "Simultaneous"]
    simulation_stages = ["Simple", "Beards with one alele", "Beards with two aleles", "Reputation"]

    # This dictionary holds the payoff for the agents,
    # keyed on: (my_move, other_move)
    payoff = {("C", "C"): 1.5, ("C", "D"): 0, ("D", "C"): 2, ("D", "D"): 1}

    def __init__(
        self, initial_pop=50, activation_order="Random", payoffs=None, seed=None, distribution=0.5, stage="Simple"
    ):
        super().__init__(seed=seed)
        self.activation_order = activation_order

        #TODO: Change grid model to something more appropriate
        self.grid = OrthogonalMooreGrid((50, 50), torus=True, random=self.random)

        if payoffs is not None:
            self.payoff = payoffs

        # Create agents based on the stage and distribution
        self.create_agents(initial_pop, stage, distribution)

        # Defines metrics to graph
        self.datacollector = DataCollector(
            {
                "Cooperating_Agents": self.num_cooperating_agents,
                "All_Agents": self.num_agents,
                "Beard_Agents": lambda m: len(m.agents)
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def create_agents(self, initial_pop, stage, distribution):
        """Create agents in the model."""
        match stage:
            case "Simple":
                SimpleAgent.create_agents(model=self, n=int(initial_pop*distribution), action="C")
                SimpleAgent.create_agents(model=self, n=int(initial_pop*(1-distribution)), action="D")
            case "Beards with one alele":
                BeardAgent.create_agents(model=self, n=int(initial_pop*distribution), has_beard=True, is_beard_altruistic=True)
                BeardAgent.create_agents(model=self, n=int(initial_pop*(1-distribution)), has_beard=False, is_beard_altruistic=False)
            case "Beards with two aleles":
                # TODO: Fix the distribution logic for bearded agents
                # Here we assume a 25% distribution for each type of beard agent
                BeardAgent.create_agents(model=self, n=int(initial_pop*0.25), has_beard=True, is_beard_altruistic=True)
                BeardAgent.create_agents(model=self, n=int(initial_pop*0.25), has_beard=True, is_beard_altruistic=False)
                BeardAgent.create_agents(model=self, n=int(initial_pop*0.25), has_beard=False, is_beard_altruistic=True)
                BeardAgent.create_agents(model=self, n=int(initial_pop*0.25), has_beard=False, is_beard_altruistic=False)
            case "Reputation":
                ReputationAgent.create_agents(model=self, n=int(initial_pop*distribution), impostor=True)
                ReputationAgent.create_agents(model=self, n=int(initial_pop*(1-distribution)), impostor=False)
            case _:
                raise ValueError(f"Unknown stage: {stage}")

    def match_agents(self):
        """Match agents with their opponents."""
        agents_copy = list(self.agents)
        self.random.shuffle(agents_copy)
        self.opponents = {}
        for _ in range(len(self.agents) // 2):
            agent1 = agents_copy.pop()
            agent2 = agents_copy.pop()
            self.opponents[agent1] = agent2
            self.opponents[agent2] = agent1

    def step(self):
        self.match_agents()
        # Activate all agents, based on the activation regime
        match self.activation_order:
            case "Sequential":
                self.agents.do("step")
            case "Random":
                self.agents.shuffle_do("step")
            case "Simultaneous":
                self.agents.do("step")
                self.agents.do("advance")
            case _:
                raise ValueError(f"Unknown activation order: {self.activation_order}")

        # Collect data
        self.datacollector.collect(self)

    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()

    def num_agents(self):
        """Returns the number of agents in the model."""
        return len(self.agents)

    def num_cooperating_agents(self):
        """Returns the number of cooperating agents in the model based on stage."""
        if not self.agents:
            return 0

        first_agent = self.agents[0]

        if isinstance(first_agent, SimpleAgent):
            return len([a for a in self.agents if a.action == "C"])

        elif isinstance(first_agent, BeardAgent):
            return len([a for a in self.agents if a.is_beard_altruistic])

        elif isinstance(first_agent, ReputationAgent):
            return len([a for a in self.agents if not a.impostor])

        else:
            return 0

    def num_bearded_agents(self):
        """Returns the number of bearded agents in the model."""
        if len(self.agents) == 0 or type(self.agents[0]) != BeardAgent:
            return 0
        return len([a for a in self.agents if a.has_beard])
