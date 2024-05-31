# class that inherits from property based test
from qiskit import QuantumCircuit
import numpy as np
from qiskit.circuit.library import UnitaryGate
from qiskit.quantum_info import Operator, Statevector
from QiskitPBT.property import Property
from QiskitPBT.input_generators import RandomEigenvectorUnitaryPair, RandomUnitary, Integer
from QiskitPBT.case_studies.quantum_phase_estimation.quantum_phase_estimation import qpe_general


class PhaseEstimationSumDifferentEigenvectors(Property):
    # specify the inputs that are to be generated
    def get_input_generators(self):
        eigenvector_unitary_pair = RandomEigenvectorUnitaryPair(RandomUnitary(1, 2), 2)
        estimation_qubits = Integer(1, 3)
        return [eigenvector_unitary_pair, estimation_qubits]

    # specify the preconditions for the test
    def preconditions(self, eigenvector_unitary_pair, estimation_qubits):
        # check that the eigenvectors have the same eigenvalue

        # make sure that the eigenvectors have different enough eigenvalues, such that we can pick it up in measurements
        return abs(eigenvector_unitary_pair[0][0][1] - eigenvector_unitary_pair[0][1][1]) > 0.05

    # specify the operations to be performed on the input
    def operations(self, eigenvector_unitary_pair, estimation_qubits):
        eigenvectors, unitary = eigenvector_unitary_pair

        for eigenvector, eigenvalue in eigenvectors:
            print(eigenvalue)

        n = unitary.num_qubits

        # perform qpe on with an eigenvector in lower register
        qpe = qpe_general(estimation_qubits, UnitaryGate(unitary), eigenvectors[0][0])

        # sum of eigenvectors, then normalize
        normalized_sum_eigenvectors = (eigenvectors[0][0] + eigenvectors[1][0]) / np.sqrt(2)
        qpe2 = qpe_general(estimation_qubits, UnitaryGate(unitary), normalized_sum_eigenvectors)

        print(qpe)
        print(qpe2)

        # TODO: need to assert different
        self.statistical_analysis.assert_equal(list(range(estimation_qubits)), qpe,
                                               list(range(estimation_qubits)), qpe2)
