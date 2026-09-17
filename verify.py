"""Verify distributed bytes, small contracts, and published decision tables (no simulation)."""
import csv
import hashlib
import json
from pathlib import Path
import experiment

ROOT = Path(__file__).resolve().parent

def manifest(path):
    for line in path.read_text().splitlines():
        expected, relative = line.split('  ', 1)
        target = path.parent / relative
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('Manifest mismatch: ' + str(target.relative_to(ROOT)))

def main():
    manifest(ROOT / 'MANIFEST.sha256')
    counts = {}
    for folder in sorted((ROOT/'experiments').iterdir()):
        if not folder.is_dir():
            continue
        experiment.verify_contract(folder.name)
        manifest(folder/'MANIFEST.sha256')
        frozen = json.loads((folder/'byte-copy-manifest.json').read_text())
        for relative, expected in frozen['files_copied_byte_identically'].items():
            if experiment.digest(folder/relative) != expected:
                raise ValueError('Changed copied result: '+relative)
        with (folder/'results/summary.csv').open() as f:
            results = list(csv.DictReader(f))
        with (folder/'decision-table.csv').open() as f:
            decisions = list(csv.DictReader(f))
        if len(results) != len(decisions) or any(any(r[k] != v for k,v in d.items()) for r,d in zip(results,decisions)):
            raise ValueError('Decision table differs from summary: '+folder.name)
        counts[folder.name] = len(results)
        if folder.name == 'brain-four-pn-readout':
            gated = [r for r in results if r['condition']=='known_positive']
            if len(gated)!=8 or not all(r['all_reference_criteria_pass']==r['all_cells_exact_OFF_zero']==r['all_cells_quiet_tail']=='True' for r in gated):
                raise ValueError('README eight-pair claim differs from summary')
            report = json.loads((folder/'results/report.json').read_text())
            for row in gated:
                cells = report[row['trial']]['cells']
                if set(cells) != {'10176','10208','10390','10561'}:
                    raise ValueError('Readout changed')
                for cell in cells.values():
                    if not (cell['first']['OFF1_hz']==cell['first']['OFF20_hz']==cell['second']['OFF1_hz']==0):
                        raise ValueError('Individual zero claim failed')
    print(json.dumps({'distributed_manifests':'pass','copied_result_bytes':'pass','contract_locks':'pass',
                      'decision_table_trials':counts,'simulation_executed':False},indent=2))

if __name__ == '__main__':
    main()
