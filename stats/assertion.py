from typing import Sequence

from abc import ABC, abstractmethod

from stats.measurement_configuration import MeasurementConfiguration
from stats.measurements import Measurements


class Assertion(ABC):
    """super class of each assertion
    """
    failing_inputs = []
    @abstractmethod
    def calculate_p_values(self, measurements: Measurements) -> list[float]:
        """calculate p values for the assertion

        Args:
            measurements (Measurements): measurement outcomes
        Returns:
            list[float]: list of p values for this assertion
        """
        pass

    @abstractmethod
    def calculate_outcome(self, p_values: Sequence[float], expected_p_values: Sequence[float]) -> bool:
        """determine if assertion is true or not based on p values provided

        Args:
            p_values (Sequence[float]): sequence of p values, computed by calculate_p_values
            expected_p_values (Sequence[float]): sequence of p values, that is expected by statistics engine for the assertion to pass (respectively for each value in p_values)

        Returns:
            bool: true if assertion passed, false otherwise
        """
        pass

    @abstractmethod
    def get_measurement_configuration(self) -> MeasurementConfiguration:
        """get object containing information about which measurements to perform on which qubits

        Returns:
            MeasurementConfiguration: object containing information about which measurements to perform
        """
        pass
    
    @abstractmethod
    def __eq__(self, value: object) -> bool:
        pass