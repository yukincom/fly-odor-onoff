# Execution API

English | [日本語](API.md)

`experiment.run()` reruns a specified experimental condition and returns a JSON-compatible dictionary containing metrics and comparisons against the reference records.

```python
from experiment import run

result = run(2026091701, 1.0, "known_positive")
```

## Arguments

| Argument | Description |
|---|---|
| `seed` | One of the four random seeds recorded in the protocol |
| `gain` | Stimulus-rate multiplier: `1.0` or `0.5` |
| `gate` | Input-blocking condition defined for the experiment |
| `experiment` | Defaults to `brain-four-pn-readout`; also accepts `brain-orn-entry` and `brain-pn-output` |
| `upstream` | Model checkout at the pinned commit; defaults to `upstream/` at the repository root |
| `jdk` | Java 25 `bin` directory; if omitted, uses `JAVA_HOME` or PATH |
| `out` | New output directory; if omitted, creates a uniquely named directory under `runs/` |

`gain` applies to the stimulus and is separate from the circuit parameter `cfg.gain=0.65`. In result files, `hungry` and `satiated` label input gains of 1.0 and 0.5, respectively.

For the four-PN `known_positive` condition, a `control` with the same seed and input gain is also run to calculate ratios against the control. Other calls run one condition each.

## Output

The returned fields are `experiment, seed, gain, gate, protocol_sha256, metrics, replay_verification`. The same content is saved to `indicators.json` in the output directory.

- `metrics`: firing rates, control ratios, and evaluations calculated from the run.
- `protocol_sha256`: hash of the experimental conditions used.
- `replay_verification`: count and SHA256 hashes of files matching the reference records byte for byte.

Raw records and execution logs are also saved to the output directory. `runs/` is excluded from Git.

## Conditions and evaluation

Each experiment's `protocol.json` records the stimulus, measurement windows, and blocking rules; `cohorts.json` defines the populations. In the four-PN experiment, stimulus ON/OFF is supplied by a fixed schedule. The four readout PNs and the full set of 686 ALPNs targeted by input blocking are different sets.

Reference criteria are a peak ratio of at least 70%, a late-response ratio of at least 30%, and a post-stimulus mean of at most 3 Hz. Individual-cell 0 Hz and the absence of all spikes from 1 s after stimulus removal onward are returned as separate evaluations. See each protocol for the detailed thresholds.

## Errors and verification

The runner supports the recorded conditions. Unregistered seeds, gains, or blocking conditions; modified protocols or measurement code; and existing output directories cause an error before simulation starts. A mismatch between regenerated raw records and reference hashes also raises an error.

Experiments with different conditions require a new protocol describing those conditions and corresponding harness and validation code.

```sh
.venv/bin/python verify.py
.venv/bin/python -m unittest test_contract.py
```

`verify.py` checks the integrity of distributed files, conditions, and decision tables. `test_contract.py` checks input validation and overwrite prevention. Neither runs the simulation itself.
