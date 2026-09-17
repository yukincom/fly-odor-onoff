# fly-odor-onoff

English | [日本語](README_jp.md)

Odor ON/OFF responses in a fly connectome model.

Average projection-neuron activity can remain high after odor input is switched off. This record follows ON, OFF, and re-ON responses in just four cells associated with DM1 and VA2. It does not report a correction of the entire circuit.

Why does neural activity persist in the model after odor stimulation ends?

Using the connectome-derived leaky integrate-and-fire (LIF) model from [fly-brain-minecraft](https://github.com/blendi-remade/fly-brain-minecraft/tree/6cfa30175003ef25da68a237d5eda958f8047b82), these experiments examine which input pathways sustain post-stimulus activity and how the observed result depends on the cell population being measured. Selected inputs were blocked only during stimulus-OFF periods, and firing was compared during stimulation, after stimulus removal, and upon restimulation.

## Main findings

In four projection neurons (PNs) associated with DM1 and VA2, blocking inputs with a known positive sign from excitatory local neurons (eLNs) only during stimulus-OFF periods **preserved the initial stimulus response, reduced post-stimulus firing to zero, and allowed responses to return upon restimulation**. This pattern was observed in all eight paired configurations: four random seeds × two input gains.

| Mean firing rate of the four PNs | No input block | Input blocked only during OFF |
|---|---:|---:|
| Initial stimulus peak, 50 ms window | 410–455 Hz | 410–455 Hz |
| 1 s after stimulus removal | 330–350 Hz | 0 Hz |
| 20 s after stimulus removal | 335–352.5 Hz | 0 Hz |
| Restimulation peak, 50 ms window | 410–450 Hz | 410–450 Hz |
| 1 s after restimulation ends | 332.5–352.5 Hz | 0 Hz |

Values are ranges across eight trials per condition. In all three post-stimulus measurement windows, each of the four cells individually had a firing rate of 0 Hz. Window definitions and individual values are provided in the [four-PN time-response experiment](experiments/brain-four-pn-readout/README.md) (Japanese).

![Time responses of the four PNs](experiments/brain-four-pn-readout/results/four-PN-time-response.png)

This figure shows the mean of the four DM1/VA2 cells, not the mean across all 686 ALPNs.

## Experiments

| Experiment | Question | Result |
|---|---|---|
| [Return inputs to ORNs](experiments/brain-orn-entry/README.md) | Block PN/LN inputs to ten ORNs with persistent firing | Nine ORNs became silent, while high PN activity persisted |
| [eLN inputs to PNs](experiments/brain-pn-output/README.md) | Block positive-sign eLN inputs to PNs | The mean across all PNs fell substantially, but some PNs retained high firing rates |
| [Time responses of four DM1/VA2 PNs](experiments/brain-four-pn-readout/README.md) | Fix the readout population and compare ON, OFF, and re-ON | Responses were preserved during stimulation, became silent after removal, and returned upon restimulation |

The input-side and output-side interventions were each applied separately to the original circuit. Detailed experiment READMEs are currently in Japanese.

## Scope

These results apply to the specified model, stimulus history, and cell populations. The roles of these pathways in biological olfaction, and responses to other odors or stimulus conditions, were not tested.

Blocking was timed using an external stimulus schedule. Although the readout contains four PNs, the intervention targets the selected inputs to all 686 ALPNs. The all-PN mean includes activity from different cell populations; silence in the four-PN readout is distinct from silence across all PNs.

## Usage

Key settings for reproducing the experiment:

| Setting | Value |
|---|---|
| Readout cells | DM1_lPN `10176` and `10208`; VA2_adPN `10390` and `10561` |
| Blocked inputs | 11,069 positive-sign ALLN edges onto all 686 ALPNs, excluding the neurotransmitter label `unclear` |
| Edge breakdown | 10,944 acetylcholine edges; 125 octopamine edges |
| Blocking time | Inputs **arriving** during stimulus-OFF periods; inputs arriving during ON pass through |
| Preserved state | Membrane potential and existing synaptic state; no reset at stimulus removal |

“Known positive sign” refers to the model's sign assignment and neurotransmitter labels. These experiments do not establish the biological action of each transmitter. The mean across all 686 ALPNs is recorded as a circuit-wide measure and analyzed separately from the four-PN DM1/VA2 mean.

`hungry` and `satiated` are aliases for input gains of 1.0 and 0.5, respectively; they do not represent physiological hunger or satiety states.

Requirements: Java 25, Python 3, and NumPy. The model revision and data SHA256 are recorded in [upstream.json](upstream.json).

```sh
git clone https://github.com/blendi-remade/fly-brain-minecraft.git upstream
git -C upstream checkout --detach 6cfa30175003ef25da68a237d5eda958f8047b82
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verify.py
```

Run one paired configuration of the four-PN experiment. This runs both the specified blocking condition and a control with the same seed and input gain.

```sh
.venv/bin/python experiment.py --seed 2026091701 --gain 1 --gate known_positive \
  --jdk /path/to/jdk-25/bin --out runs/four-pn-seed1-gain1
```

Replace `--jdk` with the path to your JDK 25 `bin` directory. If omitted, the runner uses `JAVA_HOME` or the JDK on `PATH`. Install JDK 25 first if it is not available.

The Python API, arguments, and output format are described in [API.md](API.md) (Japanese). Commands for the other two experiments appear in their respective READMEs.

## Data and reproducibility

Each experiment folder contains its conditions in `protocol.json`, population definitions in `cohorts.json`, a decision table, and result CSV/JSON files. Full timestep records are generated during a rerun and checked against the included reference hashes.

| File | Contents |
|---|---|
| `decision-table.csv` | Per-trial measurements and evaluation outcomes |
| `results/summary.csv` and `report.json` | Aggregate results and detailed metrics |
| `byte-copy-manifest.json` | Included files verified as byte-identical to the original records |
| `reference-hashes.json` | SHA256 references for comparing regenerated raw records |
| `MANIFEST.sha256` | SHA256 checksums for the distributed files |

Four representative trials were rerun using this repository's runner, and their raw-record hashes matched the references. Metrics were also recomputed from saved records for all 16 four-PN trials and all 64 input-side/output-side trials, and checked against the original results. The verification environment and details are recorded in [reproduction-check.json](reproduction-check.json).

See [NOTICE.md](NOTICE.md) for attribution and licensing information (Japanese).
