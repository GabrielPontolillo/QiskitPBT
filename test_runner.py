# test runner class that receives a list of property classes that inherit from Property
# it needs to generate inputs using he generate_input method,
# then discard the generated inputs if they do not satisfy the preconditions
# and then pass the list of inputs that are generated to the operations method, one by one
# it will then check the postconditions on the circuit that is generated by the operations method
# the test runner
# also needs to receive some options for the number of inputs to generate

#later on we need to allow for the choice of which statistical analysis object to use
from typing import Sequence
from property import Property
from stats.statistical_analysis_coordinator import StatisticalAnalysisCoordinator
from qiskit.providers.basic_provider import BasicSimulator
import random

class TestRunner:
    property_objects: list[Property] = []

    def __init__(self, property_classes: Sequence[Property.__class__], num_inputs: int, random_seed: int, shrinking=False, max_attempts=100):
        self.property_classes = property_classes
        self.num_inputs = num_inputs
        self.do_shrinking = shrinking
        self.max_attempts = max_attempts
        random.seed(random_seed)


    # list all of the failing properties, by looking at the statistical analysis object's assertions's outcomes
    def list_failing_properties(self):
        failing_properties = []

        for property in self.property_objects:
            for outcome in property.statistical_analysis.results:
                if not outcome:
                    failing_properties.append(property.__class__)
                    break
    
        return failing_properties

    # list all of the failing inputs for a specific property
    def list_failing_inputs(self, property: Property) -> list[list[any]]:
        # iterate through all assertions within the property's statistical analysis object
        # if they failed, get the index of the input that failed in the inputs list of the statistical analysis object
        # and add it to the failing inputs list
        failing_inputs = [[] for _ in property.statistical_analysis.assertions]

        for i in range(len(property.statistical_analysis.assertions)):
            if not property.statistical_analysis.results[i]:
                failing_inputs[i] = property.statistical_analysis.assertions[i].failing_inputs

        return failing_inputs

    # list all of the passing properties
    def list_passing_properties(self):
        # calculate the failing properties and then return the set difference of the property classes
        # and the failing properties
        return [prop for prop in self.property_classes if prop not in self.list_failing_properties()]

    def run_tests(self, backend=BasicSimulator(), measurements=2000, family_wise_p_value=0.05):
        # for each property class, we need to create a statistical analysis object
        # and then create a property object using the statistical analysis object
        for property in self.property_classes:
            #print("===========")
            #print("Evaluating property: ", property)
            #print("===========")
            # instantiate the property with statistical analysis object
            property_obj = property()
            stat = StatisticalAnalysisCoordinator(property_obj, measurements, family_wise_p_value)
            property_obj.statistical_analysis = stat
            self.property_objects.append(property_obj)

            seeds = set()
            # generate inputs
            for _ in range(self.num_inputs):
                # get the input generators
                input_generators = property_obj.get_input_generators()

                for attempt_idx in range(self.max_attempts):
                    #print("Attempt: ", attempt_idx)
                    seed = random.randint(0, 2**31-1)
                    #print(local_seed)
                    inputs = [generator.generate(seed) for generator in input_generators]
                    # check the preconditions
                    if property_obj.preconditions(*inputs) and seed not in seeds:
                        seeds.add(seed)
                        break 

                    if attempt_idx == self.max_attempts - 1:
                        print("Precondition could not be respected for property: ", property, " after ", self.max_attempts, " attempts")
                        print("Skipping statistical analysis for this property")
                        property_obj.classical_assertion_outcome = False

                # print("Inputs", inputs)

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

            property_obj.statistical_analysis.perform_analysis(seeds, backend)

        if self.do_shrinking:
            self.shrinking()

    def shrinking(self):
        # now we need to implement shrinking
        # if any properties failed, we need to shrink the inputs that were failing
        # we will only try to shrink one failing input, if multiple inputs are failing for a property

        # get the failing properties
        failing_properties = self.list_failing_properties()

        # what if we have a hierarchy of input generators, we test one example from each generator to see if it still passes or fails, then try to minimise within that
        # if we pass the property operation to the shrink function?
        # here is the thing, we need to also have an efficient description of the minimised state, so we can use it in the future (a bit string)
        # not just the literal statevector





