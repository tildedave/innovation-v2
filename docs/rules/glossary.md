# Glossary

**Status: skeleton.** One-line, paraphrased working definitions for
vocabulary used elsewhere in `docs/rules/`. Tighten each definition as
the corresponding rule gets implemented -- precise wording belongs in
[overview.md](overview.md) / [actions.md](actions.md), not here.

| Term | Working definition | TODO |
|---|---|---|
| Age | One of the ten eras a card belongs to, roughly corresponding to its deck/difficulty tier. | Confirm age numbering and deck sizes. |
| Meld | Play a card from hand face-up onto your board, on top of its color's pile. | -- |
| Tuck | Place a card at the *bottom* of a color pile instead of melding it on top. | Confirm which effects cause tucking vs. melding. |
| Splay | Shift a color pile so cards underneath the top card are partially visible, exposing their icons. Splay left exposes the bottom-right icon of each covered card; splay right exposes the top-left and bottom-left icons; splay up exposes every icon except top-left (bottom-left, bottom-center, bottom-right). All confirmed; see `engine/board.py`. | -- |
| Score | Move a card to your score pile (face down/counted, not part of your visible board). | Confirm how score-pile value is computed. |
| Draw | Take the top card of a given age from the supply into your hand. | -- |
| Achieve | Claim an achievement card once eligible. | See actions.md. |
| Dogma | Activate the printed effect(s) of a card already on your board. | See actions.md. |
| Share | A non-active player automatically benefits from part of a dogma effect. | Confirm exact trigger condition. |
| Demand | The active player forces non-active players to suffer part of a dogma effect, gated on an icon-count comparison. | Confirm exact trigger condition. |
| Icon | One of the symbols printed in a card's four positions (top-left, bottom-left, bottom-center, bottom-right); icon counts across a player's visible board drive achieve/demand thresholds. | Confirm the icon set (see `model/enums.py`). |
| Special achievement | An achievement earned by satisfying a specific printed condition rather than a score threshold. | Confirm list and conditions. |
