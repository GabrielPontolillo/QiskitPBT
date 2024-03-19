# statistical analysis class that is passed in the initialisation of each property based test
# it is used to call statistical assertions on the circuits that are generated
# it is also used to identify what measurements to make in order to perform the least number of measurements
# it stores the results of the measurements in a dictionary with the hash of the circuit and hashed input generation
# function as he key
# the class stores assertions that are made on the circuits as a wrapper, and the inputs to the assertion to identify what measurements to make
# these functions are called later by the perform_analysis function which will be called by the test runner in order to apply family wise error rate correction at the end
# perform_measurements function will perform the identified measurements and store the results in the dictionary
from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.providers.basic_provider import BasicSimulator
from case_studies.stats.assertion_def import AssertionDef
from case_studies.stats.single_qubit_distributions.assert_equal import AssertEqual


class SingleQubitStatisticalAnalysis:
    # probably move these static variables to assertion def, as well as the perform_analysis function
    assertions = []
    unique_circuits = []
    union_of_qubits = []
    outcomes = []

    def __init__(self, property_class, input_function_hash, number_of_measurements=2000):
        self.property_class = property_class
        self.input_function_hash = input_function_hash
        self.number_of_measurements = number_of_measurements

        # store the inputs that are generated by the test runner
        self.inputs = []

    # perform the analysis on the measurements that have been made and stored in the dictionary
    def perform_analysis(self):
        self.perform_measurements()

        for assertion in self.assertions:
            # need to pass in the two respective measurement dictionaries to the assertion
            assertion.calculate_p_values(self.outcomes, self.unique_circuits, self.union_of_qubits)

        # perform family wise error rate correction
        holm_bonferroni_correction(self.assertions, 0.05)

        # calculate the outcome of each assertion
        for assertion in self.assertions:
            assertion.calculate_outcome()

    # needs to identify qubit index overlap in assertions with the same input function hash, and them perform the least number of measurements
    def perform_measurements(self):
        # we need to get a list containing of unique circuits,
        # and a list with union of the qubits to measure for all identical circuits in the list
        # we can then perform the least number of measurements on these qubits
        self.unique_circuits = []
        self.union_of_qubits = []
        # outcomes is a list of dicts, with the key as the qubit that was measurement, and the values as a triple, containing the x,y,z outcomes
        self.outcomes = []
        for assertion in self.assertions:
            for circuit, indexes in assertion.circuits_and_indexes_to_measure:
                if circuit in self.unique_circuits:
                    index = self.unique_circuits.index(circuit)
                    self.union_of_qubits[index] = list(set(self.union_of_qubits[index] + indexes))
                else:
                    self.unique_circuits.append(circuit)
                    self.union_of_qubits.append(indexes)

        # measure the x, y, and z basis components of the qubits in each unique circuit
        for index, circuit in enumerate(self.unique_circuits):
            self.outcomes.append(
                measure_qubits(circuit.copy(), self.union_of_qubits[index], self.number_of_measurements))

    # wrapper for assert equal that calls add assertion to store it for future use
    # can pass in a string, or a circuit with qubits to assert equality of.
    def assert_equal(self, state1: str | QuantumCircuit,
                     qubits1: list[int],
                     state2: str | QuantumCircuit,
                     qubits2: list[int]):

        self.assertions.append(
            AssertEqual(self.property_class,
                        [(state1, qubits1), (state2, qubits2)],
                        [state1, qubits1, state2, qubits2],
                        len(self.inputs)-1)
        )


def measure_y(circuit, qubit_indexes):
    control_bit_index = 0
    for index in qubit_indexes:
        circuit.sdg(index)
        circuit.h(index)
        circuit.measure(index, control_bit_index)
        control_bit_index += 1
    return circuit


def measure_z(circuit, qubit_indexes):
    control_bit_index = 0
    for index in qubit_indexes:
        circuit.measure(index, control_bit_index)
        control_bit_index += 1
    return circuit


def measure_x(circuit, qubit_indexes):
    control_bit_index = 0
    for index in qubit_indexes:
        circuit.h(index)
        circuit.measure(index, control_bit_index)
        control_bit_index += 1
    return circuit


def measure_qubits(circuit_1, register, measurements=1000, basis=None):
    # receives a circuit to measure, and a list of qubit registers to measure
    # returns a list of measurements for respective qubits
    backend = BasicSimulator()

    if basis is None:
        basis = ['x', 'y', 'z']

    results = {}
    circuit_1.add_register(ClassicalRegister(len(register)))

    if 'z' in basis:
        c1z = measure_z(circuit_1.copy(), register)
        z_counts_1 = backend.run(transpile(c1z, backend), shots=measurements).result().get_counts()

    if 'x' in basis:
        c1x = measure_x(circuit_1.copy(), register)
        x_counts_1 = backend.run(transpile(c1x, backend), shots=measurements).result().get_counts()

    if 'y' in basis:
        c1y = measure_y(circuit_1, register)
        y_counts_1 = backend.run(transpile(c1y, backend), shots=measurements).result().get_counts()

    for i in range(len(register)):
        res_dict = {}

        if 'x' in basis:
            x1 = sum([v for (k, v) in x_counts_1.items() if k[-(i + 1)] == '1'])
            x0 = measurements - x1
            res_dict["x0"] = x0
            res_dict["x1"] = x1

        if 'y' in basis:
            y1 = sum([v for (k, v) in y_counts_1.items() if k[-(i + 1)] == '1'])
            y0 = measurements - y1
            res_dict["y0"] = y0
            res_dict["y1"] = y1

        if 'z' in basis:
            z1 = sum([v for (k, v) in z_counts_1.items() if k[-(i + 1)] == '1'])
            z0 = measurements - z1
            res_dict["z0"] = z0
            res_dict["z1"] = z1

        # add res_dict to the output dictionary with the register index as its key
        results[register[i]] = res_dict
    return results


# need a Holm Bonferroni correction function that receives a list of p-values and returns a list of p-values to compare them to
# Ideally, we need to sort all of the p-values from all assertions, then pass back the corrected alpha values to compare them to in a list
def holm_bonferroni_correction(assertion_list: list[AssertionDef], family_wise_alpha=0.05):
    p_vals = []
    for assertion_index, assertion in enumerate(assertion_list):
        for p_value_index, p_val in enumerate(assertion.p_vals):
            p_vals.append([assertion_index, p_value_index, p_val, None])

    # sort by p_val ascending order
    p_vals.sort(key=lambda x: x[2])
    for i, p_val in enumerate(p_vals):
        p_val[3] = (family_wise_alpha / (len(p_vals) - i))

    # sort by first then second index
    p_vals.sort(key=lambda x: (x[0], x[1]))

    # place back into the format of the original assertion list, so for each assertion, we have a list of alpha values to compare to
    for i, assertion in enumerate(assertion_list):
        assertion.expected_p_vals = [x[3] for x in p_vals if x[0] == i]