from timeline_json_parser import parse_timeline_json
from pprint import pprint
import subprocess

# init resolve api
resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
mediaPool = project.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()
clips = rootFolder.GetClipList()
current_timeline = project.GetCurrentTimeline()


# move playhead back so GetCurrentVideoItem() returns most recent appened clip
# appending clip after playhead move does not overwrite clip from playhead position
def ChangeTimecode(timecode: str, frames: int) -> str:
    timecode = timecode.split(':')
    hours = int(timecode[0])
    minutes = int(timecode[1])
    seconds = int(timecode[2])
    frames = int(timecode[3])
    frames = frames + frames
    return "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds,
                                                frames)



# create timeline json
for clip in clips:
    file_path = clip.GetClipProperty()['File Path']
    if file_path == '': # skip empty list items
        continue
    
    # dont put .split() in declaration incase folder is same name as file
    file_name = clip.GetClipProperty()['File Name'] 
    file_path = file_path.split(file_name)[0]
    pprint(f"clip '{file_name.split(".")[0]}' found at: {file_path}")

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
        f"{file_name.split(".")[0]}",
    ],
                   cwd=fr"{file_path}",
                   creationflags=subprocess.CREATE_NO_WINDOW)
    

# add sample clip from media pool
if mediaPool.AppendToTimeline([{
        "mediaPoolItem": clips[0],
        "startFrame": 6000,
        "endFrame": 6500,
}]):
    print(f"added {clips[0].GetName()}")

    # Set the playhead to the new position
    current_frame = current_timeline.GetCurrentTimecode()
    new_frame = ChangeTimecode(current_frame, -300)
    current_timeline.SetCurrentTimecode(new_frame)
    print("moved playhead")

    # set clip color
    current_video_item = current_timeline.GetCurrentVideoItem()
    current_video_item.SetClipColor("Orange")
    print("clip color changed")
