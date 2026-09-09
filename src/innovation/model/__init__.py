"""Data model: the immutable, plain-data types that describe cards and
game state.

Every type here is frozen. Nothing in this package enforces a rule or
produces a new state -- it only defines the shapes. Rule enforcement
and state transitions (each returning a new state rather than
mutating) live in ``innovation.engine``.
"""
