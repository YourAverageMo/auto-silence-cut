from timeline_json_parser import parse_timeline_json

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
def ChangeTimecode(timecode: str):
    timecode = timecode.split(':')
    hours = int(timecode[0])
    minutes = int(timecode[1])
    seconds = int(timecode[2])
    frames = int(timecode[3])
    frames = frames - 300
    return "{:02d}:{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds,
                                                frames)


# add sample clip from media pool
if mediaPool.AppendToTimeline([{
        "mediaPoolItem": clips[0],
        "startFrame": 6000,
        "endFrame": 6500,
}]):
    print(f"added {clips[0].GetName()}")

    # Set the playhead to the new position
    current_frame = current_timeline.GetCurrentTimecode()
    new_frame = ChangeTimecode(current_frame)
    current_timeline.SetCurrentTimecode(new_frame)
    print("moved playhead")

    # set clip color
    current_video_item = current_timeline.GetCurrentVideoItem()
    current_video_item.SetClipColor("Orange")
    print("clip color changed")
