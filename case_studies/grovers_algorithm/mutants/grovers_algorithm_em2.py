from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli


# returns grover's algorithm on the provided oracle
def grovers_algorithm(grover_oracle: QuantumCircuit, iterations: int):

    num_qubits = grover_oracle.num_qubits

    grover_qc = QuantumCircuit(num_qubits, num_qubits)

    # initialise lower register to |1>
    grover_qc.x(num_qubits - 1)

    # initialise superposition to get |++....++>|->
    grover_qc.h(range(num_qubits))

    grover_qc.barrier()

    # apply the oracle and reflection about the mean
    for i in range(iterations):
        # semantic preserving changes loc 3, gates 11, index 0
        grover_qc.z(0)
        grover_qc.x(0)
        grover_qc.append(Pauli('iY'), [0])

        grover_qc.compose(grover_oracle, range(num_qubits), inplace=True)

        grover_qc.barrier()

        # reflection about the mean
        grover_qc.h(range(num_qubits - 1))
        grover_qc.x(range(num_qubits - 1))
        grover_qc.h(num_qubits - 2)
        grover_qc.mcx(list(range(num_qubits - 2)), num_qubits - 2)
        grover_qc.h(num_qubits - 2)
        grover_qc.x(range(num_qubits - 1))
        grover_qc.h(range(num_qubits - 1))

        grover_qc.barrier()

    return grover_qc
