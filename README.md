# GVAS Save Editor (Tree View)

A Python-based graphical user interface (GUI) for editing Unreal Engine GVAS (`.sav`) files. This tool provides a user-friendly tree structure to navigate, search, and modify save data, including support for embedded JSON strings commonly found in modern UE games.

## Features

* **Visual Tree Navigation**: Explore the complex nested structure of `.sav` files easily.
* **Deep Search**: Quickly find specific keys or values across the entire save file.
* **In-Place Editing**: Modify primitive values (strings, integers, floats, booleans) directly within the interface.
* **Embedded JSON Support**: Automatically detects, parses, and re-compresses JSON strings stored inside save properties.
* **Cross-Platform Logic**: Designed to work on Windows and other OS environments where the `uesave` tool is available.

## Requirements

1.  **Python 3.x**: Ensure Python is installed on your system.
2.  **uesave**: This GUI acts as a wrapper for the `uesave` command-line utility.
    * You must have the `uesave` executable in the same directory as the script.
    * **Credits**: This tool relies on the excellent work of [trumank/uesave-rs](https://github.com/trumank/uesave-rs).

## How to Use

### Method A (Recommended)
* **Double-click** the `uesavegui.bat` file to launch the application.

### Method B (Manual)
1.  **Setup**: Place `gvas_gui.py` and the `uesave` executable in the same folder.
2.  **Run**: Execute the script via terminal or command prompt:
    ```bash
    python gvas_gui.py
    ```
3.  **Load**: Click **"1. Load .sav File"** and select your game save.
4.  **Edit**: 
    * Navigate the tree or use the **Search** bar to find the property you want to change.
    * Select the leaf node (the specific value).
    * Enter the new value in the edit panel at the bottom and click **"Update Value"**.
5.  **Save**: Click **"2. Save as .sav File"** to export your modified save.

## Important Notes

* **Backups**: Always create a backup of your original `.sav` files before editing.
* **Data Types**: The editor attempts to preserve the original data type (e.g., keeping an integer as an integer). Ensure your input matches the expected type to avoid errors.
* **UESAVE Version**: Ensure you are using a version of `uesave` compatible with your specific game's save format.

## Credits

This project is a GUI wrapper. The heavy lifting of parsing and rebuilding the GVAS format is handled by:
* **uesave**: [https://github.com/trumank/uesave] (for windows/macos/linux users)
