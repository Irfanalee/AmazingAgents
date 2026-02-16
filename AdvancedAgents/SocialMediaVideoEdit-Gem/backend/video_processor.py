import ffmpeg
import os

class VideoProcessor:
    def __init__(self):
        pass

    def cut_video(self, input_path: str, start_time: int, end_time: int, output_path: str):
        """
        Cuts a segment from the video.
        """
        try:
            print(f"Cutting video: {input_path} from {start_time} to {end_time}")
            (
                ffmpeg
                .input(input_path, ss=start_time, to=end_time)
                .output(output_path, vcodec='libx264', preset='fast', crf=23, acodec='aac') # Re-encode for safety
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error cutting video: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            return False

    def concatenate_videos(self, video_paths: list, output_path: str):
        """
        Concatenates multiple video files.
        """
        try:
            print(f"Concatenating {len(video_paths)} videos to {output_path}")
            inputs = [ffmpeg.input(path) for path in video_paths]
            (
                ffmpeg
                .concat(*inputs)
                .output(output_path, c='copy') # Try copy first if codecs match
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error concatenating (copy failed, trying re-encode): {e}")
            # Fallback to re-encode if copy fails
            try:
                (
                    ffmpeg
                    .concat(*inputs)
                    .output(output_path, vcodec='libx264', preset='fast')
                    .overwrite_output()
                    .run(quiet=True)
                )
                return True
            except ffmpeg.Error as e2:
                print(f"Error concatenating (re-encode failed): {e2}")
                return False

    def process_highlights(self, original_video: str, highlights: list, output_path: str):
        """
        Main workflow: cut highlights, then stitch highlights + original.
        """
        temp_files = []
        try:
            # 1. Cut each highlight
            for i, highlight in enumerate(highlights):
                temp_output = f"temp_highlight_{i}.mp4"
                if self.cut_video(original_video, highlight['start'], highlight['end'], temp_output):
                    temp_files.append(temp_output)
            
            if not temp_files:
                return False

            # 2. Concatenate highlights + original
            # Note: Concatenating re-encoded clips with original might fail 'copy' if original is different.
            # Ideally we should re-encode original too or just the highlights.
            # For simplicity/speed, let's just concat highlights for now as the "teaser" 
            # OR if user really wants them attached to original, we list them all.
            
            all_files = temp_files + [original_video]
            
            # We need to be careful about formats. If original is distinct, concat might fail.
            # Let's try to concat just the highlights first as a "teaser" video, 
            # but the user asked to "put them at the start of video".
            
            # Let's assume we just make the "Teaser" video for now to avoid massive re-encoding of 1hr video.
            # Wait, user said "create a new video that i can upload".
            # If I re-encode 1hr video, it will take forever.
            # I will produce a "Highlights Only" video for now as it's more practical for "social media".
            # If they want the full thing, I can add it, but let's stick to highlights compilation.
            # Actually, re-reading: "put them at the start of video".
            # Okay, I will try to concat. If it fails or takes too long, that's a future optimization.
            # But to be safe, I will just output the highlights compilation as "highlights.mp4" 
            # and maybe the full one as "full_output.mp4".
            
            return self.concatenate_videos(all_files, output_path)

        except Exception as e:
            print(f"Error processing highlights: {e}")
            return False
        finally:
            # Cleanup temp files
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
