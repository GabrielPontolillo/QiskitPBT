# test runner class that receives a list of property classes that inherit from Property
# it needs to generate inputs using he generate_input method,
# then discard the generated inputs if they do not satisfy the preconditions
# and then pass the list of inputs that are generated to the operations method, one by one
# it will then check the postconditions on the circuit that is generated by the operations method
# the test runner
# also needs to receive some options for the number of inputs to generate

#later on we need to allow for the choice of which statistical analysis object to use
from stats.single_qubit_distributions.single_qubit_statistical_analysis import SingleQubitStatisticalAnalysis
from stats.assertion_def import AssertionDef
import random

MAX_ATTEMPTS = 100

class TestRunner:
    property_objects = []
    generated_seeds = []

    def __init__(self, property_classes, num_inputs, random_seed, shrinking=False):
        self.property_classes = property_classes
        self.num_inputs = num_inputs
        self.do_shrinking = shrinking
        random.seed(random_seed)


    # list all of the failing properties, by looking at the statistical analysis object's assertions's outcomes
    def list_failing_properties(self):
        failing_properties = []

        # assertions are a static variable, so we only need to get one assertion object
        property = self.property_objects[0]

        # get the failing properties by checking the assertions from the statistical analysis object
        for assertion in property.statistical_analysis.assertions:
            if not assertion.outcome:
                failing_properties.append(assertion.property_class)

        # get the failing properties by checking the classical assertion outcome
        for prop in self.property_objects:
            if not prop.classical_assertion_outcome:
                failing_properties.append(prop)

        return list(set(failing_properties))

    # list all of the failing inputs for a specific property
    def list_failing_inputs(self, property):
        # iterate through all assertions within the property's statistical analysis object
        # if they failed, get the index of the input that failed in the inputs list of the statistical analysis object
        # and add it to the failing inputs list
        failing_inputs = []

        for assertion in property.statistical_analysis.assertions:
            if not assertion.outcome:
                failing_inputs.append(property.statistical_analysis.inputs[assertion.input_index])

        return failing_inputs

    # list all of the passing properties
    def list_passing_properties(self):
        # calculate the failing properties and then return the set difference of the property classes
        # and the failing properties
        failing_properties = self.list_failing_properties()

        # calculate the set defference
        passing_properties = [prop for prop in self.property_classes if prop not in failing_properties]

        return passing_properties

    def run_tests(self):
        # for each property class, we need to create a statistical analysis object
        # and then create a property object using the statistical analysis object
        for property in self.property_classes:
            print("===========\nEvaluating property: ", property, "\n===========")
            # instantiate the property with statistical analysis object
            stat = SingleQubitStatisticalAnalysis(property, property.generate_input)
            property_obj = property(stat)
            self.property_objects.append(property_obj)

            # generate inputs
            for i in range(self.num_inputs):
                # get the input generators
                input_generators = property_obj.generate_input()

                # call generate using all of the generators provided
                inputs = [x for x in range(len(input_generators))]

                for attempt_idx in range(MAX_ATTEMPTS):
                    print("Attempt: ", attempt_idx)
                    for i, generator in enumerate(input_generators):
                        # 2,147,483,647 is the maximum value for the seed, 2^31 - 1, the maximum value for a 32 bit signed integer
                        local_seed = random.randint(0, 2147483647)
                        print(local_seed)
                        self.generated_seeds.append(local_seed)
                        inputs[i] = generator.generate(local_seed)

                    # check the preconditions
                    if property_obj.preconditions(*inputs):
                        break

                    if attempt_idx == MAX_ATTEMPTS - 1:
                        print("Precondition could not be respected for property: ", property, " after ", MAX_ATTEMPTS, " attempts")
                        print("Skipping statistical analysis for this property")
                        property_obj.classical_assertion_outcome = False


                print("Inputs", inputs)

                # add the generated inputs to the statistical analysis object of the property
                # what if each property has its own statistical analysis object?
                # and the assertions were only stored in the statistical analysis object for the specific property
                # property_obj.statistical_analysis.inputs.append(inputs)
                stat.inputs.append(inputs)

                try:
                    # run the operations method
                    circuit = property_obj.operations(*inputs)
                except AssertionError as e:
                    print("Classical assertion failed within property: ", property)
                    print("AssertionError: ", e)
                    print("Skipping statistical analysis for this property")
                    property_obj.classical_assertion_outcome = False

        property_obj.statistical_analysis.perform_analysis()

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





