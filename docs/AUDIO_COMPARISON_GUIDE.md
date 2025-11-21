# Audio Comparison Module - User Guide

## Overview

The Audio Comparison Module provides comprehensive audio file comparison capabilities for conformance testing and quality assurance. It analyzes audio properties, computes similarity scores, and identifies differences between baseline and current audio files.

## Features

- **Audio Property Analysis**: Extract and compare duration, sample rate, channels, and format
- **Spectral Analysis**: MFCC-based similarity scoring for audio content comparison
- **Format Support**: WAV, MP3, FLAC, OGG, M4A, and other common audio formats
- **Detailed Reporting**: Comprehensive comparison results with issues and recommendations
- **Web UI**: User-friendly interface for uploading and comparing audio files
- **REST API**: Programmatic access for automation and integration

## Quick Start

### Using the Web Interface

1. **Navigate to Audio Module**
   - Visit `http://127.0.0.1:8000/audio` in your browser
   - Click "🎧 Compare Audio Files"

2. **Upload Audio Files**
   - Enter a test name (required)
   - Add an optional description
   - Select baseline audio file
   - Select current audio file
   - Click "🎵 Compare Audio Files"

3. **View Results**
   - System processes audio files (may take a moment for large files)
   - Redirects to comparison results page
   - View similarity score, property comparisons, and detailed differences

### Using the REST API

#### Compare Audio Files

```bash
# Using curl
curl -X POST "http://127.0.0.1:8000/audio/compare" \
  -H "Content-Type: multipart/form-data" \
  -F "baseline_file=@baseline.wav" \
  -F "current_file=@current.wav" \
  -F "test_name=Audio Quality Test" \
  -F "description=Comparing audio quality"
```

```python
# Using Python requests
import requests

files = {
    'baseline_file': open('baseline.wav', 'rb'),
    'current_file': open('current.wav', 'rb')
}
data = {
    'test_name': 'Audio Quality Test',
    'description': 'Comparing audio quality'
}

response = requests.post(
    'http://127.0.0.1:8000/audio/compare',
    files=files,
    data=data
)
print(response.json())
```

#### Get Comparison Results

```bash
curl -X GET "http://127.0.0.1:8000/audio/api/comparisons/1"
```

#### List Comparisons

```bash
# List all comparisons (paginated)
curl -X GET "http://127.0.0.1:8000/audio/api/comparisons?page=1&page_size=20"

# Filter by status
curl -X GET "http://127.0.0.1:8000/audio/api/comparisons?status=COMPLETED"

# Filter by test name
curl -X GET "http://127.0.0.1:8000/audio/api/comparisons?test_name=Quality"
```

#### Delete Comparison

```bash
curl -X DELETE "http://127.0.0.1:8000/audio/api/comparisons/1"
```

## Comparison Metrics

### Audio Properties

The module compares the following audio properties:

1. **Duration**
   - Measured in seconds
   - Match criteria:
     - `EXACT`: Difference < 0.01 seconds
     - `CLOSE`: Difference < 0.1 seconds
     - `DIFFERENT`: Difference ≥ 0.1 seconds

2. **Sample Rate**
   - Measured in Hz (e.g., 44100 Hz, 48000 Hz)
   - Match criteria:
     - `MATCH`: Identical sample rates
     - `MISMATCH`: Different sample rates

3. **Channels**
   - Number of audio channels (1=mono, 2=stereo)
   - Match criteria:
     - `MATCH`: Same channel count
     - `MISMATCH`: Different channel count

4. **Format**
   - Audio file format (WAV, MP3, FLAC, etc.)
   - Match criteria:
     - `MATCH`: Same format
     - `MISMATCH`: Different format

### Similarity Score

The similarity score (0-100%) measures how similar the audio content is:

- **Algorithm**: MFCC (Mel-Frequency Cepstral Coefficients) based comparison
- **90-100%**: Very similar (likely identical or near-identical content)
- **70-89%**: Similar (same content with minor variations)
- **50-69%**: Somewhat similar (related content)
- **0-49%**: Different (significantly different content)

**Note**: Files are automatically resampled to the same sample rate for comparison.

### Overall Match Status

- **MATCH**: All properties match and high similarity (≥90%)
- **PARTIAL_MATCH**: Some properties match or moderate similarity (70-89%)
- **MISMATCH**: Multiple property mismatches or low similarity (<70%)

## Response Schema

### AudioComparisonResponse

```json
{
  "id": 1,
  "test_name": "Audio Quality Test",
  "description": "Comparing audio quality",
  "status": "COMPLETED",
  "baseline_filename": "baseline.wav",
  "current_filename": "current.wav",
  "baseline_duration": 10.5,
  "current_duration": 10.5,
  "baseline_sample_rate": 44100,
  "current_sample_rate": 44100,
  "baseline_channels": 2,
  "current_channels": 2,
  "baseline_format": "WAV",
  "current_format": "WAV",
  "similarity_score": 95.5,
  "duration_match": "EXACT",
  "format_match": "MATCH",
  "sample_rate_match": "MATCH",
  "channels_match": "MATCH",
  "summary": {
    "overall_match": "MATCH",
    "similarity_score": 95.5,
    "duration_match": "EXACT",
    "format_match": "MATCH",
    "sample_rate_match": "MATCH",
    "channels_match": "MATCH",
    "issues_found": 0,
    "issues": [],
    "recommendations": null
  },
  "differences": [],
  "created_at": "2025-01-03T12:00:00",
  "completed_at": "2025-01-03T12:00:05"
}
```

