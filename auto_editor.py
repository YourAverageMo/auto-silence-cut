import subprocess
import json
from pprint import pprint
from datetime import datetime


# NOTE ChangeTimecode() is legacy code now use change_clip_colors() now.
def ChangeTimecode(timecode: str) -> str:
    """move play head back so GetCurrentVideoItem() returns most recent append clip. Appending clip after play head move does not overwrite clip from play head position

    Args:
        timecode (str):
        frames (int):

    Returns:
        str:
    """
    timecode = timecode.split(':')
    hours = int(timecode[0])
    minutes = int(timecode[1])
    seconds = int(timecode[2])
    frames = int(timecode[3]) - 1

    # Handle negative frames by borrowing from seconds
    if frames < 0:
        seconds -= 1
        frames += 60

    # Handle negative seconds by borrowing from minutes
    if seconds < 0:
        minutes -= 1
        seconds += 60

    # Handle negative minutes by borrowing from hours
    if minutes < 0:
        hours -= 1
        minutes += 60

    return "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds,
                                                frames)


def parse_timeline_json(timeline_dir: str, timeline_name: str,
                        total_frames: int) -> bool:
    r"""Takes a given {timeline_name} at {timeline_dir} and creates a new file {timeline_name}_parsed.json in the same dir. Adjusting the speed changes and fixing the mismatched frametimes.
    NOTE 'dur' = length of clip.
    'offset' = the source clip frame start time (NOT 'start').
    'speed' = 2 is the way the script knows what clip is silence.
    Setting speed to 2 messes with the 'start' 'offset' and 'dur' frames
    hence why we have to parse the json with this script.

    Args:
        timeline_dir (str): path to the timeline location to be parsed (excluding file name). i.e. C:\Program Files\\ 
        timeline_name (str): name of the timeline (excluding .JSON). This will also be used to give the new timeline created by this function.
        total_frames (int): total amount of frames in the timeline provided. used for the last subclip dur

    Returns:
        bool:
    """
    # Load the timeline JSON
    with open(f"{timeline_dir + timeline_name}.json", 'r') as f:
        timeline = json.load(f)

    # get number of audio tracks
    audio_track_count = len(timeline['a'])

    # Extract clips from the JSON
    timeline_clips = timeline.get('v', [])[0]

    # Init a list to hold adjusted clips
    adjusted_clips = []

    for i, clip in enumerate(timeline_clips):
        if clip['speed'] == 1.0:
            # Use the given values directly for speed 1.0
            adjusted_clips.append(clip)
        elif clip['speed'] == 2.0:
            # Calculate start and dur for speed 2.0
            previous_clip = timeline_clips[i - 1] if i > 0 else None
            next_clip = timeline_clips[
                i + 1] if i < len(timeline_clips) - 1 else None

            # Calculate new start
            if previous_clip:
                new_start = previous_clip['offset'] + previous_clip['dur']
            else:
                new_start = clip['start']

            # Calculate new dur
            if next_clip:
                new_dur = next_clip['offset'] - new_start
            else:
                new_dur = total_frames - new_start

            # Update clip with new start and dur
            adjusted_clip = clip.copy()
            adjusted_clip['offset'] = new_start
            adjusted_clip['dur'] = new_dur
            adjusted_clips.append(adjusted_clip)

    # Save new JSON file
    with open(f"{timeline_dir}{timeline_name}_parsed.json", 'w') as f:
        json.dump(
            {
                "audio_track_count": audio_track_count,
                'v': [adjusted_clips],
            },
            f,
            indent=4)
    return True


# FIXME fix overlapping frames at end of clip and beginning of clip
def parse_timeline_json2(timeline_dir: str, timeline_name: str,
                         total_frames: int) -> bool:
    r"""Takes a given {timeline_name} at {timeline_dir} and creates a new file {timeline_name}_parsed.json in the same dir. Adjusting the speed changes and fixing the mismatched frametimes.
    NOTE'dur' = length of clip, 'offset' = the source clip frame start time (NOT 'start'), 'speed' = 2 is the way the script knows what clip is silence. Setting speed to 2 messes with the 'start' 'offset' and 'dur' frames
    hence why we have to parse the json with this script.
    
    Args:
        timeline_dir (str): path to the timeline location to be parsed (excluding file name). i.e. C:\Program Files\\
        timeline_name (str): name of the timeline (excluding .JSON). This will also be used to give the new timeline created by this function.
        total_frames (int): total amount of frames in the timeline provided. used for the last subclip dur
        
    Returns:
        bool:
    """
    # Load the timeline JSON
    with open(f"{timeline_dir + timeline_name}.json", 'r') as f:
        timeline = json.load(f)
    
    # get number of audio tracks
    audio_track_count = len(timeline['a'])
    
    # Extract clips from the JSON
    timeline_clips = timeline.get('v', [])[0]
    
    # Init a list to hold adjusted clips
    adjusted_clips = []
    silent_clips = []
    
    for i, clip in enumerate(timeline_clips):
        if clip['speed'] == 1.0:
            new_clip = {
                'startFrame': clip['offset'],
                'endFrame': clip['offset'] + clip['dur'],
            }
        elif clip['speed'] == 2.0:
            silent_clips.append(i)
            
            # Calculate start and dur for speed 2.0
            previous_clip = timeline_clips[i - 1] if i > 0 else None
            next_clip = timeline_clips[
                i + 1] if i < len(timeline_clips) - 1 else None
            
            # Calculate new start
            if previous_clip:
                new_start = previous_clip['offset'] + previous_clip['dur']
            else:
                new_start = clip['start']
                
            # Calculate new dur
            if next_clip:
                new_dur = next_clip['offset'] - new_start
            else:
                new_dur = total_frames - new_start
            
            # Update clip with new start and dur
            new_clip = {
                'startFrame': new_start,
                'endFrame': new_start + new_dur,
            }
        
        if i > 0:
            new_clip['startFrame'] += 1
        adjusted_clips.append(new_clip)
    
    # Save new JSON file
    with open(f"{timeline_dir}{timeline_name}_parsed.json", 'w') as f:
        json.dump(
            {
                "audio_track_count": audio_track_count,
                "silent_clips": silent_clips,
                'v': adjusted_clips,
            },
            f,
            indent=4)
    return True


