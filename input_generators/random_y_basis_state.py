# class for generating random statevectors using Qiskit, the generator method receives the dimensions of the statevector
from input_generators.input_generator import InputGenerator
from qiskit.quantum_info import Statevector
import random


class RandomYBasisState(InputGenerator):
    def __init__(self, number_of_qubits):
        self.number_of_qubits = number_of_qubits

    def generate(self):
        # generate a random statevector from the tensor product of the |r>,|l>
        # loop through the number of qubits, choose one of the 2 statevectors
        state_string = ""
        for i in range(self.number_of_qubits):
            state = random.randint(0, 1)
            if state == 0:
                state_string += "r"
            elif state == 1:
                state_string += "l"

        # convert the string to a statevector
        return Statevector.from_label(state_string).data