OPENQASM 2.0;
include "qelib1.inc";
gate dcx q0,q1 { cx q0,q1; cx q1,q0; }
qreg q[3];
h q[1];
cx q[1],q[2];
dcx q[0],q[1];
h q[0];
cx q[1],q[2];
cz q[0],q[2];
