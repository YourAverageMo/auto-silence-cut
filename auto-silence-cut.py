import subprocess
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# TODO add audio treshhold settings
# TODO put clips in diff dir instead of root


def input_to_float(text: str) -> float:
    """Converts input `text` into a float except returns 0.2 (default value) on ValueError (meaning input text is not only numbers). Used to convert user input felids in GUI."""

    if text == "":
        return False
    try:
        number = float(text)
        return number
    except ValueError:
        # error handling in case user changes values in settings.json or UI
        print("trim margins are not numbers, using default values of 0.2")
        return 0.2


def input_to_float_dB(text: str) -> float:
    """Converts input `text` into a float except returns -20.0 (default value) on ValueError (meaning input text is not only numbers). Used to convert user input felids in GUI."""

    # check added since value threshold is different from margin

    if text == "":
        return False
    try:
        number = float(text)
        return number
    except ValueError:
        # error handling in case user changes values in settings.json or UI
        print("trashhold is not numbers, using default values of -20.0")
        return -20.0


def load_settings() -> bool:
    """Handles loading of settings.json file, if exists = False creates one with default settings. Sets Global vars:

    L_TRIM_MARGIN, R_TRIM_MARGIN, USE_AUDIO_TRACK, HIGHLIGHT_COLOR, HIGHLIGHT_COLOR_INDEX, SKIP_GUI"""

    settings_file = settings_dir / "settings.json"
    # use settings file if it exists
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
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
            "L_TRIM_MARGIN": 0.2,
            "R_TRIM_MARGIN": 0.2,
            "USE_AUDIO_TRACK": [0],
            "GATE_DB": -20.0,
            "HIGHLIGHT_COLOR": "Orange",
            "HIGHLIGHT_COLOR_INDEX": 0,
            "DELETE_SILENCE": False,
            "SKIP_GUI": False,
        }
        with open(settings_file, "w") as f:
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
    timecode = timecode.split(":")
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

    return "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds, frames)


