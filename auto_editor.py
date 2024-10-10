import subprocess
import json
from datetime import datetime
from pathlib import Path

# TODO add gui
# TODO add audio treshhold settings
# TODO trim margin adjustment
# TODO put clips in diff dir instead of root


def load_settings():
    settings_file = settings_dir / "settings.json"
    # use settings file if it exists
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        # abort if syntax error to preserve user settings
        except json.decoder.JSONDecodeError:
            print(
                "error loading user settings (syntax error), please correct settings.json or delete the file and rerun to use default settings"
            )
            print("aborting script...")
            exit()

    # save default settings to file
    else:
        settings = {
            'L_TRIM_MARGIN': 0,
            'R_TRIM_MARGIN': 0,
            'USE_AUDIO_TRACK': [0],
            'HIGHLIGHT_COLOR': 'Orange',
            'SKIP_GUI': False,
        }
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    # set global settings
    # i think its neater to use globals here than to have these in the main loop
    global L_TRIM_MARGIN
    global R_TRIM_MARGIN
    global USE_AUDIO_TRACKS
    global HIGHLIGHT_COLOR
    global SKIP_GUI

    try:
        L_TRIM_MARGIN = settings["L_TRIM_MARGIN"]
        R_TRIM_MARGIN = settings["R_TRIM_MARGIN"]
        USE_AUDIO_TRACKS = settings["USE_AUDIO_TRACK"]
        HIGHLIGHT_COLOR = settings["HIGHLIGHT_COLOR"]
        SKIP_GUI = settings["SKIP_GUI"]
    except KeyError:
        print(
            "error loading user settings (missing setting), please correct settings.json or delete the file and rerun to use default settings"
        )
        print("aborting script...")
        exit()

    # cleaning memory
    del settings

    return True


# NOTE ChangeTimecode() is legacy code use change_clip_colors() now.
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


def parse_timeline_json(file_path: Path, total_frames: int) -> bool:
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
    with open(f"{file_path.parent / file_path.stem}.json", 'r') as f:
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

    parsed_timeline = {
        "audio_track_count": audio_track_count,
        "silent_clips": silent_clips,
        'v': adjusted_clips,
    }

    with open(f"{file_path.parent / file_path.stem}_parsed.json", 'w') as f:
        json.dump(parsed_timeline, f, indent=4)

    return parsed_timeline


def create_timeline_with_clip(parsed_timeline: dict, clip_idx: int) -> bool:

    subclips_json_parsed = parsed_timeline.get('v', [])
    audio_track_count = parsed_timeline["audio_track_count"]
    timestamp = datetime.now().strftime("%y%m%d%H%M")

    # make new timeline using first clip
    media_pool.CreateTimelineFromClips(
        f"cool timeline yo {timestamp}",
        [{
            'mediaPoolItem': clips[clip_idx],
            'startFrame': subclips_json_parsed[0]['startFrame'],
            'endFrame': subclips_json_parsed[0]['endFrame'],
        }])

    # set current_timeline
    global current_timeline
    current_timeline = project.GetCurrentTimeline()

    # clip color
    # 0 since this is 1st subclip
    if 0 not in parsed_timeline['silent_clips'] and HIGHLIGHT_COLOR is not None:
        change_clip_colors(HIGHLIGHT_COLOR, audio_track_count)


def append_clips(parsed_timeline: dict,
                 clip_idx: int,
                 skip_first: bool = False) -> bool:

    subclips_json_parsed = parsed_timeline.get('v', [])
    audio_track_count = parsed_timeline["audio_track_count"]

    # appending clips
    for idx, subclip in enumerate(subclips_json_parsed):
        # i could list slice parsed_timeline and remove idx 0 if skip_first instead of checking if every subclip... but for now this is fine. if it causes performance issues i will change it
        if skip_first and idx == 0:
            continue
        media_pool.AppendToTimeline([{
            'mediaPoolItem': clips[clip_idx],
            'startFrame': subclip['startFrame'],
            'endFrame': subclip['endFrame'],
        }])

        # clip color
        if idx not in parsed_timeline[
                'silent_clips'] and HIGHLIGHT_COLOR is not None:
            change_clip_colors(HIGHLIGHT_COLOR, audio_track_count)


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


