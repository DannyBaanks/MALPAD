# mutable_cell ? input-driven primitive (attempt record)

## GENUINE FINDING (DEMONSTRATED)
A SYNTHESIZED Malbolge program (input_driven.mal = "ub"), produced by Autobolge
relational.synthesize, READS input and its output DEPENDS on that input:
  input "XY" -> "X" ; "AY" -> "A" ; "BY" -> "B"
Verified cross-backend: malbolge-oracle + Malbolge-Engine agree (deterministic).
This demonstrates read_input + emit_event in a synthesized, input-driven program
(not fixed output) ? the first primitive beyond the truth-machine pattern.

## MEMORY PRIMITIVE (mutable_cell): NOT_DEMONSTRATED
Attempted the reverse test (input "AB" -> output "BA", which requires storing the
first input and retrieving it after the second = persistent state). Autobolge
relational.synthesize FAILED (produced only "B"). No program exists that stores a
value across inputs and reproduces it later. This is the honest front of the M3
wall, now confirmed by attempted synthesis, not only by inventory.

## Summary
  read_input / emit_event (input-driven): DEMONSTRATED (synthesized, cross-backend)
  mutable_cell_load / store (memory): NOT_DEMONSTRATED
  BLOCKER CLASS: TOOLING / COMPILATION GAP (not a language-impossibility claim)
