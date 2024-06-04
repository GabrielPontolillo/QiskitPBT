# class that inherits from property based test
from qiskit import QuantumCircuit
import numpy as np
from qiskit.circuit.library import UnitaryGate
from QiskitPBT.property import Property
from QiskitPBT.input_generators import RandomEigenvectorUnitaryPair, RandomUnitary, Integer
from QiskitPBT.case_studies.quantum_phase_estimation.quantum_phase_estimation import qpe_general


class LowerRegisterUnchangedByEigenvector(Property):
    # specify the inputs that are to be generated
    def get_input_generators(self):
        eigenvector_unitary_pair = RandomEigenvectorUnitaryPair(RandomUnitary(1, 2), 1)
        estimation_qubits = Integer(1, 3)
        return [eigenvector_unitary_pair, estimation_qubits]

    # specify the preconditions for the test
    def preconditions(self, eigenvector_unitary_pair, estimation_qubits):
        return True

    # specify the operations to be performed on the input
    def operations(self, eigenvector_unitary_pair, estimation_qubits):
        eigenvectors, unitary = eigenvector_unitary_pair

        n = unitary.num_qubits

        # perform qpe on with an eigenvector in lower register
        qpe = qpe_general(estimation_qubits, UnitaryGate(unitary), eigenvectors[0][0])

        # state should be the unchanged eigenvector
        qpe2 = QuantumCircuit(n, n)
        qpe2.initialize(eigenvectors[0][0], list(range(n)))

        self.statistical_analysis.assert_equal(list(range(estimation_qubits, estimation_qubits+unitary.num_qubits)), qpe, list(range(n)), qpe2)