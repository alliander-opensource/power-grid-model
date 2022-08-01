# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pytest

from power_grid_model import initialize_array, power_grid_meta_data
from power_grid_model.enum import CalculationType
from power_grid_model.validation.errors import (
    IdNotInDatasetError,
    MissingValueError,
    MultiComponentNotUniqueError,
)
from power_grid_model.validation.validation import (
    assert_valid_data_structure,
    validate_ids_exist,
    validate_required_values,
    validate_unique_ids_across_components,
    validate_values,
)

NaN = power_grid_meta_data["input"]["node"]["nans"]["id"]


def test_assert_valid_data_structure():
    node_input = initialize_array("input", "node", 3)
    line_input = initialize_array("input", "line", 3)
    node_update = initialize_array("update", "node", 3)
    line_update = initialize_array("update", "line", 3)

    # Input data: Assertion ok
    assert_valid_data_structure({"node": node_input, "line": line_input}, "input")

    # Update data: Assertion ok
    assert_valid_data_structure({"node": node_update, "line": line_update}, "update")

    # There is no such thing as 'output' data
    with pytest.raises(KeyError, match=r"output"):
        assert_valid_data_structure({"node": node_input, "line": line_input}, "output")

    # Input data is not valid update data
    with pytest.raises(TypeError, match=r"Unexpected Numpy structured array"):
        assert_valid_data_structure({"node": node_input, "line": line_input}, "update")

    # Update data is not valid input data
    with pytest.raises(TypeError, match=r"Unexpected Numpy structured array"):
        assert_valid_data_structure({"node": node_update, "line": line_update}, "input")

    # A normal numpy array is not valid input data
    node_dummy = np.array([(1, 10.5e3), (2, 10.5e3), (3, 10.5e3)])
    with pytest.raises(TypeError, match=r"Unexpected Numpy array"):
        assert_valid_data_structure({"node": node_dummy, "line": line_input}, "input")

    # A structured numpy array, with wrong data type for u_rated f4 != f8, is not valid input data
    node_dummy = np.array([(1, 10.5e3), (2, 10.5e3), (3, 10.5e3)], dtype=[("id", "i4"), ("u_rated", "f4")])
    with pytest.raises(TypeError, match=r"Unexpected Numpy structured array"):
        assert_valid_data_structure({"node": node_dummy, "line": line_input}, "input")

    # A structured numpy array, with correct data types is not a valid, is still not valid input data.
    # N.B. It is not 'aligned'
    node_dummy = np.array([(1, 10.5e3), (2, 10.5e3), (3, 10.5e3)], dtype=[("id", "i4"), ("u_rated", "f8")])
    with pytest.raises(TypeError, match=r"Unexpected Numpy structured array"):
        assert_valid_data_structure({"node": node_dummy, "line": line_input}, "input")

    # Invalid component type
    input_with_wrong_component = {"node": node_input, "some_random_component": line_input}
    with pytest.raises(KeyError, match="Unknown component 'some_random_component' in input_data."):
        assert_valid_data_structure(input_with_wrong_component, "input")

    input_with_wrong_data_type = {"node": node_input, "line": [1, 2, 3]}
    with pytest.raises(TypeError, match="Unexpected data type list for 'line' input_data "):
        assert_valid_data_structure(input_with_wrong_data_type, "input")


def test_validate_unique_ids_across_components():
    node = initialize_array("input", "node", 3)
    node["id"] = [1, 2, 3]

    line = initialize_array("input", "line", 3)
    line["id"] = [4, 5, 3]

    transformer = initialize_array("input", "transformer", 3)
    transformer["id"] = [1, 6, 7]

    source = initialize_array("input", "source", 3)
    source["id"] = [8, 9, 10]

    input_data = {"node": node, "line": line, "transformer": transformer, "source": source}

    unique_id_errors = validate_unique_ids_across_components(input_data)

    assert (
        MultiComponentNotUniqueError(
            [("node", "id"), ("line", "id"), ("transformer", "id")],
            [("node", 1), ("node", 3), ("line", 3), ("transformer", 1)],
        )
        in unique_id_errors
    )
    assert len(unique_id_errors[0].ids) == 4


