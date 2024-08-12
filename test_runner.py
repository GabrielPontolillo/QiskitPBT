# test runner class that receives a list of property classes that inherit from Property
# it needs to generate inputs using he generate_input method,
# then discard the generated inputs if they do not satisfy the preconditions
# and then pass the list of inputs that are generated to the operations method, one by one
# it will then check the postconditions on the circuit that is generated by the operations method
# the test runner
# also needs to receive some options for the number of inputs to generate

# later on we need to allow for the choice of which statistical analysis object to use
from typing import Sequence
from QiskitPBT.property import Property
from QiskitPBT.stats.statistical_analysis_coordinator import StatisticalAnalysisCoordinator, TestExecutionStatistics
from qiskit.providers.basic_provider import BasicSimulator
import random


class TestRunner:
    def __init__(self, property_classes: Sequence[Property.__class__], num_inputs: int, random_seed: int, num_measurements: int, shrinking=False, max_attempts=100):
        self.property_classes = property_classes
        self.num_inputs = num_inputs
        self.do_shrinking = shrinking
        self.max_attempts = max_attempts
        self.num_measurements = num_measurements
        self.property_objects: list[Property] = []
        self.test_execution_stats: TestExecutionStatistics = None
        # keep track of seeds for testing purposes
        self.seeds_list_dict = {}
        random.seed(random_seed)

    # list the failing properties, by looking at the statistical analysis object's assertion outcomes
    def list_failing_properties(self):
        failing_properties = set()

        for failed_property in self.test_execution_stats.failed_property:
            failing_properties.add(failed_property.property.__class__)
    
        return list(failing_properties)

    # list all of the failing inputs for a specific property
    def list_inputs(self, property: Property) -> list[any]:
        return self.seeds_list_dict[tuple(property.get_input_generators())]

    # list all of the passing properties
    def list_passing_properties(self):
        # calculate the failing properties and then return the set difference of the property classes
        # and the failing properties
        return [prop for prop in self.property_classes if prop not in self.list_failing_properties()]

    def run_tests(self, backend=BasicSimulator(), run_optimization=True, family_wise_p_value=0.01):
        # for each property class, we need to create a statistical analysis object
        # and then create a property object using the statistical analysis object
        stat_analysis_coordinator = StatisticalAnalysisCoordinator(self.num_measurements, family_wise_p_value)
        properties = []

        # needs to be sorted to ensure reproducibility, otherwise different seeds will be generated if random order
        for property in sorted(self.property_classes, key=lambda x: x.__name__):
            # instantiate the property with statistical analysis object
            property_obj = property()
            properties.append(property_obj)
            property_obj.statistical_analysis = stat_analysis_coordinator
            self.property_objects.append(property_obj)

            seeds_set = set()

            # get the input generators (moved out of loop because we only need to retrieve them once)
            input_generators = property_obj.get_input_generators()

            # index to keep track of which seeds have been attempted to be reused
            reuse_index = 0

            # begin generation
            for _ in range(self.num_inputs):
                for attempt_idx in range(self.max_attempts):
                    # keep track of whether we have reused a set of seeds
                    reused = False

                    # have we previously seen the same combination of input generators and preconditions?
                    if self.seeds_list_dict.get(tuple(input_generators), None) is not None:
                        # retrieve all previously used sets of seeds for the same input generators
                        seeds_list = self.seeds_list_dict[tuple(input_generators)]

                        # attempt to reuse seed
                        if reuse_index < len(seeds_list):
                            seeds = seeds_list[reuse_index]
                            reuse_index += 1
                            reused = True
                        else:
                            # we have used all previously generated seeds, we need to generate new seeds
                            seeds = tuple(random.randint(0, 2**31-1) for _ in input_generators)
                    else:
                        # if we have not previously seen this exact set of input generators
                        # generate new seeds
                        seeds = tuple(random.randint(0, 2**31-1) for _ in input_generators)

                    inputs = [generator.generate(seeds[i]) for i, generator in enumerate(input_generators)]

                    # check the preconditions
                    if property_obj.preconditions(*inputs) and seeds not in seeds_set:
                        seeds_set.add(seeds)
                        if tuple(input_generators) not in self.seeds_list_dict:
                            self.seeds_list_dict[tuple(input_generators)] = [seeds]
                        elif not reused:
                            # only add this seed if it was not reused
                            self.seeds_list_dict[tuple(input_generators)].append(seeds)
                        break

                    if attempt_idx == self.max_attempts - 1:
                        print("Precondition could not be respected for property: ", property, " after ", self.max_attempts, " attempts")
                        print("Skipping statistical analysis for this property")
                        property_obj.classical_assertion_outcome = False

                # add the generated inputs to the statistical analysis object of the property
                # what if each property has its own statistical analysis object?
                # and the assertions were only stored in the statistical analysis object for the specific property
                # property_obj.statistical_analysis.inputs.append(inputs)

                try:
                    # run the operations method
                    property_obj.operations(*inputs)
                except AssertionError as e:
                    print("Classical assertion failed within property: ", property)
                    print("AssertionError: ", e)
                    print("Skipping statistical analysis for this property")
                    property_obj.classical_assertion_outcome = False
        self.test_execution_stats = stat_analysis_coordinator.perform_analysis(properties, backend, run_optimization)
        return self.test_execution_stats
