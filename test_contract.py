"""Protocol violations must fail before launching a simulation or overwriting records."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import experiment

class ContractTests(unittest.TestCase):
    def test_unrecorded_conditions_never_launch(self):
        for seed,gain,gate in [(1,1.,'known_positive'),(2026091701,.75,'known_positive'),
                               (2026091701,1.,'all_positive'),(2026091701,True,'control')]:
            with patch('experiment.subprocess.run') as launch:
                with self.assertRaises(ValueError):
                    experiment.run(seed,gain,gate)
                launch.assert_not_called()

    def test_changed_off_source_and_threshold_rejected(self):
        for field in ['OFF_input','threshold']:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)/'copy'
                shutil.copytree(experiment.ROOT,root,ignore=shutil.ignore_patterns('runs','upstream','__pycache__','.git'))
                p=root/'experiments/brain-four-pn-readout/protocol.json'
                d=json.loads(p.read_text())
                if field=='OFF_input':d['external_gate_input']['feedback_from_PN_activity']=True
                else:d['criteria']['peak_ratio']=0.01
                p.write_text(json.dumps(d))
                with patch.object(experiment,'ROOT',root),patch('experiment.subprocess.run') as launch:
                    with self.assertRaises(ValueError):experiment.run(2026091701,1.,'known_positive')
                    launch.assert_not_called()

    def test_no_record_overwrite(self):
        with patch('experiment.subprocess.run') as launch:
            with self.assertRaises(ValueError):
                experiment.run(2026091701,1.,'control',out=experiment.ROOT/'experiments'/'brain-four-pn-readout')
            launch.assert_not_called()
        with tempfile.TemporaryDirectory() as tmp:
            with patch('experiment.subprocess.run') as launch:
                with self.assertRaises(FileExistsError):experiment.run(2026091701,1.,'control',out=tmp)
                launch.assert_not_called()

if __name__=='__main__':unittest.main()