def test_validate_ids_exist():
    source = initialize_array("input", "source", 3)
    source["id"] = [1, 2, 3]

    sym_load = initialize_array("input", "sym_load", 3)
    sym_load["id"] = [4, 5, 6]

    input_data = {
        "source": source,
        "sym_load": sym_load,
    }

    source_update = initialize_array("update", "source", 3)
    source_update["id"] = [1, 2, 4]
    source_update["u_ref"] = [1.0, 2.0, 3.0]

    sym_load_update = initialize_array("update", "sym_load", 3)
    sym_load_update["id"] = [4, 5, 7]
    sym_load_update["p_specified"] = [4.0, 5.0, 6.0]

    update_data = {"source": source_update, "sym_load": sym_load_update}

    invalid_ids = validate_ids_exist(update_data, input_data)

    assert IdNotInDatasetError("source", [4], "input_data") in invalid_ids
    assert IdNotInDatasetError("sym_load", [7], "input_data") in invalid_ids


@pytest.mark.parametrize(
    "calculation_type",
    [
        pytest.param(None, id="no calculation type specified"),
        pytest.param(CalculationType.power_flow, id="power_flow"),
        pytest.param(CalculationType.state_estimation, id="state_estimation"),
    ],
)
@pytest.mark.parametrize("symmetric", [pytest.param(True, id="symmetric"), pytest.param(False, id="asymmetric")])
def test_validate_required_values_sym_calculation(calculation_type, symmetric):
    node = initialize_array("input", "node", 1)
    line = initialize_array("input", "line", 1)
    link = initialize_array("input", "link", 1)
    transformer = initialize_array("input", "transformer", 1)
    source = initialize_array("input", "source", 1)
    shunt = initialize_array("input", "shunt", 1)
    sym_load = initialize_array("input", "sym_load", 1)
    sym_gen = initialize_array("input", "sym_gen", 1)
    asym_load = initialize_array("input", "asym_load", 1)
    asym_gen = initialize_array("input", "asym_gen", 1)
    sym_voltage_sensor = initialize_array("input", "sym_voltage_sensor", 1)

    asym_voltage_sensor = initialize_array("input", "asym_voltage_sensor", 1)
    asym_voltage_sensor["u_measured"] = [[1.0, np.nan, 2.0]]

    sym_power_sensor = initialize_array("input", "sym_power_sensor", 1)

    asym_power_sensor = initialize_array("input", "asym_power_sensor", 1)
    asym_power_sensor["p_measured"] = [[np.nan, 2.0, 1.0]]
    asym_power_sensor["q_measured"] = [[2.0, 1.0, np.nan]]

    data = {
        "node": node,
        "line": line,
        "link": link,
        "transformer": transformer,
        "source": source,
        "shunt": shunt,
        "sym_load": sym_load,
        "sym_gen": sym_gen,
        "asym_load": asym_load,
        "asym_gen": asym_gen,
        "sym_voltage_sensor": sym_voltage_sensor,
        "asym_voltage_sensor": asym_voltage_sensor,
        "sym_power_sensor": sym_power_sensor,
        "asym_power_sensor": asym_power_sensor,
    }
    required_values_errors = validate_required_values(data=data, calculation_type=calculation_type, symmetric=symmetric)

    pf_dependent = calculation_type == CalculationType.power_flow or calculation_type is None
    se_dependent = calculation_type == CalculationType.state_estimation or calculation_type is None
    asym_dependent = not symmetric

    assert MissingValueError("node", "id", [NaN]) in required_values_errors
    assert MissingValueError("node", "u_rated", [NaN]) in required_values_errors

    assert MissingValueError("line", "id", [NaN]) in required_values_errors
    assert MissingValueError("line", "from_node", [NaN]) in required_values_errors
    assert MissingValueError("line", "to_node", [NaN]) in required_values_errors
    assert MissingValueError("line", "from_status", [NaN]) in required_values_errors
    assert MissingValueError("line", "to_status", [NaN]) in required_values_errors
    assert MissingValueError("line", "r1", [NaN]) in required_values_errors
    assert MissingValueError("line", "x1", [NaN]) in required_values_errors
    assert MissingValueError("line", "c1", [NaN]) in required_values_errors
    assert MissingValueError("line", "tan1", [NaN]) in required_values_errors
    assert MissingValueError("line", "i_n", [NaN]) in required_values_errors
    assert (MissingValueError("line", "r0", [NaN]) in required_values_errors) == asym_dependent
    assert (MissingValueError("line", "x0", [NaN]) in required_values_errors) == asym_dependent
    assert (MissingValueError("line", "c0", [NaN]) in required_values_errors) == asym_dependent
    assert (MissingValueError("line", "tan0", [NaN]) in required_values_errors) == asym_dependent

    assert MissingValueError("link", "id", [NaN]) in required_values_errors
    assert MissingValueError("link", "from_node", [NaN]) in required_values_errors
    assert MissingValueError("link", "to_node", [NaN]) in required_values_errors
    assert MissingValueError("link", "from_status", [NaN]) in required_values_errors
    assert MissingValueError("link", "to_status", [NaN]) in required_values_errors

    assert MissingValueError("transformer", "id", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "from_node", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "to_node", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "from_status", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "to_status", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "u1", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "u2", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "sn", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "uk", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "pk", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "i0", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "p0", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "winding_from", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "winding_to", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "clock", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "tap_side", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "tap_pos", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "tap_min", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "tap_max", [NaN]) in required_values_errors
    assert MissingValueError("transformer", "tap_size", [NaN]) in required_values_errors

    assert MissingValueError("source", "id", [NaN]) in required_values_errors
    assert MissingValueError("source", "node", [NaN]) in required_values_errors
    assert MissingValueError("source", "status", [NaN]) in required_values_errors
    assert (MissingValueError("source", "u_ref", [NaN]) in required_values_errors) == pf_dependent

    assert MissingValueError("shunt", "id", [NaN]) in required_values_errors
    assert MissingValueError("shunt", "node", [NaN]) in required_values_errors
    assert MissingValueError("shunt", "status", [NaN]) in required_values_errors
    assert MissingValueError("shunt", "g1", [NaN]) in required_values_errors
    assert MissingValueError("shunt", "b1", [NaN]) in required_values_errors
    assert (MissingValueError("shunt", "g0", [NaN]) in required_values_errors) == asym_dependent
    assert (MissingValueError("shunt", "b0", [NaN]) in required_values_errors) == asym_dependent

    assert MissingValueError("sym_load", "id", [NaN]) in required_values_errors
    assert MissingValueError("sym_load", "node", [NaN]) in required_values_errors
    assert MissingValueError("sym_load", "status", [NaN]) in required_values_errors
    assert MissingValueError("sym_load", "type", [NaN]) in required_values_errors
    assert (MissingValueError("sym_load", "p_specified", [NaN]) in required_values_errors) == pf_dependent
    assert (MissingValueError("sym_load", "q_specified", [NaN]) in required_values_errors) == pf_dependent

    assert MissingValueError("sym_gen", "id", [NaN]) in required_values_errors
    assert MissingValueError("sym_gen", "node", [NaN]) in required_values_errors
    assert MissingValueError("sym_gen", "status", [NaN]) in required_values_errors
    assert MissingValueError("sym_gen", "type", [NaN]) in required_values_errors
    assert (MissingValueError("sym_gen", "p_specified", [NaN]) in required_values_errors) == pf_dependent
    assert (MissingValueError("sym_gen", "q_specified", [NaN]) in required_values_errors) == pf_dependent

    assert MissingValueError("asym_load", "id", [NaN]) in required_values_errors
    assert MissingValueError("asym_load", "node", [NaN]) in required_values_errors
    assert MissingValueError("asym_load", "status", [NaN]) in required_values_errors
    assert MissingValueError("asym_load", "type", [NaN]) in required_values_errors
    assert (MissingValueError("asym_load", "p_specified", [NaN]) in required_values_errors) == pf_dependent
    assert (MissingValueError("asym_load", "q_specified", [NaN]) in required_values_errors) == pf_dependent

    assert MissingValueError("asym_gen", "id", [NaN]) in required_values_errors
    assert MissingValueError("asym_gen", "node", [NaN]) in required_values_errors
    assert MissingValueError("asym_gen", "status", [NaN]) in required_values_errors
    assert MissingValueError("asym_gen", "type", [NaN]) in required_values_errors
    assert (MissingValueError("asym_gen", "p_specified", [NaN]) in required_values_errors) == pf_dependent
    assert (MissingValueError("asym_gen", "q_specified", [NaN]) in required_values_errors) == pf_dependent

    assert MissingValueError("sym_voltage_sensor", "id", [NaN]) in required_values_errors
    assert MissingValueError("sym_voltage_sensor", "measured_object", [NaN]) in required_values_errors
    assert (MissingValueError("sym_voltage_sensor", "u_sigma", [NaN]) in required_values_errors) == se_dependent
    assert (MissingValueError("sym_voltage_sensor", "u_measured", [NaN]) in required_values_errors) == se_dependent

    assert MissingValueError("asym_voltage_sensor", "id", [NaN]) in required_values_errors
    assert MissingValueError("asym_voltage_sensor", "measured_object", [NaN]) in required_values_errors
    assert (MissingValueError("asym_voltage_sensor", "u_sigma", [NaN]) in required_values_errors) == se_dependent
    assert (MissingValueError("asym_voltage_sensor", "u_measured", [NaN]) in required_values_errors) == se_dependent

    assert MissingValueError("sym_power_sensor", "id", [NaN]) in required_values_errors
    assert MissingValueError("sym_power_sensor", "measured_object", [NaN]) in required_values_errors
    assert MissingValueError("sym_power_sensor", "measured_terminal_type", [NaN]) in required_values_errors
    assert (MissingValueError("sym_power_sensor", "power_sigma", [NaN]) in required_values_errors) == se_dependent
    assert (MissingValueError("sym_power_sensor", "p_measured", [NaN]) in required_values_errors) == se_dependent
    assert (MissingValueError("sym_power_sensor", "q_measured", [NaN]) in required_values_errors) == se_dependent

    assert MissingValueError("asym_power_sensor", "id", [NaN]) in required_values_errors
    assert MissingValueError("asym_power_sensor", "measured_object", [NaN]) in required_values_errors
    assert MissingValueError("asym_power_sensor", "measured_terminal_type", [NaN]) in required_values_errors
    assert (MissingValueError("asym_power_sensor", "power_sigma", [NaN]) in required_values_errors) == se_dependent
    assert (MissingValueError("asym_power_sensor", "p_measured", [NaN]) in required_values_errors) == se_dependent
    assert (MissingValueError("asym_power_sensor", "q_measured", [NaN]) in required_values_errors) == se_dependent


def test_validate_required_values_asym_calculation():
    line = initialize_array("input", "line", 1)
    shunt = initialize_array("input", "shunt", 1)

    data = {"line": line, "shunt": shunt}
    required_values_errors = validate_required_values(data=data, symmetric=False)

    assert MissingValueError("line", "r0", [NaN]) in required_values_errors
    assert MissingValueError("line", "x0", [NaN]) in required_values_errors
    assert MissingValueError("line", "c0", [NaN]) in required_values_errors
    assert MissingValueError("line", "tan0", [NaN]) in required_values_errors

    assert MissingValueError("shunt", "g0", [NaN]) in required_values_errors
    assert MissingValueError("shunt", "b0", [NaN]) in required_values_errors


def test_validate_values():
    # Create invalid nodes and lines
    node = initialize_array("input", "node", 3)
    line = initialize_array("input", "line", 3)

    # Validate nodes and lines individually
    node_errors = validate_values({"node": node})
    line_errors = validate_values({"line": line})

    # Validate nodes and lines combined
    both_errors = validate_values({"node": node, "line": line})

    # The errors should add up (in this simple case)
    assert both_errors == node_errors + line_errors