def create_timeline_with_clip(timeline_dir: str, timeline_name: str,
                              clip_idx: int) -> bool:
    # Load the timeline JSON
    with open(f"{timeline_dir + timeline_name}.json", 'r') as f:
        timeline = json.load(f)

    subclips_json_parsed = timeline.get('v', [])
    audio_track_count = timeline["audio_track_count"]
    timestamp = datetime.now().strftime("%y%m%d%H%M")

    # make new timeline using first clip
    mediaPool.CreateTimelineFromClips(
        f"cool timeline yo {timestamp}",
        [{
            'mediaPoolItem': clips[clip_idx],
            'startFrame': subclips_json_parsed[0]['startFrame'],
            'endFrame': subclips_json_parsed[0]['endFrame'],
        }])

    # clip color
    # 0 since this is 1st subclip
    if 0 not in timeline['silent_clips']:
        change_clip_colors("Orange", audio_track_count)

    # set current_timeline
    global current_timeline
    current_timeline = project.GetCurrentTimeline()


def append_clips(timeline_dir: str,
                 timeline_name: str,
                 clip_idx: int,
                 skip_first: bool = False) -> bool:

    # Load the timeline JSON
    with open(f"{timeline_dir + timeline_name}.json", 'r') as f:
        timeline = json.load(f)

    subclips_json_parsed = timeline.get('v', [])
    audio_track_count = timeline["audio_track_count"]

    # appending clips
    for idx, subclip in enumerate(subclips_json_parsed):
        if skip_first and idx == 0:
            continue
        mediaPool.AppendToTimeline([{
            'mediaPoolItem': clips[clip_idx],
            'startFrame': subclip['startFrame'],
            'endFrame': subclip['endFrame'],
        }])

        # clip color
        if idx not in timeline['silent_clips']:
            change_clip_colors("Orange", audio_track_count)


def change_clip_colors(color: str, audio_track_count: int):
    # get last clip index on timeline horizontally. leave on audio just incase user is only using audio
    subclip_idx = len(current_timeline.GetItemListInTrack("audio", 1)) - 1

    # set video track color
    current_timeline.GetItemListInTrack("video",
                                        1)[subclip_idx].SetClipColor(color)

    # iter over audio tracks vertically
    # NOTE for some reason DR api track index's start at 1 not 0 so thats the reason for the weird range()
    for i in range(1, audio_track_count + 1):
        current_timeline.GetItemListInTrack("audio",
                                            i)[subclip_idx].SetClipColor(color)

    return True


def main():
    # TODO update comment
    # begin main loop per clip (get clips -> gen json -> parse json -> add clip from timecode -> change clip color accordingly -> repeat till all clips added)

    is_new_timeline = True

    for clip_idx, clip in enumerate(clips):
        file_path = clip.GetClipProperty()['File Path']
        if file_path == '':  # skip empty list items
            continue

        file = clip.GetClipProperty()['File Name']
        # TODO Fix filename convention. grabe everything but the last '.'
        file_name = file.split(".")[0]
        file_dir = file_path.split(file)[0]

        print(f"creating timeline json for {file} clip at: {file_dir}")

        # use auto-edit to create timeline json
        subprocess.run(
            [
                'auto-editor',
                # TODO Fix name below 👇🏽
                file,
                '--edit',
                '(audio #:stream 1)',
                '--export',
                'json',
                '--silent-speed',
                '2',
                '--video-speed',
                '1',
                '--output',
                f"{file_name}",
            ],
            cwd=fr"{file_dir}",
            creationflags=subprocess.CREATE_NO_WINDOW)

        print("timeline creation successful, parsing JSON...")

        # parsing json
        total_frames = int(clips[clip_idx].GetClipProperty('End'))
        if parse_timeline_json2(file_dir, file_name, total_frames):
            print("parse successful, adding clips to timeline...")

        if is_new_timeline:
            create_timeline_with_clip(file_dir, f"{file_name}_parsed",
                                      clip_idx)
            # append rest of the clips in first file
            append_clips(file_dir, f"{file_name}_parsed", clip_idx, True)
            is_new_timeline = False
            print(f"new timeline created")
            print(f"{file} added...\n")
            continue

        # append remaining clips if multiple files
        append_clips(file_dir, f"{file_name}_parsed", clip_idx)
        print(f"{file} added...\n")


# init resolve api
resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()
# clips variable name is reference in test() so if your going to change its name you have to change it there too
# FIXME change search folder to a specific folder to prevent looping non-videos
clips = rootFolder.GetClipList()
current_timeline = project.GetCurrentTimeline()

# logging
print("beginning process.")
print("---")

main()

print("---")
print("process complete.")
