import json
from typing import List, Union, Optional
from pydantic import BaseModel, ValidationError

from makedata import IntParameter, FloatParameter, EnumParameter, EnumChoice


# Function to parse and create instances of Pydantic models
def create_parameter_instance(
    param: dict,
) -> Union[IntParameter, FloatParameter, EnumParameter] | None:
    min = param.get("min", 0)
    max = param.get("max", 100)
    default = param.get("default", 0)
    if param["type"] == "int":
        # Create an instance of IntParameter
        return IntParameter(
            displayName=param["label"],
            variableName=param["name"],
            description="",
            min=min,
            max=max,
            default=default,
        )
    elif param["type"] == "float":
        # Create an instance of FloatParameter
        return FloatParameter(
            displayName=param["label"],
            variableName=param["name"],
            description="",
            min=min,
            max=max,
            default=default,
        )
    elif param["type"] == "dropDown":
        # Create an instance of EnumParameter
        # Convert 'options' to 'choices' suitable for EnumParameter
        choices = [
            EnumChoice(
                displayName=option["label"],
                value=option["value"] if option["value"] is not None else "NONE",
            )
            for option in param.get("options", [])
        ]
        default = param.get("options", [])[0]["value"]
        # Ensure the 'default' is correctly set, especially if it's expected to be a value from 'choices'
        return EnumParameter(
            displayName=param["label"],
            variableName=param["name"],
            description="",
            choices=choices,
            default=default,
        )
    else:
        print(f"Unknown parameter type: {param['type']}")
    return None


# List to hold all parameter instances
parameter_instances = []

# Load JSON Data
with open("prodPLparams.json", "r") as file:
    params_json = json.load(file)

# Parse JSON and create parameter instances
for param_group in params_json:
    group = []
    for param in param_group:
        try:
            parameter_instance = create_parameter_instance(param)
            if parameter_instance:
                group.append(parameter_instance.dict())
        except ValueError as e:
            print(e)
    parameter_instances.append(group)


# Specify the output file name
output_filename = "prod_parameter_instances2.json"

# Write the list of dictionaries to a JSON file
with open(output_filename, "w") as output_file:
    # Use json.dump() to serialize and save the data
    json.dump(parameter_instances, output_file, indent=4)

print(f"Saved parameter instances to '{output_filename}'.")