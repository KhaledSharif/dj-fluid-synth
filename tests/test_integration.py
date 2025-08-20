"""Integration tests for the full YAML to WAV pipeline"""

import unittest
import sys
import os
import tempfile
import yaml
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import generate_edm_from_yaml, validate_yaml_config


class TestIntegration(unittest.TestCase):
    """Test full integration of YAML validation and generation"""
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_valid_yaml_generation(self):
        """Test that valid YAML generates WAV successfully"""
        yaml_content = {
            "tempo": 128,
            "sample_rate": 44100,
            "sections": [
                {
                    "name": "test",
                    "bars": 1,
                    "tracks": [
                        {
                            "type": "kick",
                            "pattern": [1, 0, 0, 0],
                            "volume": 0.8
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.test_dir, "test.yml")
        wav_path = os.path.join(self.test_dir, "test.wav")
        
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)
        
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_out:
            generate_edm_from_yaml(yaml_path, wav_path)
            output = fake_out.getvalue()
        
        # Check validation passed message
        self.assertIn("✓ YAML validation passed", output)
        # Check file was created
        self.assertTrue(os.path.exists(wav_path))
    
    def test_invalid_yaml_exits(self):
        """Test that invalid YAML exits with error message"""
        yaml_content = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "D4"],
                            "durations": [10, 10],  # Exceeds 8 beats
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.test_dir, "invalid.yml")
        wav_path = os.path.join(self.test_dir, "invalid.wav")
        
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)
        
        # Capture stdout and expect sys.exit
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                generate_edm_from_yaml(yaml_path, wav_path)
            output = fake_out.getvalue()
        
        # Check exit code is 1
        self.assertEqual(cm.exception.code, 1)
        # Check error message format
        self.assertIn("❌ YAML validation failed", output)
        self.assertIn("exceeds section length", output)
        # Check file was not created
        self.assertFalse(os.path.exists(wav_path))
    
    def test_warnings_displayed(self):
        """Test that warnings are displayed but don't stop generation"""
        yaml_content = {
            "tempo": 250,  # Unusual tempo
            "sidechain": True,
            "sidechain_style": "unknown",  # Unknown style
            "sections": [
                {
                    "name": "test",
                    "bars": 1,
                    "tracks": []  # Empty tracks warning
                }
            ]
        }
        
        yaml_path = os.path.join(self.test_dir, "warnings.yml")
        wav_path = os.path.join(self.test_dir, "warnings.wav")
        
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)
        
        # Capture stdout
        with patch('sys.stdout', new=StringIO()) as fake_out:
            generate_edm_from_yaml(yaml_path, wav_path)
            output = fake_out.getvalue()
        
        # Check warnings are displayed
        self.assertIn("Warning: Unusual tempo", output)
        self.assertIn("Warning: Unknown sidechain_style", output)
        self.assertIn("Warning:", output)
        # Check validation still passed
        self.assertIn("✓ YAML validation passed", output)
        # Check file was created despite warnings
        self.assertTrue(os.path.exists(wav_path))
    
    def test_multiple_errors_reported(self):
        """Test that multiple validation errors are all reported"""
        yaml_content = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "InvalidNote", "Z9"],
                            "durations": [2, 2],  # Mismatch with notes
                            "volume": 1.5  # Invalid volume
                        },
                        {
                            "type": "kick",
                            "pattern": [1, 0, 2, -1],  # Invalid velocities
                            "volume": -0.5  # Invalid volume
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.test_dir, "multi_error.yml")
        wav_path = os.path.join(self.test_dir, "multi_error.wav")
        
        with open(yaml_path, "w") as f:
            yaml.dump(yaml_content, f)
        
        # Capture stdout and expect sys.exit
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as cm:
                generate_edm_from_yaml(yaml_path, wav_path)
            output = fake_out.getvalue()
        
        # Check multiple errors are reported
        self.assertIn("arrays don't match", output)
        self.assertIn("invalid note", output)
        self.assertIn("invalid volume", output)
        self.assertIn("velocity value", output)
        # Check error count
        self.assertIn("error(s):", output)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in validation"""
    
    def test_negative_frequency_note(self):
        """Test handling of notes that would produce negative frequency"""
        # This is an edge case that's hard to trigger since note_to_freq
        # doesn't return negative values normally
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 1,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C-1"],  # Very low octave
                            "durations": [4],
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        # Should handle gracefully without crashing
        self.assertIsNotNone(errors)
        self.assertIsNotNone(warnings)
    
    def test_complex_valid_config(self):
        """Test a complex but valid configuration"""
        config = {
            "tempo": 140,
            "sample_rate": 44100,
            "sidechain": True,
            "sidechain_style": "extreme",
            "sidechain_strength": 0.9,
            "sections": [
                {
                    "name": "intro",
                    "bars": 8,
                    "tracks": [
                        {
                            "type": "kick",
                            "pattern": [1, 0, 0.8, 0, 1, 0, 0.8, 0],
                            "volume": 0.9
                        },
                        {
                            "type": "melody",
                            "notes": ["C4", "rest", "E4", "G4", "rest", "C5"],
                            "durations": [4, 2, 4, 4, 2, 16],
                            "volume": 0.7
                        },
                        {
                            "type": "pitch_bend_bass",
                            "notes": ["A1", "A1"],
                            "bend_notes": ["A#1", "G1"],
                            "durations": [16, 16],
                            "volume": 0.8
                        }
                    ]
                },
                {
                    "name": "drop",
                    "bars": 16,
                    "tracks": [
                        {
                            "type": "supersaw",
                            "notes": ["E4", "F4", "G4", "A4"],
                            "durations": [16, 16, 16, 16],
                            "volume": 1.0
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertEqual(errors, [])
        # May have warnings about durations, but no errors
        self.assertIsNotNone(warnings)


if __name__ == "__main__":
    unittest.main()