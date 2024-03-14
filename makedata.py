from pydantic import BaseModel, Field
from typing import List, Union, Optional
import json
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite


# Define your Pydantic models here (as you've already defined them in your question)
class RTPBase(BaseModel):
    """Parameters defined in a protocol."""

    displayName: str = Field(..., description="Display string for the parameter.")
    variableName: str = Field(..., description="Python variable name of the parameter.")
    description: str = Field(..., description="Detailed description of the parameter.")
    suffix: Optional[str] = Field(
        None,
        description="Units (like mL, mm/sec, etc) or a custom suffix for the parameter.",
    )


class IntParameter(RTPBase):
    """An integer parameter defined in a protocol."""

    min: int = Field(
        ..., description="Minimum value that the integer param is allowed to have."
    )
    max: int = Field(
        ..., description="Maximum value that the integer param is allowed to have."
    )
    default: int = Field(
        ...,
        description="Default value of the parameter, to be used when there is no client-specified value.",
    )


class FloatParameter(RTPBase):
    """A float parameter defined in a protocol."""

    min: float = Field(
        ..., description="Minimum value that the float param is allowed to have."
    )
    max: float = Field(
        ..., description="Maximum value that the float param is allowed to have."
    )
    default: float = Field(
        ...,
        description="Default value of the parameter, to be used when there is no client-specified value.",
    )


class EnumChoice(BaseModel):
    """Components of choices used in RTP Enum Parameters."""

    displayName: str = Field(..., description="Display string for the param's choice.")
    value: str = Field(..., description="Enum value of the param's choice.")


class EnumParameter(RTPBase):
    """A string enum defined in a protocol."""

    choices: List[EnumChoice] = Field(
        ..., description="List of valid choices for this parameter."
    )
    default: str = Field(
        ...,
        description="Default value of the parameter, to be used when there is no client-specified value.",
    )


RunTimeParameter = Union[IntParameter, FloatParameter, EnumParameter]

# normal_chars = st.characters(whitelist_categories=("Lu", "Ll", "Nd"))
normal_chars = st.characters(min_codepoint=48, max_codepoint=57) | st.characters(min_codepoint=65, max_codepoint=90) | st.characters(min_codepoint=97, max_codepoint=122)

# Define the corrected strategies
@composite
def enum_choice_strategy(draw):
    display_name = draw(st.text(alphabet=normal_chars, min_size=1))
    value = draw(st.text(alphabet=normal_chars, min_size=1))
    return EnumChoice(displayName=display_name, value=value)


@composite
def enum_parameter_strategy(draw):
    displayName = draw(st.text(alphabet=normal_chars, min_size=1))
    variableName = draw(st.text(alphabet=normal_chars, min_size=1))
    description = draw(st.text(alphabet=normal_chars, min_size=1))
    choices = draw(st.lists(enum_choice_strategy(), min_size=1, max_size=5))
    default = draw(st.sampled_from([choice.value for choice in choices]))
    return EnumParameter(
        displayName=displayName,
        variableName=variableName,
        description=description,
        choices=choices,
        default=default,
    )


# Strategy for IntParameter
@composite
def int_parameter_strategy(draw):
    displayName = draw(st.text(alphabet=normal_chars, min_size=1))
    variableName = draw(st.text(alphabet=normal_chars, min_size=1))
    description = draw(st.text(alphabet=normal_chars, min_size=1))
    suffix = draw(st.one_of(st.none(), st.text(alphabet=normal_chars, min_size=1)))
    min_value = draw(st.integers(min_value=-1000, max_value=0))
    max_value = draw(st.integers(min_value=1, max_value=1000))
    default = draw(st.integers(min_value=min_value, max_value=max_value))
    return IntParameter(
        displayName=displayName,
        variableName=variableName,
        description=description,
        suffix=suffix,
        min=min_value,
        max=max_value,
        default=default,
    )


@composite
def float_parameter_strategy(draw):
    displayName = draw(st.text(alphabet=normal_chars, min_size=1))
    variableName = draw(st.text(alphabet=normal_chars, min_size=1))
    description = draw(st.text(alphabet=normal_chars, min_size=1))
    suffix = draw(st.one_of(st.none(), st.text(alphabet=normal_chars, min_size=1)))
    min_value = draw(
        st.floats(
            min_value=-1000.0, max_value=0.0, allow_nan=False, allow_infinity=False
        )
    )
    max_value = draw(
        st.floats(
            min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False
        )
    )
    # Ensure default is within the range
    default = draw(
        st.floats(
            min_value=min_value,
            max_value=max_value,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    return FloatParameter(
        displayName=displayName,
        variableName=variableName,
        description=description,
        suffix=suffix,
        min=min_value,
        max=max_value,
        default=default,
    )


@composite
def protocol_runtime_parameters_strategy(draw):
    int_params = draw(st.lists(int_parameter_strategy(), min_size=1, max_size=5))
    float_params = draw(st.lists(float_parameter_strategy(), min_size=1, max_size=5))
    enum_params = draw(st.lists(enum_parameter_strategy(), min_size=1, max_size=5))
    # Return a dict combining all parameter types under the 'runTimeParameters' key
    return {"runTimeParameters": int_params + float_params + enum_params}


def generate_and_save_params():
    examples = []
    for _ in range(5):  # Generate 10 examples
        example = (
            protocol_runtime_parameters_strategy().example()
        )  # Generate a single example
        # Convert Pydantic models to dicts for JSON serialization
        for key in example:
            example[key] = [param.dict() for param in example[key]]
        examples.append(example)

    # Serialize and save to JSON
    with open("protocol_runtime_parameters.json", "w") as f:
        json.dump(examples, f, indent=4)

def main():
    generate_and_save_params()

if __name__ == "__main__":
    main()
