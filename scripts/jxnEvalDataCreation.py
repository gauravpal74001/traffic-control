from datetime import datetime, timedelta
from moviepy.video.io import ffmpeg_tools
import subprocess


def subtract_timestamps(timestamp1, timestamp2):
    time_format = "%H:%M:%S"
    dt1 = datetime.strptime(timestamp1, time_format)
    dt2 = datetime.strptime(timestamp2, time_format)
    time_difference = dt1 - dt2
    total_seconds = time_difference.total_seconds()
    return total_seconds



def mainFunc(videoSource,cycle,finalpath):
    import os
    
    offSetConstant = 1
    start_time_stamp = 0
    i = 0
    
    # Handle both Windows and Unix path separators
    normalized_source = videoSource.replace('\\', '/')
    normalized_finalpath = finalpath.replace('\\', '/')
    
    # Ensure finalpath ends with proper separator
    if not normalized_finalpath.endswith('/'):
        normalized_finalpath += '/'
    
    print("Processing video:", videoSource)
    print("Output directory:", normalized_finalpath)
    print("Cycle lengths:", cycle)
    print("Number of cycles:", len(cycle))
    
    while (True):
        index = i%len(cycle)
        slice_end = start_time_stamp+(cycle[index]/offSetConstant)
        if (slice_end>1290):
            break
        
        # Use proper path joining for cross-platform compatibility
        clip_name = os.path.join(normalized_finalpath, f"clip{i}.mp4")
        
        try:
            ffmpeg_tools.ffmpeg_extract_subclip(videoSource, start_time_stamp, slice_end, clip_name)
            print(f"Created clip {i}: clip{i}.mp4 ({start_time_stamp}s - {slice_end}s)")
        except Exception as e:
            print(f"Error creating clip {i}: {str(e)}")
            break
        
        i+=1
        start_time_stamp = slice_end
    
    print(f"Dataset creation complete! Created {i} clips in {normalized_finalpath}")


