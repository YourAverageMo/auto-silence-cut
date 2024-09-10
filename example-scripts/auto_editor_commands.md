# Current CLI:

exports as dr timeline:  
`auto-editor test.mkv --edit "(audio #:stream 1)" --export resolve --silent-speed 1 --video-speed 1`

exports as individual clips:  
`auto-editor test.mkv --edit "(audio #:stream 1)" --export clip-sequence --silent-speed 1 --video-speed 1 --my-ffmpeg --keep-tracks-separate`

# seems to work:

`auto-editor test.mkv --edit "(or audio:threshold=0.5,stream=0 audio:stream=1)" --export resolve`

`auto-editor test.mkv --edit "(or audio:stream=0,threshold=0.5 audio:stream=1)" --export resolve`

`auto-editor test.mkv --edit "(audio 0.05 #:stream 0)" --export resolve`


# doesnt work:

`auto-editor test.mkv --edit "(audio: threshold = 0.5, stream = 0)" --export resolve`