<!-- omit in toc -->
# Davinci Resolve FREE Auto Silence Cut
<!-- add summary here -->
<!-- mention nondestructive -->

<!-- omit in toc -->
## Table of Contents
- [Usage Guide](#usage-guide)
- [Requirements](#requirements)
- [Installation](#installation)
- [Settings Explained](#settings-explained)
- [FAQ](#faq)
    - [Is multi-track audio supported?](#is-multi-track-audio-supported)
    - [Can I process multiple clips at once?](#can-i-process-multiple-clips-at-once)
    - [Where are my settings saved?](#where-are-my-settings-saved)
    - [How do I remove silent clips from the timeline?](#how-do-i-remove-silent-clips-from-the-timeline)
    - [Can I adjust clips after Auto-Editor runs?](#can-i-adjust-clips-after-auto-editor-runs)
    - [I ran the script but nothing happened?](#i-ran-the-script-but-nothing-happened)
- [Contribute](#contribute)
- [Known Issues](#known-issues)

# Usage Guide

<!-- omit in toc -->
### Step 1: Add Clips to the 'Master' Folder
Drag and drop all the clips you want Auto-Silence-Cut to process into the 'MASTER' folder in DaVinci Resolve. 

> **Note:** The current version of Auto-Silence-Cut processes **all** video files in the 'MASTER' folder.

Although you can process multiple clips simultaneously, it's recommended to only do a few at a time in case something goes wrong. Additionally, having too many clips on the timeline can cause DaVinci Resolve to slow down.

<!-- omit in toc -->
### Step 2: Open the Console
    Workspace -> Console

<!-- omit in toc -->
### Step 3: Open Auto-Silence-Cut
    Workspace -> Scripts -> Auto-Silence-Cut

<!-- omit in toc -->
### Step 4: Adjust Settings
A popup window will appear, allowing you to configure how Auto-Silence-Cut processes the video files. Refer to the [Settings Explained](#settings-explained) section for detailed explanations of each option.

Settings are automatically saved upon closing in the following location: `Documents\Auto Editor\settings.json`

The next time you run Auto-Silence-Cut, it will load the previously used settings. This is especially important for how the "Skip this window" option behaves.

If the `settings.json` file is missing or has been deleted, default settings will be restored and saved to the same location.

<!-- omit in toc -->
### Step 5: Click 'START'
When you're ready, click 'START' and **avoid using the keyboard or mouse** while Auto-Silence-Cut runs. The script will automatically insert the edited (non-destructive) clips into the timeline, and any input during this time could interfere with that process.

The duration of this process depends on how much footage you are processing. For optimal performance, it's recommended to process no more than 45 minutes of footage at a time to prevent DaVinci Resolve from lagging.

Once the process is complete, a message will appear in the console, and the Auto-Silence-Cut window will close automatically.

<!-- omit in toc -->
### Step 6: Adjust Subclips
After Auto-Silence-Cut has added the subclips to the timeline, you can adjust them as needed. Since this process is non-destructive, all subclips reference the original source material, allowing you to extend or contract the handles of each subclip.

If you're unfamiliar with this, refer to the provided GIF for guidance.

- **Silent Clips**: These clips will have no color.
- **Sound Clips**: Clips where sound was detected will be highlighted with the color selected in the settings (`Highlight Color`, default is Orange).

<!-- omit in toc -->
### Step 7: Remove Silence
To remove all the silent clips,

    Timeline -> Select Clips With Color -> Default Color

This will select and highlight all the silent clips in the timeline and from there you can just ripple delete all of them to leave no gaps.


# Requirements

List of all required dependencies:

- [Python](https://www.python.org/downloads/)
- [Auto-Editor](https://github.com/WyattBlue/auto-editor)
  ```
  pip install auto-editor
  ```

# Installation
Once you have the required dependencies installing Auto-Silence-Cut is as simple as downloading Auto-Silence-Cut.py and placing it in your scripts folder for DaVinci Resolve.

For Windows: `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility`

For Mac: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility`


# Settings Explained
- **LEFT TRIM MARGIN:** The amount of padding, in seconds, to leave *before* the edit (the left of detected audio)
- **RIGHT TRIM MARGIN:** The amount of padding, in seconds, to leave *after* the edit (the right of detected audio)
- **HIGHLIGHT COLOR:** The color of sound clips
- **EDIT BASED ON THESE TRACKS:** Which audio tracks to use to search for silence. (multiple allowed)
- **SKIP THIS WINDOW:** If checked, next time the script is launched GUI will be skipped and processing will begin immediatly. Use this if you always use the same settings.

# FAQ

### Is multi-track audio supported?
Yes, silence detection across multiple audio tracks is allowed. Select which audio tracks you would like to process in the pop-up window.


### Can I process multiple clips at once?
Yes, you can process multiple clips simultaneously by adding them to the 'MASTER' folder. However, for optimal performance and to avoid potential issues, it's recommended to only process a few clips at a time.

### Where are my settings saved?
Auto-Editor saves settings automatically to:

    Documents\Auto Editor\settings.json

These settings are loaded the next time you run Auto-Editor. If the file is deleted or missing, default settings are restored and saved.

### How do I remove silent clips from the timeline?
After Auto-Editor adds the subclips to the timeline, silent clips are highlighted with no color. You can remove them by selecting:

    Timeline -> Select Clips With Color -> Default Color

This selects all silent clips, allowing you to ripple-delete them and remove gaps from your timeline.

### Can I adjust clips after Auto-Editor runs?
Yes, since the process is non-destructive, all subclips reference the original source material. You can extend or contract the handles of each subclip as needed.

### I ran the script but nothing happened?
Open up the console in DaVinci Resolve and check why. I tryied to code in as much user-friendly error handling as possible but if you still have trouble feel free to open up an issue.

# Contribute
If you got a fix in mind or feel like you could improve upon Auto-Silence-Cut feel free to make a fork of this repo, create a new branch, and submit a pull request. As long as the code is well documented and readable, I'd love to see it through!

The Resolve API is very hard to navigate so here are some helpful resources:
- [Unofficial Davinci Resolve API Docs](https://deric.github.io/DaVinciResolve-API-Docs/)
- [More Detailed Davinci Resolve API Reference](https://resolvedevdoc.readthedocs.io/en/latest/API_basic.html)
- [DaVinci Resolve Fusion Scripting Manuel](https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf)
- [Auto-Editor Github](https://github.com/WyattBlue/auto-editor)

# Known Issues

- sometimes extra tracks are created when creating new timeline. No idea why this is happening but I think its a DR problem.

- there is a case where sometimes the output timeline will be slightly shorter than the original file by a frame or two. I believe this is something to do with the way auto-editor handles cuts.