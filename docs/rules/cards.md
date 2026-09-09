# Card data

**Status: two cards entered, both with tested dogma effects.** This
file tracks progress on populating
[cards/registry.py](../../src/innovation/cards/registry.py) card by
card, age by age.

## Adding a card

For each card, two things need to exist and can be done as separate
steps (see [architecture.md](architecture.md)):

1. **Data**: name, age, color, and the four corner icons, entered into
   the registry.
2. **Behavior**: the dogma effect(s) implemented in
   [engine/actions.py](../../src/innovation/engine/actions.py) (or
   wherever the effect system ends up living), plus tests that exercise
   the exact rules-text scenario.

A card isn't "done" until both exist and are tested; track partial
progress explicitly rather than leaving it ambiguous.

## Progress by age

| Age | Cards entered | Cards with tested dogma |
|---|---|---|
| 1 | 2 / ? (Sailing, Metalworking) | 2 / ? |
| 2 | 0 / ? | 0 / ? |
| 3 | 0 / ? | 0 / ? |
| 4 | 0 / ? | 0 / ? |
| 5 | 0 / ? | 0 / ? |
| 6 | 0 / ? | 0 / ? |
| 7 | 0 / ? | 0 / ? |
| 8 | 0 / ? | 0 / ? |
| 9 | 0 / ? | 0 / ? |
| 10 | 0 / ? | 0 / ? |

TODO: fill in the `?` denominators (cards per age) from the box/rulebook,
and note here whether special achievements or any expansion content
(beyond the base 4th-edition set) are in scope.
