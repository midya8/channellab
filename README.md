# ChannelLab: same accuracy, different information

Exact finite binary experiment comparison. A constructive state-independent garbling, or a strict two-action decision witness proving why it cannot exist. Dependency-free Python 3.10+ and a separate BigInt browser inspector. Original implementation of classical Blackwell comparison, not a new theorem or learned sensor benchmark.

[Open the live inspector](https://midya8.github.io/channellab/).

## 0.2: hold the task fixed, vary every prior

A tie at one prior can hide a reversal. For the default classification task, A is strictly better for every 0 < p < 1/2, B for every 1/2 < p < 1, and both tie at p = 0, 1/2 and 1. Their optimal policies also change at 1/3 and 2/3. The new exact prior atlas finds all these changes over the complete closed prior interval, not a sampled grid.

Every policy has an exact affine value `intercept + slope * p` and its complete closed optimality range, including policies that are optimal only at a single endpoint or knot. The atlas retains all tied policies at every knot and on every open interval, the A/B/no-signal value functions, information-value functions and all additional A-minus-B roots. The browser shows the full atlas, every policy, a piecewise-affine chart and a separate exact download. The original v1 information-order report format is unchanged.

`examples/prior_crossing.json` is a disclosed denominator-four development example: A and B have equal task value at p = 1/3 without either channel's or the no-signal policy changing there. A policy-only partition would miss that ranking boundary. A separate test keeps the exact threshold 1/1,000,001 rather than losing a narrow prior cell to sampling.

The atlas is for **one supplied payoff table across all priors**, not all payoff tables. It does not establish Blackwell dominance. Certain-state endpoints are valid for task values because joint payoffs require no posterior division; the original information-order input still requires full support.

```sh
python -m channellab atlas examples/incomparable.json > atlas.json
python -m channellab verify-atlas atlas.json
python -m channellab atlas examples/prior_crossing.json
# Optional independent floating LP reference for every policy's prior range:
python tools/check_atlas_highs.py
```

The generator intersects complete-policy half-spaces. The separate `atlas_verify.py` instead finds optimal per-signal action crossings and constructs all joint policy ties as Cartesian products. Importing either checker does not load either generator. No new theorem, posterior-learning method, statistical confidence or real-world sensor validation is claimed.

## One task ties. The information order does not.

At a uniform prior over states 0 and 1, consider:

```text
          signal0 signal1             signal0 signal1
A state0     1       0       B state0    1/2     1/2
A state1    1/2     1/2      B state1     0       1
```

Both experiments achieve exactly 3/4 optimal classification accuracy. Neither can simulate the other using a single state-independent randomized signal transformation.

| Decision task | Optimal value from A | Optimal value from B | Strict advantage |
|---|---:|---:|---:|
| Action 0=(0,0), action 1=(-1/3,2/3) | 1/6 | 1/4 | B by 1/12 |
| Action 0=(0,0), action 1=(-2/3,1/3) | 1/12 | 0 | A by 1/12 |

Payoff pairs list state 0 then state 1. The decision maker chooses after seeing the signal. These are exact supplied teaching problems, not measured sensors, a dataset, an accuracy leaderboard or a real-world recommendation.

## Inspect the entire comparison

```sh
python -m channellab demo
python -m channellab run examples/incomparable.json > report.json
python -m channellab verify report.json
python -m pip install .
channellab demo
python -m unittest discover -s tests -v
node --test --test-concurrency=1 tests/test_engine.cjs tests/test_atlas.cjs tests/test_browser.cjs
python tools/check_installed.py
# Optional external numerical reference:
python tools/check_highs.py
# Serve docs/ using any static server to open the browser inspector.
```

The local browser accepts the complete exact model, switches between both directions, exposes every signal/posterior, every call-function knot, stochastic kernel, reconstructed state law, prior-weighted coupling and every deterministic task policy. A failed direction exposes its own two-action counterexample with all signal action values and ties. Zero-mass signals have null posteriors, not invented beliefs. Downloads contain the full exact report for separate native replay. Editing clears old output and disables download; failed input leaves no stale result. All computation stays local, no backend, network model or paid API.

The default is one of 13 developed controls. Relabelled and split signals can be equivalent even with different output alphabets. A perfect signal can be more informative without helping a task whose best action ignores the state. A tiny full-support prior changes posterior positions and task values, not Blackwell order. A disclosed large-fraction control requires integer outputs beyond JavaScript's safe range.

## The finite proof objects

For two states and any full-support prior, A dominates B exactly when its posterior distribution is larger in convex order. The upper-hinge call value is C(t)=E[max(posterior-t,0)]. ChannelLab checks all supported posterior knots plus 0 and 1. Their difference is affine between knots, so there is no threshold-sampling gap.

- A passing direction constructs K>=0 with each row summing to 1 and A K=B for both states. Exact bounded-polytope basis enumeration returns one feasible vertex, not every kernel.
- A failed direction supplies a knot t with C_B(t)>C_A(t), and payoffs (0,0) versus (-t,1-t). The returned strict value gap is a separating decision problem, not a failed numerical search.
- A separate verifier imports validation only, not the generator or its elimination/basis solver. It replays every field and checks feasible kernel equations or the strict witness. Valid alternative feasible kernels are accepted if their derived fields match. This is computational evidence, not a proof-assistant certificate.

The chart connects exact knots using floating-point pixel coordinates only. Inference, tables and report serialization use exact fractions. [METHOD.md](METHOD.md) gives the derivation, complete schema, independent-check contract, development-search provenance and the inspected source ledger.

## Checks actually executed

- 30 Python tests, including 372 separately altered non-input primitive leaves rejected in the default report, unknown fields/type confusion, signal/state relabelling, full-support prior changes, null signals, strict CLI errors and a valid alternative feasible kernel.
- 710 complete Python/checker/BigInt report comparisons: 13 controls, all 625 ordered pairs of denominator-four binary-output channels, and 72 seeded rectangular pairs over all nine 1..3 by 1..3 signal-count combinations. Reports include 6,994 task policies, 627 feasible directional kernels and 793 strict directional counterexamples. This is a declared small finite grid, not a universal empirical benchmark.
- Actual SciPy 1.15.3 HiGHS executes 1,420 directional feasibility solves. Its 627 feasible cases match the exact relation. Worst equality residual below 2.8e-16, against a 1e-8 tolerance. SciPy is optional reference evidence, never a production dependency.
- 710 complete Python/signal-checker/BigInt atlas comparisons cover 8,486 affine policies, 3,401 exact knots and 2,691 open intervals. Another 297 separately altered non-input atlas primitives are rejected, plus missing knots/intervals, policy-range changes, noncanonical rationals and type confusion. Endpoint-only policies, null signals, duplicate actions, constant negative payoffs, state reflection and supplied-prior independence are tested.
- Optional SciPy 1.15.3 HiGHS runs 16,972 additional LPs to find both endpoints of all 8,486 policy optimality ranges. All 6,251 nonempty ranges match; worst endpoint difference is 0 on this declared finite suite, against 1e-8 tolerance. Numerical agreement is reference evidence, not exact proof.
- A fresh 0.2.0 wheel outside the checkout checks eight module origins and installed distribution version, all 13 controls and atlases through both console/module entrypoints. For each report type, 26 direct and 52 CLI forgery rejections pass.
- Actual Chrome checks 39 control/width reports at 1280, 390 and 320 pixels, 78 directions, 165 posterior rows, 162 hinge rows, 366 task-policy rows, 99 kernel rows and 147 witness-signal rows. The same 39 views check 180 atlas-knot rows, 141 open-interval rows and 444 affine-policy rows. Thirteen information-order and thirteen atlas trusted completed downloads are byte-exact and accepted by their separate native verifiers. All visible signal, task, kernel/coupling/moment and separating-witness tables are checked. Stale/invalid clearing, touch-target heights, horizontal table scroll and viewport containment are tested. Publication/deployed pixel completion is a separate gate, not inferred from these local tests.

## Scope without shortcuts

Exactly two states. One to three signals per channel, one to three actions. One full-support prior. Exact non-boolean integer/pair input, raw components<=1,000,000; normalized denominator LCM<=1,000,000; payoff magnitude<=100. Strict JSON input 64 KiB, report verification 8 MiB. Enumeration bounds do not bound all arithmetic bit complexity, output size, wall time or memory. Full details in METHOD.

No channel learning, sequential design, real sensor validation, privacy guarantee, finance, safety promise, multi-state scalar-order shortcut, scalability claim or new Blackwell algorithm. Shared mathematical assumptions remain shared failure modes in cross-language/reference agreement. Exact arithmetic does not make the supplied model true. MIT.