def sanitize_resolve_xml(xml_path):
    """
    Removes clips and extra resource information from a Resolve XML file,
    leaving an empty timeline structure.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Find the sequence tag and clear its children
        sequence = root.find(".//sequence")
        if sequence is not None:
            # This is a safe way to remove all children
            for child in list(sequence):
                sequence.remove(child)

        # Find the resources tag, keep only the first format tag
        resources = root.find(".//resources")
        if resources is not None:
            first_format_tag = resources.find("format")
            # Remove all children of <resources>
            for child in list(resources):
                resources.remove(child)
            # Add the first format tag back if it was found
            if first_format_tag is not None:
                resources.append(first_format_tag)

        # Write the modified XML back to the file
        tree.write(xml_path)
        print("XML sanitization successful.")
        return True
    except Exception as e:
        print(f"ERROR: Failed to parse or modify XML file at {xml_path}: {e}")
        return False


def diff_audio_tracks() -> int:
    """used to check if all video files in `clips` have the same audio track count. Returns audio track count as int."""
    previous_audio_tracks = None

    for clip in clips:
        file_path = clip.GetClipProperty().get("File Path")
        if not file_path:
            continue

        # Run ffprobe to get audio stream information
        command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "json",
            file_path,
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        ffprobe_output = json.loads(result.stdout)

        # Count the number of audio streams
        audio_tracks = len(ffprobe_output.get("streams", []))

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
        checkbox = ui.CheckBox(
            {
                "ID": f"checkbox_{track}",
                "Text": f"Track {track + 1}",
                "Checked": True if track in USE_AUDIO_TRACKS else False,
            }
        )
        checkbox_group.append(checkbox)

    return checkbox_group


def populate_and_color_timeline(
    all_clips_json_path: Path,
    audible_clips_json_path: Path,
    source_clip,
    delete_silence: bool,
    highlight_color: str,
    timeline_offset: int,
):
    """
    Populates the timeline using a comprehensive JSON and colors audible clips
    regardless of the delete_silence setting.
    """
    try:
        with open(all_clips_json_path, "r") as f:
            all_clips_data = json.load(f)
        with open(audible_clips_json_path, "r") as f:
            audible_clips_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON files: {e}")
        return False

    # Create a set of audible source offsets for quick lookup
    audible_offsets = {clip["offset"] for clip in audible_clips_data.get("v", [[]])[0]}

    video_clips_to_process = all_clips_data.get("v", [[]])
    if not video_clips_to_process or not video_clips_to_process[0]:
        print("No video clips found in the main JSON file.")
        return True

    total_source_frames = int(source_clip.GetClipProperty("Frames"))
    clips_to_append = []

    num_clips = len(video_clips_to_process[0])
    for i, clip_data in enumerate(video_clips_to_process[0]):
        start_frame = clip_data["offset"]
        is_audible = start_frame in audible_offsets

        # Decide whether to append the clip
        if not delete_silence or (delete_silence and is_audible):
            if i == num_clips - 1:
                end_frame = total_source_frames - 1
            else:
                end_frame = start_frame + clip_data["dur"] - 1

            new_clip = {
                "mediaPoolItem": source_clip,
                "startFrame": start_frame,
                "endFrame": end_frame,
            }
            clips_to_append.append(new_clip)

    if not clips_to_append:
        print("No clips to append after processing.")
        return True

    # Get the number of items on the video track before appending
    item_count_before_append = len(
        current_timeline.GetItemListInTrack("video", 1) or []
    )

    print(f"Appending {len(clips_to_append)} clips...")
    if not media_pool.AppendToTimeline(clips_to_append):
        print("ERROR: Failed to append clips to timeline.")
        return False

    print("Coloring audible clips...")
    video_items_after = current_timeline.GetItemListInTrack("video", 1) or []
    new_video_items = video_items_after[item_count_before_append:]

    # Create a lookup for audio items by their timeline start frame for efficiency
    audio_items_by_start = {}
    for i in range(1, current_timeline.GetTrackCount("audio") + 1):
        for item in current_timeline.GetItemListInTrack("audio", i) or []:
            audio_items_by_start.setdefault(item.GetStart(), []).append(item)

    for video_item in new_video_items:
        # GetLeftOffset() gives the frame offset from the start of the source media
        source_start_frame = video_item.GetLeftOffset()
        if source_start_frame in audible_offsets:
            # Color the video clip
            video_item.SetClipColor(highlight_color)

            # Find and color corresponding audio clips using the lookup
            timeline_start_frame = video_item.GetStart()
            if timeline_start_frame in audio_items_by_start:
                for audio_item in audio_items_by_start[timeline_start_frame]:
                    audio_item.SetClipColor(highlight_color)
    return True


def main():
    # flow of main():
    # 1. Generate assets using auto-editor (XML and V3 JSONs)
    # 2. Sanitize XML and import it to create a new, empty timeline
    # 3. Parse V3 JSON and append clips to the new timeline

    is_new_timeline = True
    timeline_offset = 0

    # Formatting for auto-editor is different for 1+ audio streams
    if len(USE_AUDIO_TRACKS) == 1:
        # i.e. `audio:stream=0`
        edit_param = f"audio:stream={USE_AUDIO_TRACKS[0]} audio:{GATE_DB}dB"
    else:
        # i.e. `(or audio:stream=0 audio:stream=1)`
        streams = " ".join(f"audio:stream={stream}" for stream in USE_AUDIO_TRACKS)
        edit_param = f"(or {streams}) audio:{GATE_DB}dB"

    for clip_idx, clip in enumerate(clips):
        file_path = clip.GetClipProperty()["File Path"]
        if not file_path:
            continue

        file_path = Path(file_path)
        print(f"Processing {file_path.name} at: {file_path.parent}")

        common_flags = [
            "auto-editor",
            str(file_path),
            "--edit",
            edit_param,
            "--margin",
            f"{L_TRIM_MARGIN}s,{R_TRIM_MARGIN}s",
        ]

        print("Generating Resolve FCPXML timeline...")
        xml_timeline_path = file_path.with_suffix(".fcpxml")
        resolve_flags = common_flags + [
            "--export",
            "resolve",
            "--output",
            str(xml_timeline_path),
        ]
        subprocess.run(
            resolve_flags,
            cwd=str(file_path.parent),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        print("Generating V3 JSON for all clips...")
        json_path_all_clips = file_path.with_name(f"{file_path.stem}_all_clips.v3")
        all_clips_flags = common_flags + [
            "--export",
            "v3",
            "--video-speed",
            "1",
            "--silent-speed",
            "1",
            "--output",
            str(json_path_all_clips),
        ]
        subprocess.run(
            all_clips_flags,
            cwd=str(file_path.parent),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        print("Generating V3 JSON for audible clips...")
        json_path_audible_clips = file_path.with_name(
            f"{file_path.stem}_audible_clips.v3"
        )
        audible_clips_flags = common_flags + [
            "--export",
            "v3",
            "--video-speed",
            "1",
            "--output",
            str(json_path_audible_clips),
        ]
        subprocess.run(
            audible_clips_flags,
            cwd=str(file_path.parent),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        print("Creating and importing empty timeline...")
        # generated timeline file needs to be empty only needed to create timeline. by doing it this way we support the original fps the video was in.
        if not sanitize_resolve_xml(xml_timeline_path):
            print(f"Skipping {file_path.name} due to XML sanitization error.")
            continue

        if is_new_timeline:
            print("Importing new timeline from XML...")
            timeline_name = (
                f"{project.GetName()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            new_timeline = media_pool.ImportTimelineFromFile(
                str(xml_timeline_path),
                {
                    "timelineName": timeline_name,
                    "importSourceClips": False,
                },
            )

            if not new_timeline:
                print("ERROR: Failed to create new timeline from XML. Skipping...")
                continue

            # Update global timeline object to the newly created one
            project.SetCurrentTimeline(new_timeline)
            global current_timeline
            current_timeline = new_timeline
            print(f"Successfully created and set timeline: {timeline_name}")
            is_new_timeline = False

        print("Populating timeline with clips...")

        populate_and_color_timeline(
            json_path_all_clips,
            json_path_audible_clips,
            clip,
            DELETE_SILENCE,
            HIGHLIGHT_COLOR,
            timeline_offset,
        )

        # Increment offset for the next file
        timeline_offset += int(clip.GetClipProperty("Frames"))

        print(f"{file_path.name} processed.\n")


# --
# -- GUI building starts here
# --
def open_user_interface():
    # element IDs
    win_id = "main_window"
    coffee_button = "coffee_button"
    start_button = "start_button"
    l_trim_input = "l_trim_input"
    r_trim_input = "r_trim_input"
    gate_db_input = "gate_db_input"
    highlight_color_input = "highlight_color_input"
    delete_silence_check = "delete_silence_check"
    skip_gui_check = "skip_ui"

    # check for existing instance
    win = ui.FindWindow(win_id)
    if win:
        win.Show()
        win.Raise()
        exit()

    # window layout
    winLayout = ui.VGroup(
        [
            # shameless plug section
            ui.Label(
                {
                    "ID": "DialogBox",
                    "Text": "Auto Editor\nby Muhammed Yilmaz",
                    "Weight": 0,
                    "Font": ui.Font(
                        {
                            "PixelSize": 24,
                            "Italic": True,
                            "Bold": True,
                        }
                    ),
                    "Alignment": {"AlignHCenter": True},
                    "StyleSheet": "QLabel { color: white; }",
                }
            ),
            ui.Button(
                {
                    "ID": coffee_button,
                    "Text": "If this plugin is useful and want to support me, consider buying me a coffee :)",
                    "Weight": 0,
                    "StyleSheet": "QPushButton { color: #f1f17b; }",
                }
            ),
            ui.VGap(5),
            # start button
            ui.Button(
                {
                    "ID": start_button,
                    "Text": "START",
                    "Font": ui.Font({"PixelSize": 16, "Bold": True}),
                    "Weight": 0,
                }
            ),
            ui.VGap(5),
            # Labels for l/r trim
            ui.HGroup(
                {"Weight": 0},
                [
                    ui.Label(
                        {
                            "Text": "Left Trim Margin [s]:",
                            "Font": ui.Font(
                                {
                                    "Bold": True,
                                }
                            ),
                        }
                    ),
                    ui.Label(
                        {
                            "Text": "Right Trim Margin [s]:",
                            "Font": ui.Font(
                                {
                                    "Bold": True,
                                }
                            ),
                        }
                    ),
                ],
            ),
            # inputs for l/r trim
            ui.HGroup(
                {"Weight": 0},
                [
                    ui.LineEdit(
                        {
                            "ID": l_trim_input,
                        }
                    ),
                    ui.LineEdit(
                        {
                            "ID": r_trim_input,
                        }
                    ),
                ],
            ),
            ui.VGap(5),
            # Labels for audio threshhold and color
            ui.HGroup(
                {"Weight": 0},
                [
                    ui.Label(
                        {
                            "Text": "Audio Threshold [dB]:",
                            "Font": ui.Font(
                                {
                                    "Bold": True,
                                }
                            ),
                        }
                    ),
                    ui.Label(
                        {
                            "Text": "Highlight Color:",
                            "Font": ui.Font(
                                {
                                    "Bold": True,
                                }
                            ),
                        }
                    ),
                ],
            ),
            # inputs for audio threshhold and color
            ui.HGroup(
                {"Weight": 0},
                [
                    ui.LineEdit(
                        {
                            "ID": gate_db_input,
                        }
                    ),
                    ui.ComboBox(
                        {
                            "ID": highlight_color_input,
                        }
                    ),
                ],
            ),
            ui.VGap(5),
            # track checkboxes (constructed)
            ui.Label(
                {
                    "Text": "Edit Based on These Tracks:",
                    "Weight": 0,
                    "Font": ui.Font(
                        {
                            "Bold": True,
                        }
                    ),
                }
            ),
            ui.HGroup({"Weight": 0}, construct_checkboxes(audio_track_count)),
            # delete silence immidiately
            ui.CheckBox(
                {
                    "ID": delete_silence_check,
                    "Text": "Automatically delete detected silence?",
                    "Weight": 0,
                }
            ),
            # skip GUI
            ui.CheckBox(
                {
                    "ID": skip_gui_check,
                    "Text": "Skip this window? (Warning to undo this you will have to change the settings file.)",
                    "Weight": 0,
                }
            ),
            ui.VGap(2),
        ]
    )

    #  create window and get items
    win = dispatcher.AddWindow(
        {
            "ID": win_id,
            "WindowTitle": "Auto Editor by Muhammed Yilmaz",
            "Geometry": [20, 50, 530, 390],
        },
        winLayout,
    )
    itm = win.GetItems()

    # populate fields
    itm[highlight_color_input].AddItem("Orange")
    itm[highlight_color_input].AddItem("Apricot")
    itm[highlight_color_input].AddItem("Yellow")
    itm[highlight_color_input].AddItem("Lime")
    itm[highlight_color_input].AddItem("Olive")
    itm[highlight_color_input].AddItem("Green")
    itm[highlight_color_input].AddItem("Navy")
    itm[highlight_color_input].AddItem("Blue")
    itm[highlight_color_input].AddItem("Purple")
    itm[highlight_color_input].AddItem("Violet")
    itm[highlight_color_input].AddItem("Pink")
    itm[highlight_color_input].AddItem("Tan")
    itm[highlight_color_input].AddItem("Beige")
    itm[highlight_color_input].AddItem("Brown")
    itm[highlight_color_input].AddItem("Chocolate")
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
            if itm[f"checkbox_{track}"].Checked:
                USE_AUDIO_TRACKS_EDITED.append(track)

        settings = {
            "L_TRIM_MARGIN": input_to_float(itm[l_trim_input].Text),
            "R_TRIM_MARGIN": input_to_float(itm[r_trim_input].Text),
            "GATE_DB": input_to_float_dB(itm[gate_db_input].Text),
            "USE_AUDIO_TRACK": USE_AUDIO_TRACKS_EDITED,
            "HIGHLIGHT_COLOR": itm[highlight_color_input].CurrentText,
            "HIGHLIGHT_COLOR_INDEX": itm[highlight_color_input].CurrentIndex,
            "DELETE_SILENCE": itm[delete_silence_check].Checked,
            "SKIP_GUI": itm[skip_gui_check].Checked,
        }
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)

        return True

    def on_close(ev):
        save_settings()
        dispatcher.ExitLoop()
        exit()

    def on_start(ev):
        itm[start_button].Text = "RUNNING... (dont press anything)"
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

if __name__ == "__main__":
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
                    f"Skipping user interface, to re-enable set SKIP_GUI to false in settings.json at {settings_dir}"
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
            "The video files in the scan directory do not all contain the same number of audio tracks. Please address this issue and run the script separately for files with different # of audio tracks"
        )
        print("aborting...")
        exit()

    # error handling
    if USE_AUDIO_TRACKS and max(USE_AUDIO_TRACKS) > audio_track_count:
        USE_AUDIO_TRACKS = [0]
        SKIP_GUI = False
        print(
            "One selected audio track in user settings was not available on current clip(s) restoring default settings "
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
