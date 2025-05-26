import subprocess
import json
from datetime import datetime
from pathlib import Path

# TODO add audio treshhold settings
# TODO put clips in diff dir instead of root


def input_to_float(text: str) -> float:
    """Converts input `text` into a float except returns 0.2 (default value) on ValueError (meaning input text is not only numbers). Used to convert user input felids in GUI."""

    if text == '':
        return False
    try:
        number = float(text)
        return number
    except ValueError:
        # error handling in case user changes values in settings.json or UI
        print('trim margins are not numbers, using default values of 0.2')
        return 0.2

def input_to_float_dB(text: str) -> float:
    """Converts input `text` into a float except returns -20.0 (default value) on ValueError (meaning input text is not only numbers). Used to convert user input felids in GUI."""

    #check added since value threshold is different from margin

    if text == '':
        return False
    try:
        number = float(text)
        return number
    except ValueError:
        # error handling in case user changes values in settings.json or UI
        print('trashhold is not numbers, using default values of -20.0')
        return -20.0

def load_settings() -> bool:
    """Handles loading of settings.json file, if exists = False creates one with default settings. Sets Global vars:
    
    L_TRIM_MARGIN, R_TRIM_MARGIN, USE_AUDIO_TRACK, HIGHLIGHT_COLOR, HIGHLIGHT_COLOR_INDEX, SKIP_GUI"""

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
            'L_TRIM_MARGIN': 0.2,
            'R_TRIM_MARGIN': 0.2,
            'USE_AUDIO_TRACK': [0],
            'GATE_DB': -20.0,
            'HIGHLIGHT_COLOR': 'Orange',
            'HIGHLIGHT_COLOR_INDEX': 0,
            'DELETE_SILENCE': False,
            'SKIP_GUI': False,
        }
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    # set global settings
    # i think its neater to use globals here than to have these in the main loop
    global L_TRIM_MARGIN
    global R_TRIM_MARGIN
    global GATE_DB
    global USE_AUDIO_TRACKS
    global HIGHLIGHT_COLOR
    global HIGHLIGHT_COLOR_INDEX
    global DELETE_SILENCE
    global SKIP_GUI

    try:
        L_TRIM_MARGIN = input_to_float(settings["L_TRIM_MARGIN"])
        R_TRIM_MARGIN = input_to_float(settings["R_TRIM_MARGIN"])
        GATE_DB = input_to_float_dB(settings["GATE_DB"])
        L_TRIM_MARGIN = settings["L_TRIM_MARGIN"]
        R_TRIM_MARGIN = settings["R_TRIM_MARGIN"]
        GATE_DB = settings["GATE_DB"]
        USE_AUDIO_TRACKS = settings["USE_AUDIO_TRACK"]
        HIGHLIGHT_COLOR = settings["HIGHLIGHT_COLOR"]
        HIGHLIGHT_COLOR_INDEX = settings["HIGHLIGHT_COLOR_INDEX"]
        DELETE_SILENCE = settings["DELETE_SILENCE"]
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
    r"""Takes the timeline json file created by `auto-editor` and parses the data inside it adjusting the speed changes and fixing the mismatched frametimes. Returns new file ends with `_parsed` in the same dir.
    
    NOTE: 'dur' = length of clip, 'offset' = the source clip frame start time (NOT 'start'), 'speed' = 2 is the way the script knows what clip is silence. Setting speed to 2 messes with the 'start' 'offset' and 'dur' frames
    hence why we have to parse the json with this script."""

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
            #skips appending silent clips if auto-delete option is enabled
            if DELETE_SILENCE == True:
                continue

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
    """Creates new timeline and appends first clip found in the newly created `parsed_timeline`."""

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
    """Appends all clips found in the newly created `parsed_timeline`. if skip_first = True the first clip in `parsed_timeline` will be skiped (meaning it was used to create a new timeline). Also calls `change_clip_colors()` if needed. """

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


