"""Rules engine: turn structure, actions, and state transitions.

This is where game rules actually get enforced. ``innovation.model``
only defines data shapes; this package is the only place that should
mutate a ``GameState`` according to the rules.
"""
