import ffmpeg
import os

class VideoProcessor:
    def __init__(self):
        pass

    def cut_video(self, input_path: str, start_time: int, end_time: int, output_path: str):
        """
        Cuts a segment from the video, preserving audio.
        """
        try:
            print(f"Cutting video: {input_path} from {start_time} to {end_time}")
            (
                ffmpeg
                .input(input_path, ss=start_time, to=end_time)
                .output(output_path, vcodec='copy', acodec='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error cutting video: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False

    def concatenate_videos(self, video_paths: list, output_path: str):
        """
        Concatenates multiple video files using the concat demuxer (stream copy, no re-encode).
        """
        filelist = output_path + "_filelist.txt"
        try:
            print(f"Concatenating {len(video_paths)} videos to {output_path}")
            with open(filelist, 'w') as f:
                for path in video_paths:
                    f.write(f"file '{os.path.abspath(path)}'\n")
            (
                ffmpeg
                .input(filelist, format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error concatenating: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False
        finally:
            if os.path.exists(filelist):
                os.remove(filelist)

    def cut_shorts(self, original_video: str, highlights: list, base_name: str) -> list:
        """
        Cuts each highlight as an individual short clip saved to processed/.
        Returns list of output file paths.
        """
        paths = []
        for i, highlight in enumerate(highlights):
            out = f"processed/{base_name}_short_{i+1}.mp4"
            if self.cut_video(original_video, highlight['start'], highlight['end'], out):
                paths.append(out)
                print(f"Short {i+1} saved: {out}")
        return paths

    def make_proxy(self, input_path: str, output_path: str) -> bool:
        """
        Creates a 480p proxy of the video for Gemini upload.
        Much smaller file = faster upload and faster Gemini processing.
        Original file is never modified — clips are still cut from the original.
        """
        try:
            print(f"Creating 480p proxy for Gemini: {output_path}")
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vf='scale=854:480:force_original_aspect_ratio=decrease',
                    vcodec='libx264',
                    preset='ultrafast',
                    crf=28,
                    acodec='aac',
                    b__a='64k',
                    ac=1,
                )
                .overwrite_output()
                .run(quiet=True)
            )
            proxy_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"Proxy created: {proxy_mb:.1f} MB")
            return True
        except ffmpeg.Error as e:
            print(f"Proxy creation failed: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False

    def compress_for_upload(self, input_path: str, output_path: str, target_size_gb: float = 1.8) -> bool:
        """
        Compress video to a target file size using H.265 for Gemini upload.
        Calculates the required bitrate from duration and target size.
        Original file is never modified.
        """
        try:
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
            # Reserve ~128 kbps for audio, rest goes to video
            target_bits = target_size_gb * 1024 * 1024 * 1024 * 8
            audio_bits = 128_000 * duration
            video_bitrate = int((target_bits - audio_bits) / duration)
            print(f"Compressing for upload: duration={duration:.1f}s, target={target_size_gb}GB, video_bitrate={video_bitrate//1000}kbps")
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec='libx265',
                    b__v=video_bitrate,
                    acodec='aac',
                    b__a='128k',
                    preset='fast',
                )
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Compression failed: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False

    def process_highlights(self, original_video: str, highlights: list, output_path: str):
        """
        Cuts each highlight and concatenates them into a single highlights reel.
        """
        temp_files = []
        try:
            for i, highlight in enumerate(highlights):
                temp_output = f"temp_highlight_{i}.mp4"
                if self.cut_video(original_video, highlight['start'], highlight['end'], temp_output):
                    temp_files.append(temp_output)

            if not temp_files:
                return False

            return self.concatenate_videos(temp_files, output_path)

        except Exception as e:
            print(f"Error processing highlights: {e}")
            return False
        finally:
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
