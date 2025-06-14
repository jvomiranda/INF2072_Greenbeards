from model import Model
from tqdm import tqdm
import os

model_params = {
    "initial_pop": 100,
    "activation_order": "Simultaneous",
    "distribution": 0.5,
    "stage": "Simple",
    "child_cost": 1,
}

if not os.path.exists(f"data"):
    os.mkdir(f"data")
for stage in Model.simulation_stages:
    if not os.path.exists(f"data/{stage}"):
        os.mkdir(f"data/{stage}")

print("Generating data for stage 1 agents")
for seed in tqdm(range(100)):
    model_params["seed"] = seed
    model_params["stage"] = "Simple"
    model_params["child_cost"] = 1
    model = Model(**model_params)
    model.run(20)
    data = model.datacollector.get_model_vars_dataframe()
    if not data.empty:
        data.to_csv(model.filename)

print("Generating data for stage 2 agents")
for seed in tqdm(range(100)):
    model_params["seed"] = seed
    model_params["stage"] = "Beards with one alele"
    model_params["child_cost"] = 3
    model = Model(**model_params)
    model.run(20)
    data = model.datacollector.get_model_vars_dataframe()
    if not data.empty:
        data.to_csv(model.filename)

print("Generating data for stage 3 agents")
for seed in tqdm(range(100)):
    model_params["seed"] = seed
    model_params["stage"] = "Beards with two aleles"
    model_params["child_cost"] = 1
    model = Model(**model_params)
    model.run(20)
    data = model.datacollector.get_model_vars_dataframe()
    if not data.empty:
        data.to_csv(model.filename)

print("Generating data for stage 4 agents")
for seed in tqdm(range(100)):
    model_params["seed"] = seed
    model_params["stage"] = "Reputation"
    model_params["child_cost"] = 1
    model = Model(**model_params)
    model.run(20)
    data = model.datacollector.get_model_vars_dataframe()
    if not data.empty:
        data.to_csv(model.filename)