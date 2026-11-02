# Daily Puzzle Hub

A mobile-first, spoiler-safe answer dashboard for 13 daily games: **Wordle, Strands, Crosswordle, Mathler, Sumplete**, plus all eight current LinkedIn games (**Pinpoint, Crossclimb, Queens, Tango, Zip, Mini Sudoku, Patches, Wend**).

## What works right now

- A complete front-end: category navigation, responsive game cards, search, date picker, previous/next day, favourite games (stored locally), light/dark modes, hints, individual spoiler reveals, and direct links to play.
- **Sunday 1 November 2026** includes checked answers for **11 of 13** games. Crosswordle is a guide (the original reverse Wordle can have multiple valid solutions). Mathler has an example that fits the specific screenshot clues shared during development, but is not represented as the game's uniquely correct answer.
- Visual solution boards for Queens, Tango, Zip, Patches, Mini Sudoku and Sumplete.
- A new date without checked data never displays the previous day's answers as though they are current.

## Preview locally

Open `daily-puzzle-hub-preview.html` (if supplied alongside this ZIP). Or from the project folder run:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`. The homepage includes an embedded copy of the latest edition for offline first load; other dates are requested from `data/YYYY-MM-DD.json` and require a normal website/server.

## Make it a public website (GitHub Pages)

1. Create a new public GitHub repository.
2. Upload the **contents** of this folder, including `.github/workflows/daily.yml`.
3. On GitHub: **Settings → Pages → Build and deployment → Deploy from a branch → main / (root)**. (If your branch is different, select its name.)
4. Go to **Actions** and enable workflows if prompted. Use **Refresh puzzle answers → Run workflow** to test.
5. GitHub Pages will give you a free public HTTPS website. A custom domain is optional.

## Daily updates: important limitations

The workflow runs at **09:30 and 12:30 UTC** (after LinkedIn's midnight-Pacific reset) and attempts to generate each new date's JSON. It currently retrieves Wordle from a public NYT JSON endpoint, tries to read Strands and Sumplete from independent guides, and attempts to parse each of LinkedIn's eight dated guide pages. It checks the puzzle date/number and validates puzzle structures before displaying **Verified**. If a site changes layout, blocks requests, or has not published yet, the corresponding game shows *not verified* rather than a fabricated result.

This workflow is **best effort, not a guaranteed 13/13 autonomous publishing pipeline**. Daily Mathler and original Crosswordle are **not automatically solved**; either needs an additional licensed data source, a custom solver/user-input feature, or manual curation. For a public monetised site, review the third-party websites' terms and data reuse rights, add your own original hints and explanation, and build a human QA step. Do not mass-republish copyrighted source articles or logos.

Manually correct or add a day at `data/YYYY-MM-DD.json` and run `python scripts/embed.py` if it becomes the newest date. Use existing entries as examples. The JSON structure supports answers of type `word`, `strands`, `words`, `ladder`, `queens`, `tango`, `zip`, `sudoku`, `patches`, `sumplete`, `math`, and `notice`.

## Host/maintenance notes

- This is an **independent reference website**, not an official game publisher or partner.
- There is no account system, database, tracking, advertising integration or deployment performed on your behalf.
- External source parsers may stop working; monitor the Action logs and review published entries.
- The free GitHub Pages address will look like `your-user.github.io/your-repo/`; it will not be live until you deploy.
- The initial data file was verified against publicly available solution guides on 1 November 2026. Attribution links are available inside each game card.
