"""Test YAML generation and enhanced features."""

import unittest
import tempfile
import os
import yaml
import numpy as np
from scipy.io import wavfile
from main import generate_edm_from_yaml


class TestYAMLGeneration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_generate_simple_track(self):
        # Create a simple YAML file
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'kick',
                            'pattern': [1, 0, 1, 0]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'test.yml')
        wav_path = os.path.join(self.temp_dir, 'test.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        # Generate the track
        generate_edm_from_yaml(yaml_path, wav_path)
        
        # Check that WAV file was created
        self.assertTrue(os.path.exists(wav_path))
        
        # Load and check the WAV file
        fs, audio = wavfile.read(wav_path)
        self.assertEqual(fs, 44100)
        self.assertGreater(len(audio), 0)
        
    def test_generate_with_melody(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 2,
                    'tracks': [
                        {
                            'type': 'melody',
                            'notes': ['C4', 'D4', 'E4', 'G4'],
                            'durations': [1, 1, 1, 1]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'melody.yml')
        wav_path = os.path.join(self.temp_dir, 'melody.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_multiple_tracks(self):
        yaml_data = {
            'tempo': 128,
            'sample_rate': 44100,
            'sidechain': False,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'kick',
                            'pattern': [1, 0, 0, 0],
                            'volume': 0.8
                        },
                        {
                            'type': 'bass',
                            'notes': ['C2', 'E2', 'G2', 'C3'],
                            'durations': [1, 1, 1, 1],
                            'volume': 0.6
                        },
                        {
                            'type': 'pad',
                            'notes': ['C4', 'G4'],
                            'durations': [2, 2],
                            'volume': 0.4
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'multi.yml')
        wav_path = os.path.join(self.temp_dir, 'multi.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_sidechain(self):
        yaml_data = {
            'tempo': 128,
            'sample_rate': 44100,
            'sidechain': True,
            'sidechain_strength': 0.6,
            'sections': [
                {
                    'name': 'test',
                    'bars': 2,
                    'tracks': [
                        {
                            'type': 'kick',
                            'pattern': [1, 0, 0, 0]
                        },
                        {
                            'type': 'pad',
                            'notes': ['C4'],
                            'durations': [8]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'sidechain.yml')
        wav_path = os.path.join(self.temp_dir, 'sidechain.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_velocity(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'snare',
                            'pattern': [0.3, 0.5, 0.7, 1.0],  # Velocity pattern
                            'volume': 0.8
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'velocity.yml')
        wav_path = os.path.join(self.temp_dir, 'velocity.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))


class TestEnhancedFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_generate_with_supersaw(self):
        yaml_data = {
            'tempo': 128,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'supersaw',
                            'notes': ['C4', 'E4', 'G4'],
                            'durations': [1, 1, 2],
                            'detune': 0.03,
                            'voices': 7,
                            'volume': 0.5
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'supersaw.yml')
        wav_path = os.path.join(self.temp_dir, 'supersaw.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_flat_notes(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'melody',
                            'notes': ['Bb3', 'Eb4', 'Ab4', 'Db5'],
                            'durations': [1, 1, 1, 1]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'flats.yml')
        wav_path = os.path.join(self.temp_dir, 'flats.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_pitch_bend(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 2,
                    'tracks': [
                        {
                            'type': 'pitch_bend_bass',
                            'notes': ['C2', 'F2', 'G2', 'C3'],
                            'bend_notes': ['E2', 'G2', 'A2', 'C3'],
                            'durations': [1, 1, 1, 1],
                            'bass_style': 'pluck',
                            'volume': 0.7
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'pitch_bend.yml')
        wav_path = os.path.join(self.temp_dir, 'pitch_bend.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))


if __name__ == '__main__':
    unittest.main()