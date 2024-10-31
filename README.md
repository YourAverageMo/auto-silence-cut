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

# FAQ

# Contribute

# Known Issues


- sometimes extra tracks are created when creating new timeline. No idea why this is happening but i think its a DR problem. It used to cause problems with coloring clips but that should be resolved now.

- there is a case where sometimes the output timeline will be slightly shorter than the original file by a frame or two. I believe this is something to do with the way auto-editor handles cuts.