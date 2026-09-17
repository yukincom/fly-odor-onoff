# Four DM1/VA2 PNs: preserved ON responses, OFF silence, and re-ON recovery

English | [日本語](README.md)

Firing during stimulation, after stimulus removal, and during restimulation was compared in four projection neurons (PNs) associated with DM1/VA2. Blocking known-positive eLN→PN inputs only during OFF preserved the initial stimulus response, reduced post-stimulus firing to zero, and allowed the response to return upon restimulation. This time-response pattern was observed in all eight paired configurations: four random seeds × two input gains.

## Readout cells and input blocking

- Readout: four cells, DM1_lPN `10176 / 10208` and VA2_adPN `10390 / 10561`.
- Blocked inputs: 11,069 known-positive ALLN edges arriving at all 686 ALPNs (10,944 ACh + 125 octopamine). Inputs labeled `unclear` and negative inputs pass through. “Known” refers to labels within the model.
- Stimulus ON/OFF and input blocking follow a fixed schedule.
- The four DM1/VA2 cells are aggregated separately from the mean across all 686 ALPNs and from the VP3 population.

No TRN cuts, temperature interpretation, or new adaptation terms were added. Earlier OFF20 measurements could not reconstruct ON peaks or re-ON responses, so individual 1 ms spike counters were added for the four PNs and the same 16 trials were rerun.

## Measurement windows and evaluation

| Metric | Calculation window |
|---|---|
| Initial and re-ON peaks, 10/50 ms | Maximum rolling mean wholly within each ON period, advanced in 1 ms steps |
| Late stimulus response | Last 500 ms of each ON period |
| OFF1 and re-OFF1 | 900–1000 ms after the corresponding stimulus removal |
| OFF20 | 19900–20000 ms after the first stimulus removal |
| Individual-cell silence | Whether each of the four cells has zero firing in the OFF windows above |
| Sustained silence | All spikes from 1 s after stimulus removal until the next ON or the end of the recording |

Operational reference thresholds were at least 70% of the matched control for peaks, at least 30% for late responses, and an OFF mean of at most 3 Hz. Restimulation peaks must also reach at least 70% of the initial peaks within the same trial, and the re-ON 50 ms peak must exceed OFF20. Individual 0 Hz and the reference mean threshold of 3 Hz are separate evaluations. These thresholds are not established physiological values.

| Metric: four-PN mean | control (8 trials) | known_positive (8 trials) |
|---|---:|---:|
| Initial peak, 10 ms | 450–500 Hz | 450–500 Hz |
| Initial peak, 50 ms | 410–455 Hz | 410–455 Hz |
| Initial late response, 500 ms | 391.5–429.5 Hz | 391.5–429.5 Hz |
| OFF1 | 330–350 Hz | 0 Hz |
| OFF20 | 335–352.5 Hz | 0 Hz |
| Re-ON peak, 10 ms | 425–500 Hz | 450–500 Hz |
| Re-ON peak, 50 ms | 410–450 Hz | 410–450 Hz |
| Re-ON late response, 500 ms | 392.5–432 Hz | 393.5–432.5 Hz |
| Re-OFF1 | 332.5–352.5 Hz | 0 Hz |

Both initial peaks and the initial late response were 100% of the matched control in every pair. The re-ON 50 ms peak was 98.8–101.1% of control. In all eight gated trials, each of the four cells had exactly 0 Hz at OFF1, OFF20, and re-OFF1. All cells remained silent from 1 s after stimulus removal until the next ON or the end of the recording.

Four of the 16 initial and repeated OFF periods contained no spikes. In the other periods, the upper edge of the last occupied 1 ms bin was at most 3 ms after stimulus removal. This is a bin boundary, not an exact spike timestamp.

![Time responses](results/four-PN-time-response.png)

The figure shows the mean of the four DM1/VA2 cells, not the mean across all 686 ALPNs. It uses fixed 10 ms bins; evaluation uses 10/50 ms rolling means advanced in 1 ms steps.

## Consistency after adding the counters

All 144 existing files (16 trials × 9 files) remained byte-identical to the earlier records after the new counters were added. These include cumulative counts for all PNs, population and ORN counters, and input, arrival, and boundary records. The new four-PN counters also matched the previous individual cumulative counts at four checkpoints. Four-PN traces through the end of the initial ON were identical between paired control and gated trials. Peaks calculated with cumulative sums were checked independently using NumPy convolution.

The [individual-cell CSV](results/cells.csv), [counter-addition verification](results/final-verification.json), and per-trial validation JSON files are included. Full 1 ms records are represented by reference hashes and regenerated during reruns.

## Scope

The readout consists of four PNs, while input blocking targets all 686 ALPNs. Blocking follows the fixed stimulus schedule. The result describes the time responses of these four cells; silence across all PNs, autonomous detection of stimulus removal from neural activity, and responses under different stimulus conditions were not tested.

## Conditions and data

Experimental conditions are recorded in [protocol.json](protocol.json), populations in [cohorts.json](cohorts.json), and evaluations in [decision-table.csv](decision-table.csv). Each blocking condition starts from the original circuit.

Four seeds (`2026091701, 2026091711, 2026091721, 2026091731`) are combined with input gains of 1.0 and 0.5. The 157 DM1/VA2 ORNs receive 60 Hz × input gain. The sequence is 0.5 s without input → ON for 1 s → OFF for 20 s → re-ON for 1 s → re-OFF for 2 s. Settings are dt = 0.5 ms, delay = 2 ms, circuit gain = 0.65, KC gain = 0.25, one worker, and a 50 ms endTick. Other settings use the pinned upstream LifConfig. The labels `hungry` and `satiated` denote input gains of 1.0 and 0.5, respectively.

Immediately before integration during OFF, the arriving input is replaced with a version that excludes only the selected edges at that arrival time. The original float addition order is preserved, and the delay buffer's nonzero-entry count is kept consistent. Spikes emitted at the end of ON and arriving during OFF are blocked; spikes emitted at the end of OFF and arriving during re-ON pass through. Membrane potential and existing synaptic state are not reset.

The [result CSV](results/summary.csv) and [metrics JSON](results/report.json) retain values from the original measurements. The [byte-copy manifest](byte-copy-manifest.json), [reference hashes for omitted raw records](reference-hashes.json), and per-trial validation JSON files are included. Full timestep records are generated during reruns and checked by SHA256 rather than distributed. Record hashes do not establish physiological validity.

## Reproduction

```sh
.venv/bin/python experiment.py --seed 2026091701 --gain 1 --gate known_positive \
  --jdk /path/to/jdk-25/bin --out runs/four-pn-seed1
```

`known_positive` also runs a fresh matched `control` to calculate metrics and control ratios. Repeating this for four seeds × two input gains reproduces the original 16 trials. `control` can also be run alone. Returned metrics are checked against the saved report.
