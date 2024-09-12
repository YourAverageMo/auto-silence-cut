import subprocess
import json
from pprint import pprint


# TODO: fix timecode func to accept all fps and any frames_delta change
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


def parse_timeline_json(timeline_dir: str, timeline_name: str) -> bool:
    r"""Takes a given {timeline_name} at {timeline_dir} and creates a new file {timeline_name}_parsed.json in the same dir. Adjusting the speed changes and fixing the mismatched frametimes.
    
    NOTE:
    'dur' = length of clip.
    'offset' = the source clip frame start time (NOT 'start').
    'speed' = 2 is the way the script knows what clip is silence.
    Setting speed to 2 messes with the 'start' 'offset' and 'dur' frames
    hence why we have to parse the json with this script.

    Args:
        timeline_dir (str): path to the timeline location to be parsed (excluding file name). i.e. C:\Program Files\\ 
        timeline_name (str): name of the timeline (excluding .JSON). This will also be used to give the new timeline created by this function.

    Returns:
        bool:
    """
    # Load the timeline JSON
    with open(f"{timeline_dir + timeline_name}.json", 'r') as f:
        timeline = json.load(f)

    # Extract clips from the JSON
    clips = timeline.get('v', [])[0]

    # Init a list to hold adjusted clips
    adjusted_clips = []

    for i, clip in enumerate(clips):
        if clip['speed'] == 1.0:
            # Use the given values directly for speed 1.0
            adjusted_clips.append(clip)
        elif clip['speed'] == 2.0:
            # Calculate start and dur for speed 2.0
            previous_clip = clips[i - 1] if i > 0 else None
            next_clip = clips[i + 1] if i < len(clips) - 1 else None

            # Calculate new start
            if previous_clip:
                new_start = previous_clip['offset'] + previous_clip['dur']
            else:
                new_start = clip['start']

            # Calculate new dur
            if next_clip:
                new_dur = next_clip['offset'] - new_start
            else:
                new_dur = None

            # Update clip with new start and dur
            adjusted_clip = clip.copy()
            adjusted_clip['offset'] = new_start
            adjusted_clip['dur'] = new_dur
            adjusted_clips.append(adjusted_clip)

    # Save new JSON file
    with open(f"{timeline_dir}{timeline_name}_parsed.json", 'w') as f:
        json.dump({'v': [adjusted_clips]}, f, indent=4)
    return True


def test(timeline_dir: str, timeline_name: str, idx: int) -> bool:
    # Load the timeline JSON
    with open(f"{timeline_dir + timeline_name}.json", 'r') as f:
        timeline = json.load(f)

    json_parsed = timeline.get('v', [])[0]

    # begin subclip loop
    for subclip in json_parsed:

        # set subclip attributes
        startframe = subclip['offset']
        # TODO: fix dup frames
        dur = subclip['dur']
        speed = subclip['speed']
        # TODO:
        if dur is None:
            dur = 120
        endframe = startframe + dur
        print(startframe, dur, endframe)

        # appending clips
        if mediaPool.AppendToTimeline([{
                "mediaPoolItem": clips[idx],
                "startFrame": startframe,
                "endFrame": endframe,
        }]):
            print(f"added subclip at {startframe}")

        if speed == 1:
            # Set the playhead to the new position
            current_frame = current_timeline.GetCurrentTimecode()
            new_frame = ChangeTimecode(current_frame)
            current_timeline.SetCurrentTimecode(new_frame)
            print("moved playhead")

            # set clip color
            current_video_item = current_timeline.GetCurrentVideoItem()
            current_video_item.SetClipColor("Orange")
            print("clip color changed")


def main():

    # logging
    print(f"found {len(clips)} clips in root dir.\n")

    # begin main loop per clip (get clips -> gen json -> parse json -> add clip from timecode -> change clip color accordingly -> repeat till all clips added)

    for idx, clip in enumerate(clips):
        file_path = clip.GetClipProperty()['File Path']
        if file_path == '':  # skip empty list items
            continue

        # dont put .split() in declaration incase folder is same name as file
        file = clip.GetClipProperty()['File Name']
        file_name = file.split(".")[0]
        file_dir = file_path.split(file)[0]

        print(f"creating timeline json for {file} clip at: {file_dir}")

        # use auto-edit to create timeline json
        subprocess.run([
            'auto-editor',
            'test.mkv',
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
        if parse_timeline_json(file_dir, file_name):
            print("parse successful, adding clips to timeline...\n")

        test(file_dir, f"{file_name}_parsed", idx)


# init resolve api
resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()
clips = rootFolder.GetClipList()
current_timeline = project.GetCurrentTimeline()

# logging
print("beginning process.")
print("---")
main()
