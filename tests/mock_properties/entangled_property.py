# class that inherits from property based test
from qiskit import QuantumCircuit
from QiskitPBT.property import Property
from QiskitPBT.input_generators import RandomState


class EntangledPrecondition(Property):
    # specify the inputs that are to be generated
    def get_input_generators(self):
        # The assumption of our code is that we need at least one input generator, if we do not include it,
        # the code breaks in the test runner - also its a fine assumption to include, property based testing requires inputs
        return [RandomState(2)]

    # specify the preconditions for the test
    def preconditions(self, mock):
        return True

    # specify the operations to be performed on the input
    def operations(self, mock):
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        # TODO: for some reason this does not work on y basis
        self.statistical_analysis.assert_entangled(self, [0, 1], qc, basis=["x", "y", "z"])
