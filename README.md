# One image of 13 November 2026's world news

Entry for the [make.fun](https://make.fun) bounty `news-image-01`: sum up
Friday 13 November 2026's world news in one image.

## What it draws

A newspaper front page, "THE WORLD IN ONE DAY — FRIDAY 13 NOVEMBER 2026":

- **Lead — Nvidia chief executive resigns.** Jensen Huang steps down as
  chief executive and leaves the board; CFO Colette Kress becomes interim
  CEO.
- **Ukraine talks open to Europe.** Europe joins the next peace talks;
  Moscow and Kyiv plan the war's biggest prisoner swap.
- **Microsoft 365 goes down.** A worldwide outage disrupts businesses,
  schools and government services.
- **China's big Pacific drills.** Taiwan details huge, unannounced Chinese
  naval exercises across the Pacific and around Taiwan.
- **Tanker hit in the Gulf.** A tanker hits a mine in the Strait of Hormuz;
  inspectors cannot trace 440 kg of Iran's uranium.

Every story was verified against real reporting of 13 November 2026
(Reuters, AP, IEA, IAEA via The Raisina Post, Bangladesh Chronicle,
Open Chronicle and KLZ).

## Run

```sh
python3 main.py   # writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output)
```

Pure Python 3.13 standard library, no network, deterministic — two runs
write byte-identical output. The program draws the PNG itself (own PNG
encoder, drawing primitives and 5x7 bitmap font); 1024x1024, ~18 KB.
