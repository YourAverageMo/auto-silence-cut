<!-- omit in toc -->
# Davinci Resolve FREE Auto Silence Cut
Automatically edit video (non-destructively) by analyzing audio, cut out silence, and import straight into davinci resolve!

- Analyze video based off of **multiple audio tracks**
- **Edit out silence** with adjustable margins
- **Completely free** and runs locally within Davinci Resolve (even on free version)
- 100% Non-destructive
- Process multiple clips simultaneously
- Highlight silent and non-silent parts in timeline
- Automatically create timeline with subclips ready to edit!

**FEATURES ADDED**
- Audio threshold adjustment and auto-silence deletion. 05-25 (thanks [@Schkullie](https://github.com/Schkullie))


> [!NOTE]
> Works best with well processed audio (clearly defined silent parts).
>
> There is a threshold adjustment, but you might have to experiment around with it to get a good result depending on your audio source.

> [!WARNING]
> Blackmagicdesign did remove the ability to use scripts with a GUI in the free version of DavinciResolve with version 19.1 [Source](https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=149311&p=1100366#p1100366)
> 
> This script **still works** on all versions of DR, but the graphical user interface with only function with older versions or DaVinci Resolve Studio. see [Settings Explained](#settings-explained) 'skip this window'

<!-- omit in toc -->
## Love it? Wanna Support?

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/YourAverageMo)

![github-stars-logo_Color](https://github.com/user-attachments/assets/6d67193f-fa3f-420e-9091-2b5e49e9918b)

<!-- omit in toc -->
## Table of Contents
- [Usage Guide](#usage-guide)
- [Requirements](#requirements)
    - [1. Install Python 3.7+](#1-install-python-37)
    - [2. Install Auto-Editor](#2-install-auto-editor)
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
![Step1](https://github.com/user-attachments/assets/7a5c17c3-df8b-441a-84d4-c67064d4dc76)

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
![Step5](https://github.com/user-attachments/assets/8ce35991-1140-4be7-995b-f87efc4cf1bd)

When you're ready, click 'START' and **avoid using the keyboard or mouse** while Auto-Silence-Cut runs. The script will automatically insert the edited (non-destructive) clips into the timeline, and any input during this time could interfere with that process.

The duration of this process depends on how much footage you are processing. For optimal performance, it's recommended to process no more than 45 minutes of footage at a time to prevent DaVinci Resolve from lagging.

Once the process is complete, a message will appear in the console, and the Auto-Silence-Cut window will close automatically.

<!-- omit in toc -->
### Step 6: Adjust Subclips
![Step6](https://github.com/user-attachments/assets/cbc2dda5-4ba2-4ecd-9ffa-217142926c7b)

After Auto-Silence-Cut has added the subclips to the timeline, you can adjust them as needed. Since this process is non-destructive, all subclips reference the original source material, allowing you to extend or contract the handles of each subclip.

If you're unfamiliar with this, refer to the provided GIF for guidance.

- **Silent Clips**: These clips will have no color.
- **Sound Clips**: Clips where sound was detected will be highlighted with the color selected in the settings (`Highlight Color`, default is Orange).

![Step6 2](https://github.com/user-attachments/assets/985bda09-d1b9-4776-abd7-0b388864373a)

<!-- omit in toc -->
### Step 7: Remove Silence
![Step7](https://github.com/user-attachments/assets/71e7ad28-ef21-4029-ad73-7542dfe33a1a)

To remove all the silent clips,

    Timeline -> Select Clips With Color -> Default Color

This will select and highlight all the silent clips in the timeline and from there you can just ripple delete all of them to leave no gaps.

> [!NOTE]
> You can also choose to immediately delete all the silence with the option "Automatically delete detected silence".
>
> **This removes the ability to adjust timings as shown in step 6!**


# Requirements

To ensure full functionality of this project, please follow the steps below to install each required dependency. If you're new to coding or Python, each step includes detailed instructions to help you get started.

### 1. Install [Python 3.7+](https://www.python.org/downloads/)

   This project requires **Python 3.7 or higher**.

   - **Step 1:** Visit the [official Python download page](https://www.python.org/downloads/) and click the button to download the latest version.
   - **Step 2:** Open the downloaded file and follow the installation instructions.
   - **Step 3:** During installation, **make sure to check the box that says "Add Python to PATH"**
   - **Step 4:** Once installed, open your command line (e.g., Command Prompt, Terminal) and type the following command to confirm Python is installed:
     ```bash
     python --version
     ```
     You should see a version number (e.g., `Python 3.10.5`) this means python was successfully installed.

### 2. Install [Auto-Editor](https://github.com/WyattBlue/auto-editor)

   Auto-Editor is a tool that helps with automatic video editing, which is a dependency for this project.

   - **Step 1:** Open your command line (Command Prompt on Windows, Terminal on Mac).
   - **Step 2:** Enter the following command to install Auto-Editor:
     ```bash
     pip install auto-editor
     ```
   - **Step 3:** After the installation completes, check that Auto-Editor is installed by typing:
     ```bash
     auto-editor --help
     ```
     If the command is recognized, you’re all set. If you see an error, try restarting your command line or refer to the [Auto-Editor documentation](https://github.com/WyattBlue/auto-editor) for help.

# Installation
Once you have the required dependencies installing Auto-Silence-Cut is as simple as downloading Auto-Silence-Cut.py and placing it in your scripts folder for DaVinci Resolve.

For Windows: `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility`

For Mac: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility`


# Settings Explained
- **LEFT TRIM MARGIN:** The amount of padding, in seconds, to leave *before* the edit (the left of detected audio)
- **RIGHT TRIM MARGIN:** The amount of padding, in seconds, to leave *after* the edit (the right of detected audio)
- **AUDIO THRESHOLD:** The loudnes above which the audio will be counted as detected (usefull for noisy audio).
- **HIGHLIGHT COLOR:** The color of sound clips
- **EDIT BASED ON THESE TRACKS:** Which audio tracks to use to search for silence. (multiple allowed)
- **AUTOMATICALLY DELETE DETECTED SILENCE:** Automatically deletes all silent parts, so only the audible parts are put on the timeline.
- **SKIP THIS WINDOW:** If checked, next time the script is launched GUI will be skipped and processing will begin immediately. Use this if you always use the same settings.

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
Open up the console in DaVinci Resolve and check why. I tried to code in as much user-friendly error handling as possible but if you still have trouble feel free to open up an issue.

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
