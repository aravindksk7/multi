"""Audio comparison service."""
import os
import base64
import tempfile
import librosa
import numpy as np
import soundfile as sf
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from .models import AudioComparison, AudioComparisonStatus
from .schemas import AudioCompareRequest, AudioComparisonSummary


class AudioComparator:
    """Service for comparing audio files."""
    
    def __init__(self):
        """Initialize audio comparator."""
        self.temp_dir = tempfile.gettempdir()
    
    def compare_audio_files(
        self,
        request: AudioCompareRequest,
        db: Session
    ) -> AudioComparison:
        """
        Compare two audio files for conformance.
        
        Args:
            request: Audio comparison request
            db: Database session
            
        Returns:
            AudioComparison record with results
        """
        # Create comparison record
        comparison = AudioComparison(
            test_name=request.test_name,
            description=request.description,
            baseline_filename=request.baseline_filename,
            current_filename=request.current_filename,
            status=AudioComparisonStatus.PROCESSING,
            started_at=datetime.utcnow()
        )
        
        db.add(comparison)
        db.commit()
        db.refresh(comparison)
        
        try:
            # Decode and save audio files temporarily
            baseline_path = self._save_audio_file(
                request.baseline_audio,
                request.baseline_filename
            )
            current_path = self._save_audio_file(
                request.current_audio,
                request.current_filename
            )
            
            comparison.baseline_file_path = baseline_path
            comparison.current_file_path = current_path
            
            # Extract audio properties
            baseline_props = self._extract_audio_properties(baseline_path)
            current_props = self._extract_audio_properties(current_path)
            
            # Store properties
            comparison.baseline_duration = baseline_props.get("duration")
            comparison.current_duration = current_props.get("duration")
            comparison.baseline_sample_rate = baseline_props.get("sample_rate")
            comparison.current_sample_rate = current_props.get("sample_rate")
            comparison.baseline_channels = baseline_props.get("channels")
            comparison.current_channels = current_props.get("channels")
            comparison.baseline_format = baseline_props.get("format")
            comparison.current_format = current_props.get("format")
            
            # Perform comparison
            comparison_results = self._compare_audio_properties(
                baseline_props,
                current_props
            )
            
            # Calculate audio similarity
            similarity = self._calculate_audio_similarity(
                baseline_path,
                current_path,
                baseline_props,
                current_props
            )
            
            comparison.similarity_score = similarity
            comparison.duration_match = comparison_results["duration_match"]
            comparison.format_match = comparison_results["format_match"]
            comparison.sample_rate_match = comparison_results["sample_rate_match"]
            comparison.channels_match = comparison_results["channels_match"]
            
            # Generate summary
            summary = self._generate_summary(comparison_results, similarity)
            differences = self._generate_differences(
                baseline_props,
                current_props,
                comparison_results
            )
            
            comparison.summary = summary
            comparison.differences = differences
            comparison.status = AudioComparisonStatus.COMPLETED
            comparison.completed_at = datetime.utcnow()
            
            # Cleanup temp files
            self._cleanup_file(baseline_path)
            self._cleanup_file(current_path)
            
        except Exception as e:
            comparison.status = AudioComparisonStatus.FAILED
            comparison.error_message = str(e)
            comparison.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(comparison)
        
        return comparison
    
    def _save_audio_file(self, audio_data: str, filename: str) -> str:
        """
        Save base64 encoded audio data to temporary file.
        
        Args:
            audio_data: Base64 encoded audio data
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Decode base64
        try:
            audio_bytes = base64.b64decode(audio_data)
        except:
            # If not base64, assume it's already binary or a path
            if os.path.exists(audio_data):
                return audio_data
            audio_bytes = audio_data.encode()
        
        # Create temp file with same extension
        _, ext = os.path.splitext(filename)
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=ext or '.wav',
            dir=self.temp_dir
        )
        
        temp_file.write(audio_bytes)
        temp_file.close()
        
        return temp_file.name
    
    def _extract_audio_properties(self, file_path: str) -> Dict[str, Any]:
        """
        Extract properties from audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary of audio properties
        """
        try:
            # Load audio with librosa
            y, sr = librosa.load(file_path, sr=None)
            
            # Get file info with soundfile
            info = sf.info(file_path)
            
            return {
                "duration": info.duration,
                "sample_rate": sr,
                "channels": info.channels,
                "format": info.format,
                "subtype": info.subtype,
                "samples": len(y),
                "rms_energy": float(np.sqrt(np.mean(y**2))),
                "zero_crossing_rate": float(np.mean(librosa.zero_crossings(y))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
            }
        except Exception as e:
            raise ValueError(f"Failed to extract audio properties: {str(e)}")
    
    def _compare_audio_properties(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Compare audio properties.
        
        Args:
            baseline: Baseline audio properties
            current: Current audio properties
            
        Returns:
            Comparison results
        """
        results = {}
        
        # Compare duration (tolerance: 0.1 seconds)
        duration_diff = abs(baseline["duration"] - current["duration"])
        if duration_diff < 0.01:
            results["duration_match"] = "EXACT"
        elif duration_diff < 0.1:
            results["duration_match"] = "CLOSE"
        else:
            results["duration_match"] = "DIFFERENT"
        
        # Compare format
        if baseline["format"] == current["format"]:
            results["format_match"] = "MATCH"
        else:
            results["format_match"] = "MISMATCH"
        
        # Compare sample rate
        if baseline["sample_rate"] == current["sample_rate"]:
            results["sample_rate_match"] = "MATCH"
        else:
            results["sample_rate_match"] = "MISMATCH"
        
        # Compare channels
        if baseline["channels"] == current["channels"]:
            results["channels_match"] = "MATCH"
        else:
            results["channels_match"] = "MISMATCH"
        
        return results
    
    def _calculate_audio_similarity(
        self,
        baseline_path: str,
        current_path: str,
        baseline_props: Dict[str, Any],
        current_props: Dict[str, Any]
    ) -> float:
        """
        Calculate audio similarity using spectral features.
        
        Args:
            baseline_path: Path to baseline audio
            current_path: Path to current audio
            baseline_props: Baseline properties
            current_props: Current properties
            
        Returns:
            Similarity score (0-100%)
        """
        try:
            # Load both audio files with same sample rate
            target_sr = min(baseline_props["sample_rate"], current_props["sample_rate"])
            y1, _ = librosa.load(baseline_path, sr=target_sr)
            y2, _ = librosa.load(current_path, sr=target_sr)
            
            # Make same length (pad shorter or trim longer)
            min_len = min(len(y1), len(y2))
            y1 = y1[:min_len]
            y2 = y2[:min_len]
            
            # Calculate MFCC features
            mfcc1 = librosa.feature.mfcc(y=y1, sr=target_sr, n_mfcc=13)
            mfcc2 = librosa.feature.mfcc(y=y2, sr=target_sr, n_mfcc=13)
            
            # Calculate cosine similarity
            mfcc1_flat = mfcc1.flatten()
            mfcc2_flat = mfcc2.flatten()
            
            # Normalize
            mfcc1_norm = mfcc1_flat / (np.linalg.norm(mfcc1_flat) + 1e-8)
            mfcc2_norm = mfcc2_flat / (np.linalg.norm(mfcc2_flat) + 1e-8)
            
            # Cosine similarity
            similarity = np.dot(mfcc1_norm, mfcc2_norm)
            
            # Convert to percentage (0-100)
            similarity_pct = (similarity + 1) * 50  # Map [-1, 1] to [0, 100]
            
            return round(float(similarity_pct), 2)
            
        except Exception as e:
            # If similarity calculation fails, return None
            return None
    
    def _generate_summary(
        self,
        comparison_results: Dict[str, str],
        similarity: Optional[float]
    ) -> Dict[str, Any]:
        """
        Generate comparison summary.
        
        Args:
            comparison_results: Comparison results
            similarity: Similarity score
            
        Returns:
            Summary dictionary
        """
        issues = []
        recommendations = []
        
        # Check duration
        if comparison_results["duration_match"] == "DIFFERENT":
            issues.append("Duration mismatch detected")
            recommendations.append("Verify audio processing pipeline for timing issues")
        
        # Check format
        if comparison_results["format_match"] == "MISMATCH":
            issues.append("Audio format mismatch")
            recommendations.append("Ensure consistent audio format encoding")
        
        # Check sample rate
        if comparison_results["sample_rate_match"] == "MISMATCH":
            issues.append("Sample rate mismatch")
            recommendations.append("Use consistent sample rate across recordings")
        
        # Check channels
        if comparison_results["channels_match"] == "MISMATCH":
            issues.append("Channel count mismatch")
            recommendations.append("Verify mono/stereo configuration")
        
        # Check similarity
        if similarity is not None and similarity < 70:
            issues.append("Low audio content similarity")
            recommendations.append("Review audio content differences")
        
        # Overall match
        if len(issues) == 0:
            overall = "MATCH"
        elif len(issues) <= 2:
            overall = "PARTIAL_MATCH"
        else:
            overall = "MISMATCH"
        
        return {
            "overall_match": overall,
            "similarity_score": similarity,
            "duration_match": comparison_results["duration_match"],
            "format_match": comparison_results["format_match"],
            "sample_rate_match": comparison_results["sample_rate_match"],
            "channels_match": comparison_results["channels_match"],
            "issues_found": len(issues),
            "issues": issues,
            "recommendations": recommendations if recommendations else None
        }
    
    def _generate_differences(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any],
        comparison_results: Dict[str, str]
    ) -> list[Dict[str, Any]]:
        """
        Generate detailed differences list.
        
        Args:
            baseline: Baseline properties
            current: Current properties
            comparison_results: Comparison results
            
        Returns:
            List of differences
        """
        differences = []
        
        # Duration difference
        if comparison_results["duration_match"] != "EXACT":
            differences.append({
                "property": "duration",
                "baseline_value": f"{baseline['duration']:.3f}s",
                "current_value": f"{current['duration']:.3f}s",
                "difference": f"{abs(baseline['duration'] - current['duration']):.3f}s",
                "status": comparison_results["duration_match"]
            })
        
        # Sample rate difference
        if comparison_results["sample_rate_match"] != "MATCH":
            differences.append({
                "property": "sample_rate",
                "baseline_value": f"{baseline['sample_rate']} Hz",
                "current_value": f"{current['sample_rate']} Hz",
                "status": "MISMATCH"
            })
        
        # Channels difference
        if comparison_results["channels_match"] != "MATCH":
            differences.append({
                "property": "channels",
                "baseline_value": baseline['channels'],
                "current_value": current['channels'],
                "status": "MISMATCH"
            })
        
        # Format difference
        if comparison_results["format_match"] != "MATCH":
            differences.append({
                "property": "format",
                "baseline_value": baseline['format'],
                "current_value": current['format'],
                "status": "MISMATCH"
            })
        
        return differences
    
    def _cleanup_file(self, file_path: str):
        """Remove temporary file."""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass  # Ignore cleanup errors
    
    def get_comparison(self, comparison_id: int, db: Session) -> Optional[AudioComparison]:
        """Get audio comparison by ID."""
        return db.query(AudioComparison).filter(
            AudioComparison.id == comparison_id
        ).first()
    
    def list_comparisons(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        test_name: Optional[str] = None
    ) -> Tuple[list[AudioComparison], int]:
        """List audio comparisons with filters."""
        query = db.query(AudioComparison)
        
        if status:
            query = query.filter(AudioComparison.status == status)
        if test_name:
            query = query.filter(AudioComparison.test_name.like(f"%{test_name}%"))
        
        total = query.count()
        comparisons = query.order_by(
            AudioComparison.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return comparisons, total
    
    def delete_comparison(self, comparison_id: int, db: Session) -> bool:
        """Delete audio comparison."""
        comparison = self.get_comparison(comparison_id, db)
        if comparison:
            # Cleanup files if they exist
            self._cleanup_file(comparison.baseline_file_path)
            self._cleanup_file(comparison.current_file_path)
            
            db.delete(comparison)
            db.commit()
            return True
        return False
