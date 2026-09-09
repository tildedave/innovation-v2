"""Rules engine: turn structure, actions, and state transitions.

This is where game rules actually get enforced. ``innovation.model``
only defines data shapes -- all of them immutable; this package is the
only place that should apply the rules, and it does so by returning a
new ``GameState`` (or ``PlayerState``) rather than mutating one.
"""
