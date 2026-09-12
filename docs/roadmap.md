# Mycelium-EI-Lang roadmap: a language for evidence-qualified environmental judgment

Status: proposal, written 2026-09-11. Nothing in this document runs. What runs is in the README and `docs/reference.md`. The programs under `examples/roadmap/` are written in the syntax this document proposes and are marked as such; the test suite does not execute them.

## 1. Where the idea came from

The record, from the repositories and files themselves:

- **January 2025, `mycelium-ei-platform`.** The first statement: "a proprietary environmental intelligence solution ... to monitor, predict, and mitigate environmental challenges in real time". The code that existed matched fungal strains to a site by temperature range, pH range and goal (restoration, pollutant breakdown). EI meant Environmental Intelligence.
- **February and March 2025, CroweOS and `Mycelium-EI`.** The grow room arrived: a batch schema (strain, substrate, spawn ratio, humidity, temperature, CO2, growth stage), a sensor schema (grow room, temperature, humidity, CO2, air exchange, light), a prediction schema (yield, growth time, harvest readiness, contamination alert), and the loop "Automation Triggers: adjust humidity, CO2 and lighting". The naming triad was fixed on 2025-03-02: Mycelium EI is "the ecological intelligence engine that processes sensor data", Crowe Logic the decision layer, Crowe OS the company. The rules that shipped were stubs: `risk = 0.1 if co2 < 900 else 0.5`; `"Increase cooling" if temp > 22`.
- **September 2025, this repository.** The language: `environment { }`, `mycelium Name { signal ...; network ...; function ...; adapt function ... }`, top-level `signal` types, and a compiler described as "type checking with environmental constraints". The roadmap sketched `type Temperature = Float<18.0, 30.0>`, an effect declaration for what an adapt function may modify, "mock environmental conditions" for tests, and "sensor integration, environmental change detection, threshold-based alerting, historical data tracking". The Rust crate got as far as an AST and a type enum; the Python interpreter ran four examples. The same month `crowe-sense` was created.
- **2026, Crowe Sense.** The environment block became physical: a node contract where every reading is `ts, node, zone, sensor, metric, value, unit, quality`, a metric vocabulary (`temperature_c`, `humidity_pct`, `co2_ppm`, `vpd_kpa`, `dew_point_c`, `light_lux`, `fruiting_score`, ...), derived metrics marked `sensor: derived, quality: est`, a stage transition log per zone, and 37 practice bands parsed from 642 cited statements in the cultivation video corpus. A Python checker (`sense_check.py`) accumulated the rules that make a judgment honest, each learned from a wrong answer on recorded data.
- **June 2026, Cortex.** A design note mapped the language onto a knowledge workspace: `environment` is the workspace, `adapt function` is a rule with a cooldown and a depth limit of two, `signal` is an event, and Crowe Sense "is the canonical environment block made physical". It decided against embedding the interpreter, because the interpreter of the time had nothing to offer that JSON rules did not.
- **July 2026, the desktop grow schema.** Blocks (species, strain, substrate, room, spawned date, stage), flushes (weight, grade), contamination events (organism, stage caught, action), environment rows (room, temperature, humidity, CO2, fresh air exchange). This is the outcome side of the loop that every prediction plan needed and never had.

Three things recur across every document: the loop sense, judge, adapt, outcome; strain matched to environment; and a mycelial network as the picture of how the parts connect. Two things failed every time: predictions with no labelled outcomes behind them, and claims (real-time, intelligence, quantum) ahead of what ran. The assets that survived are recorded readings, a stage log, cited constants, and a checker whose rules are worth keeping.

## 2. The thesis for 1.0

Mycelium-EI-Lang becomes the language in which an environmental judgment is written down so that anyone can replay it. The defining promise:

> The same recorded readings, the same evidence snapshot and the same declared policies produce the same judgments, the same refusals and the same proposed effects, offline, on any machine.

It is not a general-purpose language with cultivation libraries, and it is not a prediction engine. It is a small scripting shell around four primitive ideas that today live as conventions inside one Python file and one JSON file, where nothing enforces them.

Why this and not "faster interpreter plus more builtins": the optimizers, the toy network and the simulated monitor are demonstrations anyone could write in Python in an afternoon. The rules for when a reading may be judged against a documented practice, and for what an adaptation may do and when, are the part nobody else has, and they are currently unenforceable because they are prose in docstrings.

## 3. Core constructs

Primitive means the interpreter enforces it and a program cannot opt out. Library means it ships with the package but a program can ignore or replace it.

