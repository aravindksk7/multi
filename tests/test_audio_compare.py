"""Tests for audio comparison module."""
import pytest
import base64
import os
import wave
import struct
from sqlalchemy.orm import Session

from app.modules.audio_compare import (
    AudioComparator,
    AudioCompareRequest,
    AudioComparison,
    AudioComparisonStatus
)


def create_test_wav_file(filename: str, duration: float = 1.0, sample_rate: int = 44100, channels: int = 1) -> bytes:
    """
    Create a simple test WAV file in memory.
    
    Args:
        filename: Filename (for reference)
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        channels: Number of channels
        
    Returns:
        WAV file as bytes
    """
    import io
    
    # Generate sine wave
    num_samples = int(duration * sample_rate)
    frequency = 440.0  # A4 note
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            sample = int(32767.0 * 0.3 * (i % 1000) / 1000.0)  # Simple sawtooth wave
            packed_sample = struct.pack('<h', sample)
            for _ in range(channels):
                wav_file.writeframes(packed_sample)
    
    buffer.seek(0)
    return buffer.read()


class TestAudioComparison:
    """Test audio comparison functionality."""
    
    def test_create_identical_audio_comparison(self, db_session: Session):
        """Test comparing identical audio files."""
        # Create identical test audio files
        audio_data = create_test_wav_file("test.wav", duration=1.0, sample_rate=44100, channels=1)
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Create comparison request
        request = AudioCompareRequest(
            baseline_audio=audio_b64,
            current_audio=audio_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Identical Audio Test",
            description="Testing identical audio files"
        )
        
        # Perform comparison
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        
        # Verify results
        assert comparison is not None
        assert comparison.id is not None
        assert comparison.test_name == "Identical Audio Test"
        assert comparison.status == AudioComparisonStatus.COMPLETED
        assert comparison.similarity_score is not None
        assert comparison.similarity_score > 95.0  # Should be very similar
        assert comparison.duration_match in ["EXACT", "CLOSE"]
        assert comparison.sample_rate_match == "MATCH"
        assert comparison.channels_match == "MATCH"
        assert comparison.format_match == "MATCH"
    
    def test_create_different_duration_comparison(self, db_session: Session):
        """Test comparing audio files with different durations."""
        # Create audio files with different durations
        baseline_data = create_test_wav_file("baseline.wav", duration=1.0)
        current_data = create_test_wav_file("current.wav", duration=2.0)
        
        baseline_b64 = base64.b64encode(baseline_data).decode('utf-8')
        current_b64 = base64.b64encode(current_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=baseline_b64,
            current_audio=current_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Different Duration Test"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        
        assert comparison.status == AudioComparisonStatus.COMPLETED
        assert comparison.baseline_duration < comparison.current_duration
        assert comparison.duration_match == "DIFFERENT"
    
    def test_create_different_sample_rate_comparison(self, db_session: Session):
        """Test comparing audio files with different sample rates."""
        baseline_data = create_test_wav_file("baseline.wav", sample_rate=44100)
        current_data = create_test_wav_file("current.wav", sample_rate=48000)
        
        baseline_b64 = base64.b64encode(baseline_data).decode('utf-8')
        current_b64 = base64.b64encode(current_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=baseline_b64,
            current_audio=current_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Different Sample Rate Test"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        
        assert comparison.status == AudioComparisonStatus.COMPLETED
        assert comparison.baseline_sample_rate == 44100
        assert comparison.current_sample_rate == 48000
        assert comparison.sample_rate_match == "MISMATCH"
    
    def test_create_different_channels_comparison(self, db_session: Session):
        """Test comparing audio files with different channel counts."""
        baseline_data = create_test_wav_file("baseline.wav", channels=1)
        current_data = create_test_wav_file("current.wav", channels=2)
        
        baseline_b64 = base64.b64encode(baseline_data).decode('utf-8')
        current_b64 = base64.b64encode(current_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=baseline_b64,
            current_audio=current_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Different Channels Test"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        
        assert comparison.status == AudioComparisonStatus.COMPLETED
        assert comparison.baseline_channels == 1
        assert comparison.current_channels == 2
        assert comparison.channels_match == "MISMATCH"
    
    def test_get_comparison(self, db_session: Session):
        """Test retrieving a comparison by ID."""
        # Create a comparison first
        audio_data = create_test_wav_file("test.wav")
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=audio_b64,
            current_audio=audio_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Test Get Comparison"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        comparison_id = comparison.id
        
        # Retrieve the comparison
        retrieved = comparator.get_comparison(comparison_id, db_session)
        
        assert retrieved is not None
        assert retrieved.id == comparison_id
        assert retrieved.test_name == "Test Get Comparison"
    
    def test_list_comparisons(self, db_session: Session):
        """Test listing comparisons with pagination."""
        audio_data = create_test_wav_file("test.wav")
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        comparator = AudioComparator()
        
        # Create multiple comparisons
        for i in range(5):
            request = AudioCompareRequest(
                baseline_audio=audio_b64,
                current_audio=audio_b64,
                baseline_filename=f"baseline_{i}.wav",
                current_filename=f"current_{i}.wav",
                test_name=f"Test Comparison {i}"
            )
            comparator.compare_audio_files(request, db_session)
        
        # List comparisons
        comparisons, total = comparator.list_comparisons(db_session, skip=0, limit=3)
        
        assert total == 5
        assert len(comparisons) == 3
    
    def test_list_comparisons_filter_by_status(self, db_session: Session):
        """Test filtering comparisons by status."""
        audio_data = create_test_wav_file("test.wav")
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=audio_b64,
            current_audio=audio_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Completed Test"
        )
        
        comparator = AudioComparator()
        comparator.compare_audio_files(request, db_session)
        
        # Filter by status
        comparisons, total = comparator.list_comparisons(
            db_session,
            status=AudioComparisonStatus.COMPLETED.value
        )
        
        assert total > 0
        assert all(c.status == AudioComparisonStatus.COMPLETED for c in comparisons)
    
    def test_list_comparisons_filter_by_test_name(self, db_session: Session):
        """Test filtering comparisons by test name."""
        audio_data = create_test_wav_file("test.wav")
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=audio_b64,
            current_audio=audio_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Special Test Name XYZ"
        )
        
        comparator = AudioComparator()
        comparator.compare_audio_files(request, db_session)
        
        # Filter by test name
        comparisons, total = comparator.list_comparisons(
            db_session,
            test_name="Special"
        )
        
        assert total > 0
        assert all("Special" in c.test_name for c in comparisons)
    
    def test_delete_comparison(self, db_session: Session):
        """Test deleting a comparison."""
        audio_data = create_test_wav_file("test.wav")
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=audio_b64,
            current_audio=audio_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Test Delete"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        comparison_id = comparison.id
        
        # Delete the comparison
        success = comparator.delete_comparison(comparison_id, db_session)
        
        assert success is True
        
        # Verify deletion
        deleted = comparator.get_comparison(comparison_id, db_session)
        assert deleted is None
    
    def test_delete_nonexistent_comparison(self, db_session: Session):
        """Test deleting a non-existent comparison."""
        comparator = AudioComparator()
        success = comparator.delete_comparison(99999, db_session)
        
        assert success is False
    
    def test_comparison_summary_generation(self, db_session: Session):
        """Test summary generation with various mismatches."""
        # Create audio with multiple differences
        baseline_data = create_test_wav_file("baseline.wav", duration=1.0, sample_rate=44100, channels=1)
        current_data = create_test_wav_file("current.wav", duration=2.0, sample_rate=48000, channels=2)
        
        baseline_b64 = base64.b64encode(baseline_data).decode('utf-8')
        current_b64 = base64.b64encode(current_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=baseline_b64,
            current_audio=current_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Summary Test"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        
        assert comparison.summary is not None
        assert "overall_match" in comparison.summary
        assert "issues_found" in comparison.summary
        assert comparison.summary["issues_found"] > 0
        assert "issues" in comparison.summary
        assert len(comparison.summary["issues"]) > 0
    
    def test_differences_tracking(self, db_session: Session):
        """Test detailed differences tracking."""
        baseline_data = create_test_wav_file("baseline.wav", sample_rate=44100)
        current_data = create_test_wav_file("current.wav", sample_rate=48000)
        
        baseline_b64 = base64.b64encode(baseline_data).decode('utf-8')
        current_b64 = base64.b64encode(current_data).decode('utf-8')
        
        request = AudioCompareRequest(
            baseline_audio=baseline_b64,
            current_audio=current_b64,
            baseline_filename="baseline.wav",
            current_filename="current.wav",
            test_name="Differences Test"
        )
        
        comparator = AudioComparator()
        comparison = comparator.compare_audio_files(request, db_session)
        
        assert comparison.differences is not None
        assert len(comparison.differences) > 0
        
        # Check for sample rate difference
        sample_rate_diff = next(
            (d for d in comparison.differences if d["property"] == "sample_rate"),
            None
        )
        assert sample_rate_diff is not None
        assert "44100" in sample_rate_diff["baseline_value"]
        assert "48000" in sample_rate_diff["current_value"]