## Common Use Cases

### 1. Audio Quality Verification

Compare production audio against reference audio to verify quality:

```python
import requests

files = {
    'baseline_file': open('reference_track.wav', 'rb'),
    'current_file': open('production_track.wav', 'rb')
}
data = {
    'test_name': 'Production Quality Check',
    'description': 'Verify production audio matches reference'
}

response = requests.post(
    'http://127.0.0.1:8000/audio/compare',
    files=files,
    data=data
)

result = response.json()
if result['similarity_score'] >= 90:
    print("✓ Audio quality verified")
else:
    print(f"⚠ Low similarity: {result['similarity_score']}%")
```

### 2. Format Conversion Validation

Verify audio format conversion maintains quality:

```python
# Compare original WAV to converted MP3
files = {
    'baseline_file': open('original.wav', 'rb'),
    'current_file': open('converted.mp3', 'rb')
}
data = {
    'test_name': 'Format Conversion Test',
    'description': 'Verify MP3 conversion quality'
}

response = requests.post(
    'http://127.0.0.1:8000/audio/compare',
    files=files,
    data=data
)

result = response.json()
print(f"Format match: {result['format_match']}")
print(f"Similarity: {result['similarity_score']}%")
```

### 3. Batch Comparison

Compare multiple audio files:

```python
import os
import requests

baseline_dir = 'baseline_audio/'
current_dir = 'current_audio/'

for filename in os.listdir(baseline_dir):
    if filename.endswith('.wav'):
        files = {
            'baseline_file': open(os.path.join(baseline_dir, filename), 'rb'),
            'current_file': open(os.path.join(current_dir, filename), 'rb')
        }
        data = {
            'test_name': f'Batch Test - {filename}',
            'description': f'Automated comparison for {filename}'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/audio/compare',
            files=files,
            data=data
        )
        
        result = response.json()
        print(f"{filename}: {result['summary']['overall_match']}")
```

## Tips and Best Practices

### 1. File Format Selection

- **WAV**: Lossless format, best for reference audio
- **MP3**: Lossy compression, good for storage optimization
- **FLAC**: Lossless compression, balanced quality and size
- Use consistent formats for most accurate comparisons

### 2. Sample Rate Considerations

- Higher sample rates (48000 Hz) capture more detail but increase file size
- 44100 Hz is standard for music
- System automatically resamples for comparison if rates differ

### 3. Channel Configuration

- Mono (1 channel): Suitable for voice recordings
- Stereo (2 channels): Standard for music and most audio
- Mismatched channels may indicate processing issues

### 4. Similarity Score Interpretation

- **95-100%**: Excellent match, likely identical content
- **85-94%**: Very good match, minor variations acceptable
- **70-84%**: Fair match, review for significant differences
- **Below 70%**: Poor match, investigate root cause

### 5. Performance Optimization

- Large files may take longer to process
- Consider downsampling high sample rate files if exact quality isn't critical
- Use pagination when listing many comparisons

## Troubleshooting

### Error: "Failed to extract audio properties"

**Cause**: Unsupported or corrupt audio file

**Solution**:
- Verify file format is supported (WAV, MP3, FLAC, OGG, M4A)
- Check file is not corrupted
- Try converting file with audio editing software

### Error: Low Similarity Score Despite Identical Files

**Cause**: Different sample rates or significant format differences

**Solution**:
- Check audio properties (sample rate, channels, format)
- Convert files to same format before comparison
- Review differences list for specific issues

### Issue: Comparison Takes Too Long

**Cause**: Large file size or high sample rate

**Solution**:
- Use shorter audio clips for testing
- Downsample high sample rate files
- Consider using lower quality preview files for initial comparison

## API Reference

### POST /audio/compare

Compare two audio files.

**Request**:
- `baseline_file` (file, required): Baseline audio file
- `current_file` (file, required): Current audio file
- `test_name` (string, required): Name of the test
- `description` (string, optional): Description of the comparison

**Response**: `AudioComparisonResponse`

### GET /audio/api/comparisons

List audio comparisons with pagination.

**Query Parameters**:
- `page` (int, default: 1): Page number
- `page_size` (int, default: 20): Items per page
- `status` (string, optional): Filter by status
- `test_name` (string, optional): Filter by test name

**Response**: `AudioComparisonListResponse`

### GET /audio/api/comparisons/{comparison_id}

Get audio comparison by ID.

**Response**: `AudioComparisonResponse`

### DELETE /audio/api/comparisons/{comparison_id}

Delete audio comparison.

**Response**: `{"message": "Comparison deleted successfully"}`

## Additional Resources

- API Documentation: `http://127.0.0.1:8000/api/docs`
- Module Home: `http://127.0.0.1:8000/audio`
- Source Code: `app/modules/audio_compare/`
- Tests: `tests/test_audio_compare.py`