def diff_audio_tracks():
    previous_audio_tracks = None

    for clip in clips:
        file_path = clip.GetClipProperty().get('File Path')
        if not file_path:
            continue

        # Run ffprobe to get audio stream information
        command = [
            'ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries',
            'stream=index', '-of', 'json', file_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        ffprobe_output = json.loads(result.stdout)

        # Count the number of audio streams
        audio_tracks = len(ffprobe_output.get('streams', []))

        # Set previous_audio_tracks on first valid clip
        if previous_audio_tracks is None:
            previous_audio_tracks = audio_tracks
        elif audio_tracks != previous_audio_tracks:
            return None

    return previous_audio_tracks


def main():
    # TODO update comment
    # begin main loop per clip (get clips -> gen json -> parse json -> add clip from timecode -> change clip color accordingly -> repeat till all clips added)

    is_new_timeline = True

    # TODO threshold adjustment

    # formating for auto-edit is diff for 1+ audio streams
    if len(USE_AUDIO_TRACKS) == 1:
        # i.e. `audio:stream=0`
        edit_param = f'audio:stream={USE_AUDIO_TRACKS[0]}'
    else:
        # i.e. `(or audio:stream=0 audio:stream=1)`
        streams = ' '.join(f'audio:stream={stream}'
                           for stream in USE_AUDIO_TRACKS)
        edit_param = f'(or {streams})'

    for clip_idx, clip in enumerate(clips):
        file_path = clip.GetClipProperty()['File Path']
        if file_path:  # skip empty list items
            file_path = Path(file_path)
            print(
                f"creating timeline json for {file_path.name} clip at: {file_path.parent}"
            )

            # use auto-edit to create timeline json
            subprocess.run(
                [
                    'auto-editor',
                    file_path.name,
                    '--edit',
                    edit_param,
                    '--export',
                    'json',
                    '--silent-speed',
                    '2',
                    '--video-speed',
                    '1',
                    '--output',
                    file_path,  # auto-editor trims ext
                ],
                cwd=fr"{file_path.parent}",
                creationflags=subprocess.CREATE_NO_WINDOW)

            print("timeline creation successful, parsing JSON...")

            # parsing json
            total_frames = int(clips[clip_idx].GetClipProperty('End'))
            parsed_timeline = parse_timeline_json(file_path, total_frames)

            if not parsed_timeline:
                print(f"no audio detected in {file_path.name}, skipping...")
                continue

            print("parse successful, adding clips to timeline...")

            if is_new_timeline:
                create_timeline_with_clip(parsed_timeline, clip_idx)
                print(f"new timeline created")
                # append rest of the clips in first file
                append_clips(parsed_timeline, clip_idx, True)
                is_new_timeline = False
                print(f"{file_path.name} added...\n")
                continue

            # append remaining clips if multiple files
            append_clips(parsed_timeline, clip_idx)
            print(f"{file_path.name} added...\n")


def open_user_interface():

    # element IDs
    win_id = 'main_window'
    coffee_button = 'coffee_button'
    start_button = 'start_button'
    skip_gui_check = 'skip_ui'

    # check for existing instance
    win = ui.FindWindow(win_id)
    if win:
        win.Show()
        win.Raise()
        exit()

    # window layout
    winLayout = ui.VGroup([
        # shameless plug section
        ui.Label({
            'ID':
            'DialogBox',
            'Text':
            "Auto Editor\nby Muhammed Yilmaz",
            'Weight':
            0,
            'Font':
            ui.Font({
                'PixelSize': 24,
                'Italic': True,
                'Bold': True,
            }),
            'Alignment': {
                'AlignHCenter': True
            },
            'StyleSheet':
            'QLabel { color: white; }',
        }),
        ui.Button({
            'ID': coffee_button,
            'Text':
            'If this plugin is useful and want to support me, consider buying me a coffee :)',
            'Weight': 0,
            'StyleSheet': 'QPushButton { color: #f1f17b; }'
        }),
        ui.VGap(5),

        # start button
        ui.Button({
            'ID': start_button,
            'Text': 'START',
            'Font': ui.Font({
                'PixelSize': 16,
                'Bold': True
            }),
            'Weight': 0
        }),
        ui.VGap(5),

        # Advanced Settings Header
        ui.Label({
            'Text': "Advanced Settings",
            'Font': ui.Font({
                'PixelSize': 16,
                'Bold': True,
            }),
            'Weight': 0,
        }),
        ui.VGap(2),
        ui.CheckBox({
            'ID': skip_gui_check,
            'Text':
            "Skip this window? (Warning to undo this you will have to change the settings file.)",
            'Weight': 0
        }),
        ui.VGap(2),
    ])

    #  create window and get items
    win = dispatcher.AddWindow(
        {
            'ID': win_id,
            'WindowTitle': "Auto Editor by Muhammed Yilmaz",
            'Geometry': [20, 50, 550, 550],
        }, winLayout)
    itm = win.GetItems()

    # populate fields

    # window events
    def save_settings():
        pass

    def on_close(ev):
        save_settings()
        dispatcher.ExitLoop()
        exit()

    def on_start(ev):
        dispatcher.ExitLoop()

    def on_coffee_button(ev):
        import webbrowser
        webbrowser.open("https://www.youtube.com")

    # event handlers
    win.On[win_id].Close = on_close
    win.On[start_button].Clicked = on_start
    win.On[coffee_button].Clicked = on_coffee_button

    # Show window
    win.Show()
    dispatcher.RunLoop()


# --
# -- Main loop starts here
# --

# set/make settings folder
settings_dir = Path().home() / "Documents" / "Auto Editor"
settings_dir.mkdir(exist_ok=True)
load_settings()

try:
    # Attempt to get the DaVinci Resolve API object
    resolve = app.GetResolve()
    if resolve:
        if SKIP_GUI:
            # i no nested if statement... bite me.
            print(
                f'Skipping user interface, to re-enable set SKIP_GUI to false in settings.json at {settings_dir}'
            )
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        media_pool = project.GetMediaPool()
        root_folder = media_pool.GetRootFolder()
        folders = root_folder.GetSubFolderList()
        clips = root_folder.GetClipList()
        current_timeline = project.GetCurrentTimeline()
        ui = fusion.UIManager
        dispatcher = bmd.UIDispatcher(ui)

except NameError:
    print("Script must run inside DaVinci Resolve. aborting..")
    exit()

# error handling for files with diff # audio tracks
audio_track_count = diff_audio_tracks()
if not audio_track_count:
    print(
        'The video files in the scan directory do not all contain the same number of audio tracks. Please address this issue and run the script separately for files with different # of audio tracks'
    )
    print('aborting...')
    exit()

if resolve and not SKIP_GUI:
    # open_user_interface is just a way of loading and saving settings. ezpz
    open_user_interface()

# logging
print("beginning process.")
print("---")

main()

print("---")
print("process complete.")
