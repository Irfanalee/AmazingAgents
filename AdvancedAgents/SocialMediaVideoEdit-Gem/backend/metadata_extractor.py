import ffmpeg
import os
from datetime import datetime

class MetadataExtractor:
    def extract_metadata(self, video_path: str):
        """
        Extract video metadata using ffprobe.
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            # Calculate duration
            duration = float(probe['format'].get('duration', 0))
            
            # Get file stats
            file_stats = os.stat(video_path)
            file_size = file_stats.st_size
            upload_time = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            
            metadata = {
                'filename': os.path.basename(video_path),
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'duration': duration,
                'duration_formatted': self._format_duration(duration),
                'upload_time': upload_time,
                'format': probe['format'].get('format_name', 'unknown'),
            }
            
            if video_stream:
                metadata.update({
                    'width': video_stream.get('width'),
                    'height': video_stream.get('height'),
                    'codec': video_stream.get('codec_name'),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'bitrate': int(video_stream.get('bit_rate', 0)),
                })
            
            if audio_stream:
                metadata.update({
                    'audio_codec': audio_stream.get('codec_name'),
                    'audio_channels': audio_stream.get('channels'),
                    'audio_sample_rate': audio_stream.get('sample_rate'),
                })
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                'filename': os.path.basename(video_path),
                'error': str(e)
            }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