### 3.1 Quantities with units (primitive)

Literals carry units: `22.5 C`, `85 %`, `800 ppm`, `0.4 kPa`, `20 min`, `6 h`, `9 s`. Arithmetic is checked: adding or comparing two quantities needs the same unit; multiplying by a plain number is allowed; `21.1 C == 70 F` converts. A refinement is a declared constraint, written by the programmer: `let target: C where 18 C <= value <= 30 C`. A refinement never acquires evidence status by being declared; only a practice envelope (3.4) carries evidence.

A reading of `34 C` is a valid temperature. It is not a valid `target`. The language reports the second fact; it never drops the first.

### 3.2 Readings, series and logs (primitive)

A `reading` is the telemetry-v1 tuple. A `series` is readings of one metric in one zone, ordered by time, with a known cadence. The semantics that today live in `sense_check.py` become language rules:

- A reading stands for the interval until the next reading, so a run covers one cadence past its last sample. On raw data this adds seconds; on hourly means it is the difference between a one-hour excursion counting for an hour and counting for nothing.
- A gap longer than three times the typical cadence (minimum five minutes) is a sensor outage, not a room out of band, and is never counted.
- Aggregates are distinguished from raw readings; an hourly mean cannot establish a twenty-minute sustained condition.
- Quality is filtered explicitly (`ok`, `est`, `warming`, `stale`, `fault`); nothing is interpolated.
- `sustained(condition, 20 min)` yields periods with start, end, direction and worst value; `total_outside` reports every moment outside, including dips too short to be a period, as hours and as a percentage of readings.

### 3.3 Stages as a transition log (primitive)

`stage log` entries are (zone, stage, species, batch, start). Each entry runs until the next for that zone. A span with no entry is UNKNOWN and is not judged; `idle` is skipped. The stage decides which practice applies, and the same readings are three and a half hours out against a fruiting floor or fifteen against a pin-set band, so the language never guesses it.

### 3.4 Practice envelopes and judgment (primitive semantics, versioned data)

A `practice` is built from cited statements loaded from a file (the 37 bands today). The statements are data and are versioned with the program; the rules for turning them into a band are language semantics:

- Each statement has a kind (band or threshold), a bound (range, lower, upper, or point when low equals high), a stage, optional species, and sources.
- Floor and ceiling are the median of stated lows and highs, never interpolated: on a tie the more forgiving middle wins, lower for a floor and upper for a ceiling, so every printed number is one somebody said.
- Sidedness is honoured: a ceiling-only statement sets no floor. Point statements support the floor only.
- A side counts distinct sources. A side with fewer than two is not judged, and the output says which side was dropped and why.
- If the floor lands above the ceiling, the better-evidenced side stays.
- Thresholds are reported separately from bands.
- A tolerance of two percent of the span, at least 0.05, absorbs unit-conversion noise (70 F is 21.11 C).
- Derived metrics (VPD from temperature and humidity) inherit the weaker of their parents' evidence. A band refused in one unit does not return in another.

`judge(series, practice, stages)` returns a verdict, not a boolean: `inside`, `below`, `above` with periods and totals, or `not_judged` with the reason (no documentation for this stage, one source only, stage unknown, no readings). "Inside your documented band" is a deliberately weaker claim than "good".

### 3.5 Adapt rules with time (primitive)

`adapt name on series { effects { ... } when ... sustained ... recover when ... cooldown ... }`. The rule declares its effects: `append` to a report, `propose` an actuator change, or `control` one. In replay, `control` becomes a recorded proposal with its cause and time; nothing drives hardware from a recording. Sustain windows and recovery margins (hysteresis) are trigger policy and are printed as such; they never alter the documented envelope. A cooldown and a chain depth of two come from the Cortex design and prevent rules feeding rules.

This replaces today's `adapt function` firing on every `set_env`, which has no notion of time, sustain or effect. Existing programs keep running through a compatibility path.

### 3.6 Environments (primitive)

`environment name = replay(file)`, `live(node)`, `series { values: [...] }` (a mock), or the literal block of today. Replay and mock share one clock, and `sleep` advances it instead of waiting. A program that works on a recording works on a mock in a test, and the live adapter is a package that produces the same readings from the node API.

### 3.7 The scripting shell (kept small)

Functions, records, arrays, strings, `if`, `while`, `for`, `mycelium` models with fields and methods. These stay as they are in 0.2.x.

### Library, not core

