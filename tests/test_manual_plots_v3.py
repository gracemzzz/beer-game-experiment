"""Synthetic plot controls only; none of these figures are study findings."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.manual_plots_v3 import plot_analysis


class ManualPlotTests(unittest.TestCase):
    def test_no_matched_data_creates_no_figures(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "empty_analysis"
            self.assertEqual(plot_analysis({"primary": [{"n_pairs": 0, "mean_difference": None}]}, output), [])
            self.assertFalse(output.exists())

    def test_only_actual_endpoint_gets_three_formats_and_interim_counts(self):
        result = dict(source_kind="synthetic_software_control", collection_kind="development",
                      all_planned_games_complete=False,
                      primary=[dict(model="synthetic_only", hypothesis="H1", n_pairs=3, planned_blocks=40,
                                    mean_difference=0., ci95_low=-.1, ci95_high=.1, planned_sample_complete=False),
                               dict(model="missing", hypothesis="H2", n_pairs=0, mean_difference=None)],
                      sweeps=[dict(model="synthetic_only", hypothesis="H1", n_pairs=3, planned_blocks=10,
                                   mean_difference=0.)])
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            artifacts = plot_analysis(result, output)
            self.assertEqual(len(artifacts), 1)
            artifact = artifacts[0]
            self.assertEqual(artifact["status"], "INTERIM")
            self.assertEqual(artifact["data_kind"], "SYNTHETIC SOFTWARE CONTROL")
            self.assertEqual(artifact["matched_blocks"], {"synthetic_only": 3})
            self.assertEqual(artifact["prefix_counts"], {"synthetic_only": {"10": 3}})
            for extension, path in artifact["files"].items():
                self.assertFalse(Path(path).is_absolute())
                self.assertTrue((output / path).is_file())
                self.assertGreater((output / path).stat().st_size, 1000)
            self.assertFalse((output / "figures/H2.png").exists())
            before = {p.name: p.read_bytes() for p in (output / "figures").iterdir()}
            self.assertEqual(plot_analysis(result, output), artifacts)
            self.assertEqual({p.name: p.read_bytes() for p in (output / "figures").iterdir()}, before)
            changed = copy.deepcopy(result)
            changed["primary"][0]["mean_difference"] = 1.
            with self.assertRaises(ValueError):
                plot_analysis(changed, output)
            png = output / artifact["files"]["png"]
            png.write_bytes(png.read_bytes() + b"SYNTHETIC TAMPER")
            with self.assertRaises(ValueError):
                plot_analysis(result, output)


if __name__ == "__main__":
    unittest.main()
