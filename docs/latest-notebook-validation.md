# Latest Jupyter relocation validation

Notebook 09 ran in a temporary copied project using a new kernel and the existing Python dependencies. No training notebook ran. The source notebook and active notebook 08 were unchanged.

- Engine fingerprint: `1cf36f08bcdf85f8e2f281bd65f0273fcb5118464b27b78f168201858239ab51`
- Notebook SHA-256: `f0fa3b630c4a75e77d67781c53185482036168a69b8ec52a12fb6817fd2d6cca`
- All 11 classes exercised in 11 games.
- 11 terminal games, 0 errors, 0 action cutoffs; limit 500 actions per game.
- 1422 learning-feature decisions checked.
- Receipt: `runs/relocation_checks/e7dce8b2e9054a4cac8e2b3136d92e61/receipt.json`
- Executed notebook: `runs/relocation_checks/e7dce8b2e9054a4cac8e2b3136d92e61/executed.ipynb`

This establishes that the copied project layout, data link and bounded validation notebook work with the installed dependencies. It does not establish a clean dependency installation, all-card coverage, rule conformance, learning quality or optimal decks. The implementation pool remains 498 of 1185 cards.