def change_clip_colors(color: str, audio_track_count: int) -> bool:
    "Changes all video and audio track colors to given `color` for the last clip on the timeline"
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


def diff_audio_tracks() -> int:
    """used to check if all video files in `clips` have the same audio track count. Returns audio track count as int."""
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
        result = subprocess.run(command,
                                capture_output=True,
                                text=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        ffprobe_output = json.loads(result.stdout)

        # Count the number of audio streams
        audio_tracks = len(ffprobe_output.get('streams', []))

        # Set previous_audio_tracks on first valid clip
        if previous_audio_tracks is None:
            previous_audio_tracks = audio_tracks
        elif audio_tracks != previous_audio_tracks:
            return None

    return previous_audio_tracks


def construct_checkboxes(audio_tracks: int):
    """Constructs the checkboxes in the GUI for the count of audio tracks"""
    checkbox_group = []

    for track in range(audio_tracks):
        checkbox = ui.CheckBox({
            'ID':
            f'checkbox_{track}',
            'Text':
            f'Track {track+1}',
            'Checked':
            True if track in USE_AUDIO_TRACKS else False,
        })
        checkbox_group.append(checkbox)

    return checkbox_group


def main():
    # flow of main():
    # gen timeline json for each clip in `clips` in auto-editor > parse json into new json > create new timeline > append clips

    is_new_timeline = True

    # TODO threshold adjustment

    # formating for auto-edit is diff for 1+ audio streams
    if len(USE_AUDIO_TRACKS) == 1:
        # i.e. `audio:stream=0`
        edit_param = f'audio:stream={USE_AUDIO_TRACKS[0]} audio:{GATE_DB}dB'
    else:
        # i.e. `(or audio:stream=0 audio:stream=1)`
        streams = ' '.join(f'audio:stream={stream}'
                           for stream in USE_AUDIO_TRACKS)
        edit_param = f"(or {streams}) audio:{GATE_DB}dB"

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
                    '--margin',
                    f"{L_TRIM_MARGIN}s,{R_TRIM_MARGIN}s",
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


# --
# -- GUI building starts here
# --


def open_user_interface():

    # element IDs
    win_id = 'main_window'
    coffee_button = 'coffee_button'
    start_button = 'start_button'
    l_trim_input = 'l_trim_input'
    r_trim_input = 'r_trim_input'
    gate_db_input = 'gate_db_input'
    highlight_color_input = 'highlight_color_input'
    delete_silence_check = 'delete_silence_check'
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

        # Labels for l/r trim
        ui.HGroup({'Weight': 0}, [
            ui.Label({
                'Text': 'Left Trim Margin [s]:',
                'Font': ui.Font({
                    'Bold': True,
                }),
            }),
            ui.Label({
                'Text': 'Right Trim Margin [s]:',
                'Font': ui.Font({
                    'Bold': True,
                }),
            }),
        ]),

        # inputs for l/r trim
        ui.HGroup({'Weight': 0}, [
            ui.LineEdit({
                "ID": l_trim_input,
            }),
            ui.LineEdit({
                "ID": r_trim_input,
            }),
        ]),
        ui.VGap(5),

        # Labels for audio threshhold and color
        ui.HGroup({'Weight': 0}, [
            ui.Label({
                'Text': 'Audio Threshold [dB]:',
                'Font': ui.Font({
                    'Bold': True,
                }),
            }),
            ui.Label({
                'Text': 'Highlight Color:',
                'Font': ui.Font({
                    'Bold': True,
                }),
            }),
        ]),

        # inputs for audio threshhold and color
        ui.HGroup({'Weight': 0}, [
            ui.LineEdit({
                "ID": gate_db_input,
            }),
            ui.ComboBox({
                'ID': highlight_color_input,
            }),
        ]),
        ui.VGap(5),

        # track checkboxes (constructed)
        ui.Label({
            'Text': 'Edit Based on These Tracks:',
            'Weight': 0,
            'Font': ui.Font({
                'Bold': True,
            }),
        }),
        ui.HGroup({'Weight': 0}, construct_checkboxes(audio_track_count)),

        # delete silence immidiately
        ui.CheckBox({
            'ID': delete_silence_check,
            'Text':
            "Automatically delete detected silence?",
            'Weight': 0
        }),

        # skip GUI
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
            'Geometry': [20, 50, 530, 390],
        }, winLayout)
    itm = win.GetItems()

    # populate fields
    itm[highlight_color_input].AddItem('Orange')
    itm[highlight_color_input].AddItem('Apricot')
    itm[highlight_color_input].AddItem('Yellow')
    itm[highlight_color_input].AddItem('Lime')
    itm[highlight_color_input].AddItem('Olive')
    itm[highlight_color_input].AddItem('Green')
    itm[highlight_color_input].AddItem('Navy')
    itm[highlight_color_input].AddItem('Blue')
    itm[highlight_color_input].AddItem('Purple')
    itm[highlight_color_input].AddItem('Violet')
    itm[highlight_color_input].AddItem('Pink')
    itm[highlight_color_input].AddItem('Tan')
    itm[highlight_color_input].AddItem('Beige')
    itm[highlight_color_input].AddItem('Brown')
    itm[highlight_color_input].AddItem('Chocolate')
    itm[highlight_color_input].CurrentIndex = HIGHLIGHT_COLOR_INDEX

    itm[l_trim_input].Text = str(L_TRIM_MARGIN)
    itm[r_trim_input].Text = str(R_TRIM_MARGIN)
    itm[gate_db_input].Text = str(GATE_DB)
    itm[delete_silence_check].Checked = DELETE_SILENCE
    
    # window events
    def save_settings():
        # resolve api is weird, TextEdit boxes need to be strings and spin boxes cant be floats. so in order to give user feedback i have to do it this weird way...

        settings_file = settings_dir / "settings.json"

        # fetching checked track checkboxes
        USE_AUDIO_TRACKS_EDITED = []
        for track in range(audio_track_count):
            if itm[f'checkbox_{track}'].Checked:
                USE_AUDIO_TRACKS_EDITED.append(track)

        settings = {
            'L_TRIM_MARGIN': input_to_float(itm[l_trim_input].Text),
            'R_TRIM_MARGIN': input_to_float(itm[r_trim_input].Text),
            'GATE_DB': input_to_float_dB(itm[gate_db_input].Text),
            'USE_AUDIO_TRACK': USE_AUDIO_TRACKS_EDITED,
            'HIGHLIGHT_COLOR': itm[highlight_color_input].CurrentText,
            'HIGHLIGHT_COLOR_INDEX': itm[highlight_color_input].CurrentIndex,
            'DELETE_SILENCE': itm[delete_silence_check].Checked,
            'SKIP_GUI': itm[skip_gui_check].Checked,
        }
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

        return True

    def on_close(ev):
        save_settings()
        dispatcher.ExitLoop()
        exit()

    def on_start(ev):
        itm[start_button].Text = 'RUNNING... (dont press anything)'
        save_settings()
        load_settings()
        dispatcher.ExitLoop()

    def on_coffee_button(ev):
        import webbrowser
        webbrowser.open("https://www.buymeacoffee.com/YourAverageMo")

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

# error handling
if USE_AUDIO_TRACKS and max(USE_AUDIO_TRACKS) > audio_track_count:
    USE_AUDIO_TRACKS = [0]
    SKIP_GUI = False
    print(
        'One selected audio track in user settings was not available on current clip(s) restoring default settings '
    )

if resolve and not SKIP_GUI:
    # open_user_interface is just a way of loading and saving settings. ezpz
    construct_checkboxes(audio_track_count)
    open_user_interface()

# logging
print("beginning process.")
print("---")

main()

print("---")
print("process complete.")
