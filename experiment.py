"""Re-run one frozen condition; return metrics JSON, never pick an intervention."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent
DEFAULT = 'brain-four-pn-readout'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

def verify_contract(experiment):
    if experiment not in ('brain-orn-entry', 'brain-pn-output', DEFAULT):
        raise ValueError('Unknown frozen experiment')
    folder = ROOT / 'experiments' / experiment
    # This adapter implements frozen schedules. Editing JSON alone must not silently run old code.
    locked = read(ROOT / 'contract-lock.json')
    for relative, expected in locked.items():
        if digest(ROOT / relative) != expected:
            raise ValueError('Contract/runtime changed: ' + relative + '. Version the protocol and adapter together.')
    p = read(folder / 'protocol.json')
    if p['external_gate_input']['feedback_from_PN_activity']:
        raise ValueError('Neural-output OFF feedback is outside this protocol')
    return folder, p

def compare_raw(folder, raw, name):
    ref = read(folder / 'reference-hashes.json')
    expected = dict(ref['raw_files_not_distributed'])
    expected.update(ref.get('historical_byte_equal_files', {}))
    relevant = {n: h for n, h in expected.items() if n.startswith(name + '-')}
    if not relevant:
        raise ValueError('No frozen reference for this invocation')
    differences = [n for n, h in relevant.items() if not (raw/n).is_file() or digest(raw/n) != h]
    if differences:
        raise RuntimeError('Replay differs from recorded bytes: ' + ', '.join(differences))
    return {'reference_files_byte_identical': len(relevant), 'sha256': relevant}

def endpoint_metrics(folder, raw, name, experiment):
    if experiment == 'brain-orn-entry':
        with (raw/(name+'-populations.csv')).open() as f:
            rows = list(csv.DictReader(f))
        p = read(folder/'protocol.json')
        rates = {b: sum(int(x['cell_'+b]) for x in rows[20500:21500]) for b in p['target_ids']}
        return {'ORN_OFF19to20_hz': rates,
                'PN_OFF20_hz': sum(int(x['ALPN_spikes']) for x in rows[21400:21500])*10/686,
                'PN_OFF19to20_hz': sum(int(x['ALPN_spikes']) for x in rows[20500:21500])/686,
                'quiet_ORN_count': sum(v <= 3 for v in rates.values()),
                'PN_cohort': 'all 686; diagnostic only, not odor readout'}
    with (raw/(name+'-PN-cells.csv')).open() as f:
        rows = list(csv.DictReader(f))
    rates = [(int(x['total_21500'])-int(x['total_21400']))*10 for x in rows]
    return {'PN_OFF20_hz': sum(rates)/len(rates), 'PN_max_cell_OFF20_hz': max(rates),
            'PN_cells_above_3Hz_OFF20': sum(x > 3 for x in rates),
            'PN_cohort': 'all 686; diagnostic only, not odor readout'}

def run(seed, gain, gate, *, experiment=DEFAULT, upstream=None, jdk=None, out=None):
    """Run a recorded seed/gain/gate. Four-PN gated runs include a fresh paired control.

    Defaults: upstream=./upstream; JDK bin from JAVA_HOME or PATH; unique ./runs/ folder.
    Unknown conditions and modified contracts fail before simulation. Raw files stay under runs/.
    """
    folder, protocol = verify_contract(experiment)
    if type(seed) is not int or seed not in protocol['seeds']:
        raise ValueError('Seed is not in the frozen protocol')
    labels = [key for key, value in protocol['states'].items() if value == gain]
    if isinstance(gain, bool) or len(labels) != 1 or gate not in protocol['conditions']:
        raise ValueError('Gain or gate is not in the frozen protocol')
    label = labels[0]
    upstream = Path(upstream or ROOT/'upstream').resolve()
    if jdk is None:
        jdk = Path(os.environ['JAVA_HOME'])/'bin' if 'JAVA_HOME' in os.environ else Path(shutil.which('javac') or '/missing/javac').parent
    jdk = Path(jdk).resolve()
    out = Path(out or ROOT/'runs'/str(uuid.uuid4())).resolve()
    if out == ROOT or (ROOT/'experiments') in out.parents or out == ROOT/'experiments':
        raise ValueError('Experimental records cannot be used as run output')
    out.mkdir(parents=True, exist_ok=False)
    write(out/'protocol.json', protocol)
    write(out/'invocation.json', {'seed':seed, 'gain':gain, 'gate':gate, 'experiment':experiment,
                                'contract_sha256':digest(folder/'protocol.json')})
    with (out/'build.log').open('w') as log:
        subprocess.run([sys.executable, str(folder/'runtime/build.py'), '--upstream', str(upstream),
                        '--output', str(out/'build'), '--jdk', str(jdk)], check=True, stdout=log, stderr=log)
    actual = read(out/'build/metadata.json'); original = read(folder/'runtime/model-hashes.json')
    for key in ('source_sha256', 'patched_sha256', 'data_sha256', 'wrappers'):
        if actual[key] != original[key]:
            raise RuntimeError('Compiled source differs: '+key)
    raw = out/'raw'; raw.mkdir()
    modes = ['control', gate] if experiment == DEFAULT and gate != 'control' else [gate]
    checks = {}
    for mode in modes:
        name = f'{mode}_{label}_{seed}'
        with (out/(name+'.log')).open('w') as log:
            subprocess.run([str(jdk/'java'), '-Xmx768m', '-cp', str(out/'build/classes'),
                            'GateTrial' if experiment == 'brain-orn-entry' else 'PNTrial',
                            str(upstream/protocol['upstream']['data_path']), str(raw), name,
                            str(seed), str(gain), '24500', '60', str(folder/'runtime/residual-ORN-ids.txt'), mode],
                           check=True, stdout=log, stderr=log, timeout=1800)
        checks[name] = compare_raw(folder, raw, name)
    name = f'{gate}_{label}_{seed}'
    if experiment == DEFAULT:
        subset = dict(protocol, seeds=[seed], states={label:gain}, conditions=modes)
        write(raw/'protocol.json', subset)
        write(raw/'complete.json', {'trials':len(modes)})
        with (out/'analysis.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT/'metrics.py'), str(raw)], check=True, stdout=log, stderr=log)
        metrics = read(raw/'report.json')[name]
        if metrics != read(folder/'results/report.json')[name]:
            raise RuntimeError('Recomputed indicators differ from frozen report')
    else:
        metrics = endpoint_metrics(folder, raw, name, experiment)
    result = {'experiment':experiment, 'seed':seed, 'gain':gain, 'gate':gate,
              'protocol_sha256':digest(folder/'protocol.json'), 'metrics':metrics, 'replay_verification':checks}
    write(out/'indicators.json', result)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--gain', type=float, required=True)
    parser.add_argument('--gate', required=True)
    parser.add_argument('--experiment', default=DEFAULT)
    parser.add_argument('--upstream', type=Path)
    parser.add_argument('--jdk', type=Path, help='JDK 25 bin directory')
    parser.add_argument('--out', type=Path)
    print(json.dumps(run(**vars(parser.parse_args())), ensure_ascii=False, indent=2, allow_nan=False))