The genetic, particle swarm and ant colony optimizers, the Hebbian network and the simulated cultivation monitor move to an optional `mycelium_ei.bio` namespace, labelled as demonstrations. Sensor drivers, HTTP clients and node details live in an adapter package. Species recipes, cultivation constants and formulas such as VPD are data and standard-library functions, never language facts. Nothing in the core predicts contamination or yield.

## 4. Example programs

Under `examples/roadmap/`, in the proposed syntax, not executable in 0.2.x:

- `fruiting_humidity.myc` judges the two fruiting tents in the 469-hour recorded aggregate against the documented 80 percent humidity floor and refuses to judge CO2, for which the corpus holds no setpoint. The acceptance test for milestone 0.5 is that it reproduces the recorded finding: both tents below the floor for about six hours each night, 02:00 to 08:00 local, on 20 of 23 nights.
- `adapt_with_sustain.myc` shows a rule with a sustain window, a recovery margin, a cooldown and a proposed effect recorded during replay.
- `mock_environment_test.myc` shows tests against a hand-written series, including a unit mismatch caught by `myc --check` before anything runs.

## 5. Milestones

Each milestone ships when its test exists and passes on CPython 3.9 to 3.14, and its README entry says what it does not claim.

| Version | What lands | The test that proves it |
| --- | --- | --- |
| 0.3 | Quantities with units; `myc --check` grows a static pass for undefined names, arity and unit mismatch | unit algebra table; a program with `20 C < 80 %` fails `--check` with the line |
| 0.4 | Series and replay environments reading telemetry-v1 CSV and JSONL; cadence, gaps, `sustained`, `total_outside`; a REPL | the 23 regression cases from `test_sense_check.py` ported as `.myc` tests |
| 0.5 | Stage logs, practice envelopes, `judge` with the consensus rules | `fruiting_humidity.myc` reproduces the nightly finding from the recorded aggregate; CO2 is refused |
| 0.6 | Adapt rules with sustain, recover, cooldown, effects and replay proposals | hysteresis and depth-limit fixtures; a proposal log that is byte-identical across two runs |
| 0.7 | Live adapter for the node API and relay, as a separate package; runs on the Raspberry Pi | the same program gives the same verdict on a recording and on the live replay of that recording |
| 0.8 | Tooling: language server and a truthful VS Code extension, a formatter, a browser Lab that loads the wheel in Pyodide (the package has no dependencies, so this is packaging, not porting) | `--check` diagnostics appear in the editor; the Lab runs the twelve examples |
| 0.9 | Speed: compile the syntax tree to closures; keep pure Python | ten times faster than 0.2.2 on the two benchmarks below |
| 1.0 | Specification frozen, conformance suite, semantic versioning; the Rust crate implements the specification or is removed | every example and every test in the conformance suite passes on the reference interpreter |

Benchmarks measured on 2026-09-11 with 0.2.2 on this Mac: a 200,000-iteration while loop with arithmetic takes 0.57 s (plain Python: 0.03 s); 50,000 calls of a three-argument function take 0.46 s. The interpreter is about twenty times slower than Python on tight loops, which is acceptable for judging hourly and nine-second telemetry and is not a priority before 0.9.

## 6. Left out, and why

- Contamination and yield prediction in the core. The corpus grounds conditions richly and contamination dynamics barely; a number invented there would poison the parts that are real. Prediction can be a library on top of judgments once labelled outcomes exist.
- Wording that claims intelligence, quantum behaviour or performance superiority. Every README line traces to a test or a dated run.
- Wall-clock sleep, arbitrary I/O and undeclared mutation inside replayable rules.
- Sensor drivers, HTTP, dashboards and Raspberry Pi details in the core.
- A large class system or a second event mechanism beside the one in 3.5.

## 7. Open questions for Michael

1. **What does EI expand to?** The record says Environmental (2025-01), Ecological (2025-03 onward) and Earth (2026). The language needs one word in its one-sentence description.
2. **Provenance of the recordings.** The Crowe Sense notes disagree on whether the 2026 tent channels came from physical sensors or were synthetic. The roadmap examples call them "recorded"; the README must say which they were before any example is presented as a real finding.
3. **Where the language runs.** Cortex decided in June 2026 not to embed the interpreter. A replay engine with the semantics above is a different proposition; the decision can be revisited at 0.6, not before.
4. **The old PyPI name.** `mycelium-ei-lang` stays orphaned unless the account recovery succeeds; the language's name and the package's name may stay different for good.
