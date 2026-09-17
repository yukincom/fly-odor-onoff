# Input side: are return inputs necessary for persistent firing in ten ORNs?

English | [日本語](README.md)

PN/LN return inputs to ten olfactory receptor neurons (ORNs) that continued firing after odor removal were blocked only during OFF. Blocking 116 edges silenced nine cells in all eight paired configurations, while the PN mean remained at 132–135 Hz, differing from control by less than 1%.

The ten fixed cell IDs are listed in the protocol. Individual ORN firing during 19–20 s after stimulus removal was the primary readout. The mean across all 686 PNs during 19.9–20 s was compared as a circuit-wide measure.

| OFF blocking condition | Edges | Silent ORNs / 10 | Ten-ORN mean, Hz | All-PN OFF20 mean, Hz |
|---|---:|---:|---:|---:|
| control | 0 | 0 | 74.60–77.70 | 132.84–135.01 |
| keep_unclear | 94 | 4–5 | 25.70–26.90 | 132.76–134.75 |
| block_all | 116 | 9 | 1.90–2.00 | 132.29–134.81 |

The 116 edges comprise 18 from ALPNs and 98 from ALLNs. The 94 labeled edges comprise 60 positive ACh and 34 negative GABA edges; the remaining 22 are positive edges labeled `unclear`. This comparison blocks both positive and negative inputs and cannot be interpreted as the effect of removing positive input alone. The remaining ORN_DL1 cell, `153948`, fired at 19–20 Hz. The reference criterion of silence in all ten cells was not met. No additional pathways were cut, and sufficiency was not tested.

All eight unblocked trials matched the original records over the full 24.5 s. All 16 gated trials matched their controls over the first 1.5 s, through the end of the initial ON. Arrival classification, preservation of ON inputs, and input reconstruction were verified for all 24 trials. Checks are recorded in each trial's `*-validation.json`.

![Comparison](results/necessity-summary.png)

## Scope

One ORN continued firing after the 116 edges were blocked. This intervention relates the specified return inputs to persistent activity, but does not establish fully independent ORN and PN activity sources or locate all sources of persistence within the AL. The effects of the same intervention in living flies were not tested.

## Conditions and data

Experimental conditions are recorded in [protocol.json](protocol.json), populations in [cohorts.json](cohorts.json), and evaluations in [decision-table.csv](decision-table.csv). Each blocking condition starts from the original circuit.

Four seeds (`2026091701, 2026091711, 2026091721, 2026091731`) are combined with input gains of 1.0 and 0.5. The 157 DM1/VA2 ORNs receive 60 Hz × input gain. The sequence is 0.5 s without input → ON for 1 s → OFF for 20 s → re-ON for 1 s → re-OFF for 2 s. Settings are dt = 0.5 ms, delay = 2 ms, circuit gain = 0.65, KC gain = 0.25, one worker, and a 50 ms endTick. Other settings use the pinned upstream LifConfig. The labels `hungry` and `satiated` denote input gains of 1.0 and 0.5, respectively.

Immediately before integration during OFF, the arriving input is replaced with a version that excludes only the selected edges at that arrival time. The original float addition order is preserved, and the delay buffer's nonzero-entry count is kept consistent. Spikes emitted at the end of ON and arriving during OFF are blocked; spikes emitted at the end of OFF and arriving during re-ON pass through. Membrane potential and existing synaptic state are not reset.

The [result CSV](results/summary.csv) and [metrics JSON](results/report.json) retain values from the original measurements. The [byte-copy manifest](byte-copy-manifest.json), [reference hashes for omitted raw records](reference-hashes.json), and per-trial validation JSON files are included. Full timestep records are generated during reruns and checked by SHA256 rather than distributed. Record hashes do not establish physiological validity.

## Reproduction

Prepare the dependencies and upstream checkout at the repository root, and specify an output directory that does not yet exist.

```sh
.venv/bin/python experiment.py --experiment brain-orn-entry \
  --seed 2026091701 --gain 1 --gate block_all \
  --jdk /path/to/jdk-25/bin --out runs/orn-entry-seed1
```

The three conditions (`control / keep_unclear / block_all`) × eight configurations give 24 trials. Each call runs one specified condition and checks raw-record hashes against the originals.
