OPENQASM 2.0;
include "qelib1.inc";
gate iX q0 { x q0; }
qreg q[5];
creg c[5];
y q[0];
z q[0];
iX q[0];
h q[0];
cp(pi/2) q[1],q[0];
cp(pi/4) q[2],q[0];
cp(pi/8) q[3],q[0];
cp(pi/16) q[4],q[0];
y q[0];
z q[0];
iX q[0];
h q[1];
cp(pi/2) q[2],q[1];
cp(pi/4) q[3],q[1];
cp(pi/8) q[4],q[1];
y q[0];
z q[0];
iX q[0];
h q[2];
cp(pi/2) q[3],q[2];
cp(pi/4) q[4],q[2];
y q[0];
z q[0];
iX q[0];
h q[3];
cp(pi/2) q[4],q[3];
y q[0];
z q[0];
iX q[0];
h q[4];
swap q[0],q[4];
swap q[1],q[3];
