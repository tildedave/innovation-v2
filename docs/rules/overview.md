# Rules overview

**Status: skeleton.** This is a section outline to fill in from the
official 4th-edition rulebook, not a substitute for it -- exact
wording matters for a rules engine, so treat every line below as a
`TODO` unless noted otherwise. Don't transcribe the rulebook text
verbatim into this repo; paraphrase into whatever precision the engine
implementation actually needs.

## Overview (high level, non-authoritative)

Innovation is a card game for 2+ players about advancing a set of
technologies/ideas through ten "ages," represented by ten decks of
cards. Each player builds their own tableau by melding cards in front
of them, organized into color-coded piles. Cards' printed icons and
"dogma" effects interact with what's in a player's tableau (and
sometimes other players' tableaus) to let players draw more cards,
manipulate piles, or score points. See [glossary.md](glossary.md) for
the vocabulary used throughout these docs.

## TODO: Setup

- Number of players supported, and any per-player-count variants.
- Initial deck/supply arrangement (ages 1-10).
- Starting hand size, starting achievements pool, first-player
  determination.

## TODO: Turn structure

- What "your turn" consists of (how many actions, of which kinds).
- The four actions: Draw, Meld, Achieve, Dogma -- see
  [actions.md](actions.md) for per-action detail to fill in.

## TODO: Winning the game

- The achievement-count win condition (how many achievements needed,
  does it vary with player count).
- Special achievements and how they're earned.
- Any other end-of-game trigger (e.g. running out of a needed age's
  supply).

## TODO: Edge cases and clarifications

Track rules-as-written ambiguities and their resolutions here as
they're discovered while implementing card dogma effects, with a
reference back to the card that raised the question.
