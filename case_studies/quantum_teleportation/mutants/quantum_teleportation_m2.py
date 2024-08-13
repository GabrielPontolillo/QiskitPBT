from qiskit import QuantumCircuit


# returns the quantum_teleportation circuit
def quantum_teleportation():
    qc = QuantumCircuit(3)
    qc.sx(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)


    qc.cx(1, 2)
    qc.cz(0, 2)
    return qc

