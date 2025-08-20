"""Test suite for YAML validation functionality"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_yaml_config


class TestYAMLValidation(unittest.TestCase):
    """Test YAML configuration validation"""
    
    def test_valid_config(self):
        """Test that valid configuration passes"""
        config = {
            "tempo": 128,
            "sample_rate": 44100,
            "sections": [
                {
                    "name": "intro",
                    "bars": 4,
                    "tracks": [
                        {
                            "type": "kick",
                            "pattern": [1, 0, 0, 0],
                            "volume": 0.8
                        },
                        {
                            "type": "melody",
                            "notes": ["C4", "D4", "E4", "F4"],
                            "durations": [4, 4, 4, 4],
                            "volume": 0.6
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
    
    def test_missing_required_fields(self):
        """Test detection of missing required fields"""
        # Missing tempo
        config = {"sections": []}
        errors, warnings = validate_yaml_config(config)
        self.assertIn("Missing required field: tempo", errors)
        
        # Missing sections
        config = {"tempo": 128}
        errors, warnings = validate_yaml_config(config)
        self.assertIn("Missing required field: sections", errors)
    
    def test_empty_sections(self):
        """Test detection of empty sections"""
        config = {
            "tempo": 128,
            "sections": []
        }
        errors, warnings = validate_yaml_config(config)
        self.assertIn("No sections defined in YAML", errors)
    
    def test_missing_bars_field(self):
        """Test detection of missing bars field in section"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "intro",
                    "tracks": []
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertIn("Section 'intro': missing 'bars' field", errors)
    
    def test_duration_exceeds_section(self):
        """Test detection of durations exceeding section length"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,  # 8 beats total
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "D4"],
                            "durations": [8, 8],  # 16 beats total
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("exceeds section length" in error for error in errors))
    
    def test_notes_durations_mismatch(self):
        """Test detection of notes/durations array length mismatch"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 4,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "D4", "E4"],
                            "durations": [4, 4],  # Only 2 durations for 3 notes
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("arrays don't match" in error for error in errors))
    
    def test_invalid_note_names(self):
        """Test detection of invalid note names"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "InvalidNote", "Z9"],
                            "durations": [2, 2, 2],
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        # Should have 2 errors for invalid notes
        invalid_note_errors = [e for e in errors if "invalid note" in e]
        self.assertEqual(len(invalid_note_errors), 2)
    
    def test_valid_rest_notes(self):
        """Test that 'rest' and empty string are valid notes"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "rest", "", "D4"],
                            "durations": [2, 2, 2, 2],
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        # Should not have errors for rest notes
        self.assertFalse(any("invalid note" in error for error in errors))
    
    def test_invalid_pattern_velocity(self):
        """Test detection of invalid pattern velocity values"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "kick",
                            "pattern": [1, 0, 2, -0.5],  # 2 and -0.5 are invalid
                            "volume": 0.8
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        velocity_errors = [e for e in errors if "velocity value" in e]
        self.assertEqual(len(velocity_errors), 2)
    
    def test_invalid_volume(self):
        """Test detection of invalid volume values"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "kick",
                            "pattern": [1, 0],
                            "volume": 1.5  # Invalid > 1
                        },
                        {
                            "type": "snare",
                            "pattern": [0, 1],
                            "volume": -0.1  # Invalid < 0
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        volume_errors = [e for e in errors if "invalid volume" in e]
        self.assertEqual(len(volume_errors), 2)
    
    def test_pitch_bend_mismatch(self):
        """Test detection of pitch bend notes mismatch"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "pitch_bend_bass",
                            "notes": ["A1", "B1", "C2"],
                            "bend_notes": ["A#1"],  # Only 1 bend note for 3 notes
                            "durations": [2, 2, 2],
                            "volume": 0.7
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("bend_notes" in error and "must match" in error for error in errors))
    
    def test_unusual_tempo_warning(self):
        """Test warning for unusual tempo values"""
        # Very slow tempo
        config = {
            "tempo": 50,
            "sections": [{"name": "test", "bars": 2, "tracks": []}]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("Unusual tempo" in warning for warning in warnings))
        
        # Very fast tempo
        config["tempo"] = 250
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("Unusual tempo" in warning for warning in warnings))
        
        # Normal tempo should not warn
        config["tempo"] = 128
        errors, warnings = validate_yaml_config(config)
        self.assertFalse(any("Unusual tempo" in warning for warning in warnings))
    
    def test_short_duration_warning(self):
        """Test warning for very short durations"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 8,  # 32 beats
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["C4", "D4"],
                            "durations": [4, 4],  # Only 8 beats (25% of section)
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("much shorter than section" in warning for warning in warnings))
    
    def test_pattern_division_warning(self):
        """Test warning for patterns that don't divide evenly"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 4,  # 16 beats
                    "tracks": [
                        {
                            "type": "kick",
                            "pattern": [1, 0, 1, 0, 1],  # 5 elements doesn't divide 16 evenly
                            "volume": 0.8
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("doesn't divide evenly" in warning for warning in warnings))
    
    def test_unknown_sidechain_style_warning(self):
        """Test warning for unknown sidechain style"""
        config = {
            "tempo": 128,
            "sidechain": True,
            "sidechain_style": "unknown_style",
            "sections": [{"name": "test", "bars": 2, "tracks": []}]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("Unknown sidechain_style" in warning for warning in warnings))
    
    def test_invalid_sidechain_strength(self):
        """Test detection of invalid sidechain strength"""
        config = {
            "tempo": 128,
            "sidechain": True,
            "sidechain_strength": 1.5,  # Invalid > 1
            "sections": [{"name": "test", "bars": 2, "tracks": []}]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("Invalid sidechain_strength" in error for error in errors))
    
    def test_empty_tracks_warning(self):
        """Test warning for sections with no tracks"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "empty_section",
                    "bars": 4,
                    "tracks": []
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        self.assertTrue(any("no tracks defined" in warning for warning in warnings))
    
    def test_flat_notes(self):
        """Test that flat notes (Bb, Ab, etc.) are valid"""
        config = {
            "tempo": 128,
            "sections": [
                {
                    "name": "test",
                    "bars": 2,
                    "tracks": [
                        {
                            "type": "melody",
                            "notes": ["Bb3", "Ab4", "Eb5", "Db2"],
                            "durations": [2, 2, 2, 2],
                            "volume": 0.5
                        }
                    ]
                }
            ]
        }
        errors, warnings = validate_yaml_config(config)
        # Should not have errors for flat notes
        self.assertFalse(any("invalid note" in error for error in errors))


if __name__ == "__main__":
    unittest.main()