# class for generating random statevectors using Qiskit, the generator method receives the dimensions of the statevector
from qiskit.quantum_info import random_statevector
from input_generators.input_generator import InputGenerator


class QiskitUniformStatevector(InputGenerator):
    def __init__(self, number_of_qubits):
        self.number_of_qubits = number_of_qubits

    def generate(self):
        # generate a random statevector
        return random_statevector(2 ** self.number_of_qubits).data
