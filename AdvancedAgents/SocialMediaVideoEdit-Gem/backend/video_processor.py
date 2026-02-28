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
                .output(output_path, vcodec='libx264', preset='fast', crf=23, acodec='aac')
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error cutting video: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False

    def concatenate_videos(self, video_paths: list, output_path: str):
        """
        Concatenates multiple video files, including audio (v=1, a=1).
        """
        try:
            print(f"Concatenating {len(video_paths)} videos to {output_path}")
            inputs = [ffmpeg.input(path) for path in video_paths]
            # concat with v=1,a=1 needs interleaved [v0, a0, v1, a1, ...]
            streams = []
            for inp in inputs:
                streams.append(inp.video)
                streams.append(inp.audio)
            (
                ffmpeg
                .concat(*streams, v=1, a=1)
                .output(output_path, vcodec='libx264', acodec='aac', preset='fast', crf=23)
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error concatenating: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False

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
