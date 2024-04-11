# class that inherits from property based test
import numpy as np
from qiskit import QuantumCircuit
from property import Property
from input_generators import RandomPauliBasisState
from .quantum_fourier_transform import qft_general


class LinearShiftToPhaseShift(Property):
    # specify the inputs that are to be generated
    def generate_input(self):
        state = RandomPauliBasisState(1, 5, ["z"])
        return [state]

    # specify the preconditions for the test
    def preconditions(self, state):
        return True

    # specify the operations to be performed on the input
    def operations(self, state):
        n = state.num_qubits

        qft_1 = QuantumCircuit(n)
        qft_1.initialize(state, reversed(range(n)))
        qft_1 = qft_1.compose(qft_general(n, swap=False))
        qft_1 = phase_shift(qft_1)

        init_state = state.data
        # make the first element the last element, and vice versa
        shifted_vector = np.roll(init_state, -1)

        qft_2 = QuantumCircuit(n)
        qft_2.initialize(shifted_vector, reversed(range(n)))
        qft_2 = qft_2.compose(qft_general(n, swap=False))

        self.statistical_analysis.assert_equal(qft_1, list(range(n)), qft_2, list(range(n)))


def phase_shift(qc):
    for i in range(qc.num_qubits):
        qc.p(-np.pi / 2 ** (qc.num_qubits - 1 - i), i)
    return qc
