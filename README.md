# Visual Security System (EXTRA)

This is a Python-based Visual Security System that uses a webcam to detect motion and intrusions in defined zones.

## Prerequisites

Before running this software, ensure you have the following installed on your laptop:

1.  **Python 3.10 or newer**: [Download Python](https://www.python.org/downloads/)
    *   *Note: During installation, make sure to check "Add Python to PATH".*
2.  **Git**: [Download Git](https://git-scm.com/downloads) (Optional, if cloning via command line)
3.  **Webcam**: A functional webcam connected to your computer.

## Installation Steps for Daniel

Follow these steps to get the software running on your local machine:

### 1. Download the Code

You can either clone the repository using Git or download it as a ZIP file.

**Option A: Using Git (Recommended)**
Open your terminal (Command Prompt or PowerShell) and run:
```bash
git clone https://github.com/AxelEdgar/EXTRA.git
cd EXTRA
```

**Option B: Download ZIP**
1.  Go to the GitHub repository page (https://github.com/AxelEdgar/EXTRA).
2.  Click on the green **< > Code** button and select **Download ZIP**.
3.  Extract the ZIP folder to a location on your computer (e.g., Downloads or Desktop).
4.  Open your terminal and navigate to that folder.

### 2. Install Dependencies

It is recommended to use a virtual environment, but you can also install directly.

Run the following command in your terminal to install the necessary libraries:

```bash
pip install -r requirements.txt
```

*Note: If `pip` is not recognized, try `python -m pip install -r requirements.txt` or `pip3 install -r requirements.txt`.*

### 3. Run the Application

Make sure your webcam is not being used by another application (like Zoom or Teams). Then run:

```bash
python main.py
```

## How to Use

-   **Hand Mode (Panning)**: Press **SPACE** to toggle between "Drawing Mode" and "Hand Mode".
    -   In Hand Mode, click and drag to move around the zoomed video.
-   **Drawing Zones**: Switch to "Drawing Mode" (default). Click points on the video to define a security zone. Right-click to close the polygon.
-   **Arming**: Use the visible controls to "ARM" the system (Set HOT).
-   **Exit**: Press **Q** or click the exit button to close the application.

## Troubleshooting

-   **"Module not found" error**: Ensure you ran the `pip install` command successfully.
-   **Camera error**: Check if another app is using the camera. You may need to change `CameraManager(0)` to `CameraManager(1)` in `main.py` if you have multiple cameras.
