from QiskitPBT.case_studies.quantum_phase_estimation.lower_register_unchanged_by_eigenvector_property import LowerRegisterUnchangedByEigenvector
from QiskitPBT.case_studies.quantum_phase_estimation.phase_estimation_on_sum_of_eigenvectors_property import PhaseEstimationSumEigenvectors
from QiskitPBT.case_studies.quantum_phase_estimation.phase_estimation_on_sum_of_different_eigenvectors_property import PhaseEstimationSumDifferentEigenvectors
from QiskitPBT.case_studies.quantum_phase_estimation.phase_correctly_estimated_with_enough_qubits_property import PhaseCorrectlyEstimatedEnoughQubits
from QiskitPBT.test_runner import TestRunner

import unittest


# test the identity property
class TestQPEProperties(unittest.TestCase):
    def setUp(self):
        self.num_inputs = 5

    def test_eigenvector_property(self):
        # run the test
        runner = TestRunner([LowerRegisterUnchangedByEigenvector], self.num_inputs, 101, 1500)
        runner.run_tests()
        # the property should pass
        assert runner.list_failing_properties() == []
        assert runner.list_passing_properties() == [LowerRegisterUnchangedByEigenvector]

    def test_sum_eigenvector_property(self):
        # run the test
        runner = TestRunner([PhaseEstimationSumEigenvectors], self.num_inputs, 102, 1500)
        runner.run_tests()
        # the property should pass
        assert runner.list_failing_properties() == []
        assert runner.list_passing_properties() == [PhaseEstimationSumEigenvectors]

    def test_sum_eigenvector_different_eigenvalues_property(self):
        # run the test
        runner = TestRunner([PhaseEstimationSumDifferentEigenvectors], self.num_inputs, 102, 1500)
        runner.run_tests()
        # the property should pass
        assert runner.list_failing_properties() == []
        assert runner.list_passing_properties() == [PhaseEstimationSumDifferentEigenvectors]

    def test_phase_correctly_estimated_with_enough_qubits(self):
        # run the test
        runner = TestRunner([PhaseCorrectlyEstimatedEnoughQubits], self.num_inputs, 106, 1500)
        runner.run_tests()
        # the property should pass
        assert runner.list_failing_properties() == []
        assert runner.list_passing_properties() == [PhaseCorrectlyEstimatedEnoughQubits]
