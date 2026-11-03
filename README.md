# Chess-Playing-Robotic-Arm-Prototype

**A-level Computer Science project (OCR H446)**  
**Author:** Sanjeev Giritharan

This repo is a computer-vision and robotics project that allows a computer to play chess on a physical chessboard using an Arduino-controlled robotic arm.

## Repository history and continuation

This project has two related repositories:

- **Magnus Autonomous Prime** - the [original codebase submitted for my A-level project.](https://github.com/Vertical-JEEV/MAGNUS-AUTONOMOUS-PRIME) It is kept as a historical record of the submitted work.
- **Chess Playing Robotic Arm (Prototype)** - the repository where I continued working after submission.

This repository is the continuation of my A-level project after I had submitted it. I had access to the Braccio arm for only a limited period after submission. Once I had to return it, I no longer had the hardware needed to test and continue the full physical chess-playing system. As a result, development of the complete robotic system paused. I would like to revisit the project in the future, particularly the unfinished computer-vision work, when I have access to suitable hardware.

## Project Goals

The project explored how to combine computer vision, chess software, robotics, and database functionality to create a system capable of playing chess on a physical chessboard.

The main objectives were:

- **Chessboard Detection and Grid Mapping:** Use computer vision to detect the chessboard and map it onto an 8×8 grid. Each square was associated with four corner pixel coordinates, defining its individual bounding box for subsequent image processing.
- **Chess-Piece Movement Detection:** Use image differencing between consecutive frames, examining the bounding boxes of individual chess squares to identify changes in their visual contents and help determine which squares were affected by a move.
- **Chess-Engine Integration:** Generate chess moves using a chess engine and maintain the current state of the game.
- **Robotic-Arm Control:** Use an Arduino-controlled robotic arm to pick up and place the appropriate chess pieces on the physical board.
- **Graphical User Interface:** Develop a graphical interface for interacting with the chess game and its associated functionality.
- **Database Functionality:** Save and load game information, as well as store chessboard dimensions and chess-piece height measurements required for robotic-arm positioning.

Some parts of this workflow were more complete than others. In particular, the chessboard detection and grid mapping received substantially more development time than the later piece-movement detection.

## Technologies

| Technology | Role in the project |
| --- | --- |
| Python | Main application and software logic |
| Kivy | Desktop graphical user interface |
| OpenCV | Image processing and chessboard detection |
| NumPy | Image arrays and coordinate/matrix calculations |
| PySerial | Serial communication between the computer and Arduino |
| SQLite3 | Saving and retrieving game information |
| Stockfish | Chess-engine integration |
| Arduino Uno Rev3  | Control of the robotic arm |
| Arduino Tinkerkit Braccio | Physical robotic arm |

## System overview

The project was designed as a collection of modules, each responsible for a different part of the system.

At a high level, the intended workflow was:

1. A webcam captures an image of the physical chessboard.
2. Computer vision locates the chessboard and finds the 4 corners of the chessboard to then get a top-down view of the board by using those detected corners.
3. Apply a corner detection algorithm to find the 81 corners and map it to chess-square identifiers such as `a1`, `b1`, and `h8`.
4. Image differencing compares board frames and identifies a square whose image region has changed.
5. The chess pieces positions are represented digitally using FEN.
6. Stockfish calculates a move using the current FEN.
7. The move can be translated into physical target positions for robotic-arm movement.
8. The GUI and database provide game setup, calibration, and saved-game functionality.

The source files show individual components and prototypes for this workflow. The full process was not completely integrated or verified as a working end-to-end system.

## Computer vision

Computer vision was one of the central areas of the project. The camera was attached to the robotic-arm which meant it viewed the board from an angle, so the software needed to locate the board and account for perspective distortion before analysing its squares.

### Chessboard detection and perspective correction

Implemented in `corner_detection.py`

The process includes:

1. **Image preprocessing**
   - Convert the camera frame to grayscale.
   - Apply Gaussian blur to reduce image noise.
   - Apply thresholding to create a binary image for contour detection.

2. **Locate the outer chessboard**
   - Find contours in the thresholded image.
   - Select the largest contour as the candidate chessboard.
   - Approximate its contour to obtain the four outer board corners.

3. **Perspective transformation**
   - Use the four detected outer corners to calculate a perspective transformation matrix.
   - Warp the angled board image into a roughly top-down, square representation.
   - Keep an inverse transformation matrix so coordinates detected in the transformed image can be mapped back to the original camera image.

This perspective correction was important because the physical board could be viewed from different camera angles. Working with a rectified board made it easier to identify the intersections and associate them with chess squares.

### Detecting the 81 chessboard intersections

After perspective correction, the software uses the **Shi–Tomasi corner-detection algorithm** (`cv2.goodFeaturesToTrack`) to find the 81 intersections of a standard 8×8 chessboard.

The detected corners are refined with sub-pixel corner detection using `cv2.cornerSubPix`. The code then sorts the points into rows and columns to establish a consistent order.

The 81 intersections form the boundaries of the 64 squares: each square is defined by four neighbouring intersection points.

### Mapping squares to pixel coordinates

The `map_corners_to_uci_positions()` method associates each square with a chess-coordinate identifier, such as `a1` or `e4`.

For every square, the mapping stores four pixel-coordinate corners. These coordinates are transformed back into the original camera-image coordinate system using the inverse perspective transformation.

This mapping is used by the image-differencing module to extract the image region corresponding to a particular square.


## Chess-piece movement detection

Implemented in `image_difff_track.py` through the `ChessboardChangeDetector` class.

The movement-detection prototype compares two camera frames:

1. Store an earlier frame and a newer frame.
2. Convert both frames to grayscale.
3. Apply histogram equalisation to improve contrast.
4. Apply Gaussian blur to reduce noise.
5. Calculate the absolute pixel difference between the frames.
6. Threshold the difference image to highlight changed regions.
7. Iterate through the chess-square coordinate mapping.
8. Calculate a rectangular bounding region for each square from its four pixel corners.
9. Examine the thresholded difference within each square's region.
10. Return a chess-square identifier when a changed region is detected.

The idea was to identify which chess squares changed after a player moved a piece. The detected square information could then contribute to updating the digital chess position.

**This was an unfinished prototype.** Though the implementation returns the UCI positions of the 2 sqaures that have changed. It is not as robust as the chessboard detection pipeline due to lighting changes, shadows, and the appearance of chess pieces can all affect the difference image. More work would be needed to robustly identify chess piece movement.

## Camera calibration

Implemented in `camera_calibration.py` through the `CameraCalibration` class.

The calibration module was designed to estimate camera parameters using chessboard observations.

It includes:

- Generation of corresponding 3D chessboard corner coordinates from the physical board dimensions.
- Collection of detected image-corner coordinates from camera frames.
- OpenCV camera calibration using `cv2.calibrateCamera`.
- Calculation of an optimal camera matrix.
- Estimation of rotation and translation using `cv2.solvePnP`.
- Conversion of a rotation vector into a rotation matrix.
- Construction of an extrinsic matrix.
- Calculation of a reprojection error estimate.

The calibration interface was intended to let the user enter physical chessboard dimensions and chess-piece heights. These measurements were relevant to translating board positions into physical positions for the robotic arm.

## Chess engine and game state

Implemented in `chess_engine.py` through the `ChessEngine` class.

The chess engine uses:

- **Stockfish** as the chess engine.
- **python-chess** to represent chess positions, validate moves, and communicate with the engine.

The class supports:

- Initialising a game from a FEN position.
- Converting a requested ELO value into a Stockfish skill level.
- Requesting a best move from Stockfish.
- Retrieving the current board position as FEN.
- Checking whether a FEN position is valid.
- Checking whether a move is legal before applying it to the internal board.
- Checking for checkmate, stalemate, insufficient material, and threefold repetition.

The engine is configured to search for a move with a short time limit. The skill-level conversion provides a simple way to vary the engine's playing strength through the game setup.

FEN (Forsyth–Edwards Notation) is used to represent the chessboard position. The intention was to keep a digital representation of the game and update it as moves were made.

The project also explored using UCI move notation to represent moves between chess squares. The physical chessboard, image-detection results, and digital chess state would need to remain synchronised for the full system to work reliably.

## Graphical user interface

Implemented in `interface.py` using **Kivy**.

The interface code defines a screen-based application with a `ScreenManager` and several screens.

### Main menu

The main menu provides navigation to:

- Starting a new game.
- Loading an existing game.
- Opening the calibration menu.

### New-game menu

The new-game screen includes:

- A slider for selecting the engine's ELO setting.
- A toggle for selecting White or Black.
- Start and exit buttons.

The selected settings are currently printed when starting the game. The interface provides the structure for game setup, but the full game-start integration is not complete in this file.

### Load-game menu

The load-game screen displays a table-like list of example saved games and allows a row to be selected.

In the current source, the displayed game records are **placeholder data**, rather than being populated from the SQLite games database. The interface therefore demonstrates the intended load-game interaction, but does not fully implement database-backed game loading.

### Calibration menu

The calibration screen provides input fields for:

- Chessboard dimensions.
- Pawn height.
- Rook height.
- Knight height.
- Bishop height.
- Queen height.
- King height.

It checks that the dimensions follow a `width x height` format and that the measurements are positive numeric values. The current code prints the validated values and clears the input fields; saving these values into the database is not connected in this screen.

### Digital chessboard

The game screen draws an 8×8 chessboard using Kivy graphics and piece images. It reads a FEN-like board representation to determine which pieces to display.

The interface code establishes the visual board and screen structure, but the full interactive chess gameplay and physical robotic-arm integration are not completed in this file.

## Database

Implemented in `database.py` using **SQLite**.

The database module contains a general `Database` class and two specialised database classes.

### Games database

`GamesDatabase` is designed to store information such as:

- Game name.
- FEN position.
- ELO setting.
- User score.
- Robot score.
- Player colour.
- Next move.

It includes methods to insert, read, update, and delete records, along with a check to prevent empty or duplicate game names.

### User-parameters database

`UserParametersDatabase` is designed to store calibration and physical configuration values:

- Chessboard dimensions.
- Heights of individual chess pieces.
- Camera intrinsic parameters.
- Camera distortion parameters.
- Camera extrinsic parameters.

These values were intended to support calibration and the conversion between camera observations and physical robotic-arm positioning.

The database classes include basic record-management functionality and example test routines. However, the GUI's saved-game and calibration screens are not fully connected to all of these database operations.

## Robotic-arm control

The physical system was based on an **Arduino Tinkerkit Braccio robotic arm**, controlled through an Arduino.

### Python-side communication and inverse kinematics

Implemented in `comunicate_to_robotic_arm.py` through the `ArduinoComunicator` class.

The module uses:

- `PySerial` for the planned serial communication with an Arduino.
- `PyBullet` to load a Braccio URDF model and calculate inverse kinematics.
- Python's `math` module to convert calculated joint angles from radians to degrees.

The `move_arm()` method accepts a target position, calculates joint angles using PyBullet inverse kinematics, converts the angles to degrees, rounds them, and formats them as a comma-separated string.

The serial communication code would send the formatted joint angles to the Arduino. The Python module demonstrates the inverse-kinematics calculation, but it should not be described as currently providing complete active Arduino control.

### Arduino firmware

`move_robotic_arm.ino` contains the Arduino-side code for the Braccio arm. It receives the joint-angle information and executes those angles in the braccio library.

The Python and Arduino components represent the planned communication path between the chess software and the physical robot. The complete physical chess-playing workflow was not fully integrated or tested.

## Limitations and unfinished development

This project was developed under the time constraints of an A-level Computer Science assessment, followed by a period of continued development after submission.

Some of the main limitations and unfinished areas include:

- **Image differencing:** The prototype can detect changed square regions, but it does not reliably interpret a complete chess move in all situations.
- **Chess-state synchronisation:** The physical board, camera-detected changes, and digital FEN position would need more robust synchronisation.
- **Special chess moves:** Special cases such as castling, en passant, and pawn promotion were not fully implemented in the physical move-detection and robotic workflow.
- **Robotic-arm integration:** Inverse kinematics was explored, but the full process of translating a chess move into reliable physical piece movement was unfinished.
- **GUI integration:** Some interface screens use placeholder data or print values rather than completing the intended database or gameplay operations.
- **Calibration workflow:** The calibration components exist, but the full process of applying calibration data to physical arm movements requires further development.

These limitations reflect the state of the project in the available source files and the circumstances under which development paused.

## Future development

If I return to the project in the future, I would like to focus on:

- Improving chess-piece and move recognition under different lighting conditions and camera angles.
- Connecting detected moves reliably to the digital FEN chess state.
- Completing the integration between Stockfish, the GUI, and the physical board.
- Improving robotic-arm calibration and physical piece placement.
- Completing the database-backed game saving and loading workflow.
- Testing the complete system with suitable hardware.
