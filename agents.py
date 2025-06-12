from mesa import Agent

class BaseAgent(Agent):
    """Agent member of the iterated, spatial prisoner's dilemma model."""

    def __init__(self, model):
        super().__init__(model)
        self.score = None

    def step(self):
        if self.model.activation_order != "Simultaneous":
            self.advance()

    def advance(self):
        payoff = self.get_payoff()
        self.create_children(payoff)
        self.die()

    def get_payoff(self):
        """Get the payoff for the agent based on its action and its opponent's action."""
        opponent = self.model.opponents.get(self, None)
        # If the agent has no opponent, return a default score
        if opponent is None:
            return 1
        
        # If the opponent was processed, the payoff is cached
        # Clear cache and return score
        if self.score is not None:
            score = self.score
            self.score = None
            return score

        # Actions are deterministic on agent and opponent attributes
        my_action, opponent_action = self.get_actions(opponent)

        # Cache opponent score and return agent score
        opponent.score = self.model.payoff[(opponent_action, my_action)]
        return self.model.payoff[(my_action, opponent_action)]

    def get_actions(self, opponent):
        """Determine the actions of the agent and its opponent."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to determine behaviour logic."
        )

    def create_children(self, score):
        """Create children based on the agent's score."""
        while score >= 1:
            self.create_child()
            score -= 1
        if self.random.random() < score:
            self.create_child()

    def create_child(self):
        raise NotImplementedError(
            "This method should be implemented in subclasses to copy agent genes to child."
        )

    def die(self):
        """Remove the agent from the model."""
        self.model.deregister_agent(self)

class SimpleAgent(BaseAgent):
    """An agent that cooperates or defects based on a fixed strategy."""

    def __init__(self, model, action=None):
        super().__init__(model)
        if action is None:
            self.action = self.random.choice(["C", "D"])
        else:
            self.action = action

    def get_actions(self, opponent):
        return self.action, opponent.action

    def create_child(self):
        """Create a new SimpleAgent with the same action."""
        SimpleAgent(self.model, action=self.action)

class BeardAgent(BaseAgent):
    """An agent that may be altruistic toward beaded opponents."""
    def __init__(self, model, has_beard=None, is_beard_altruistic=None):
        super().__init__(model)
        if has_beard is None:
            self.has_beard = self.random.choice([True, False])
        else:
            self.has_beard = has_beard
        if is_beard_altruistic is None:
            self.is_beard_altruistic = self.random.choice([True, False])
        else:
            self.is_beard_altruistic = is_beard_altruistic

    def get_actions(self, opponent):
        if self.is_beard_altruistic and opponent.has_beard:
            agent_action = "C"
        else:
            agent_action = "D"
        if opponent.is_beard_altruistic and self.has_beard:
            opponent_action = "C"
        else:
            opponent_action = "D"

        return agent_action, opponent_action

    def create_child(self):
        """Create a new BeardAgent with the same beard properties."""
        BeardAgent(
            self.model,
            has_beard=self.has_beard,
            is_beard_altruistic=self.is_beard_altruistic
        )

class ReputationAgent(BaseAgent):
    """An agent that uses their trust level and opponent's reputation to decide actions."""
    def __init__(self, model, impostor=None, trust=100, reputation=100):
        super().__init__(model)
        if impostor is None:
            self.impostor = self.random.choice([True, False])
        else:
            self.impostor = impostor
        self.reputation = reputation
        self.trust = trust

    def advance(self):
        score = self.get_payoff()
        if self.impostor:
            self.reputation -= 1
        else:
            self.reputation += 1
        if score < 1:
            self.trust -= 1

    def get_actions(self, opponent):
        if (not self.impostor) and (self.trust > opponent.reputation):
            agent_action = "C"
        else:
            agent_action = "D"
        if (not opponent.impostor) and (opponent.trust > self.reputation):
            opponent_action = "C"
        else:
            opponent_action = "D"

        return agent_action, opponent_action
