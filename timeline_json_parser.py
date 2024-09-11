import json


def parse_timeline_json(timeline_dir: str, timeline_name: str) -> bool:
    r"""Takes a given {timeline_name} at {timeline_dir} and creates a new file parsed_{timeline_name}.json in the same dir. Adjusting the speed changes and fixing the mismatched frametimes.
    
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
    with open(f"{timeline_dir}parsed_{timeline_name}.json", 'w') as f:
        json.dump({'v': [adjusted_clips]}, f, indent=4)
    return True
