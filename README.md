# MN-1: Engineered for Listening, Built in Python

![Dark Theme ](https://github.com/user-attachments/assets/77bcd1d6-5090-4e3e-9aae-e1541daa17a9)


Channelling the spirit of Braun and retro HiFi gear from the past, the **MN-1** is a minimal Python music player supporting **MP3, WAV, and FLAC** formats, designed for the discerning ear.

Experience music uncluttered. The clean interface and integrated **waveform & oscilloscope displays** focus purely on the listening experience, free from distractions – just beautiful sound.

The MN-1 strips away the unnecessary complexities of modern music players, offering a streamlined experience centered around what truly matters: **your music**.

> **Pro tip:** Change your theme and accent colours via the `MN-1` button for a fresh aesthetic look!
> 

![Light Theme ](https://github.com/user-attachments/assets/c7271f49-2c7f-47dc-9bc6-1b997efe5e7e)


## Features

*   **Pure Python Core:** Built from the ground up in Python, ensuring a clean and efficient foundation.
*   **Simple, Intuitive Interface:** Inspired by classic HiFi components, the MN-1 prioritises ease of use and a distraction-free listening environment. No bloated menus or unnecessary features.
*   **Real-time Waveform & Oscilloscope Display:** Visualize your music as it plays with captivating and informative waveform and oscilloscope displays. Go beyond just hearing – see the dynamics of your tracks.
*   **Focus on Sound Quality:** The MN-1 is designed to deliver your choice of music formats (MP3, FLAC, WAV) with clarity and fidelity, letting the music speak for itself.
*   **Open Source Spirit:** The MN-1 is open source and welcomes contributions from the community. Built by music lovers, for music lovers.

## Getting Started

Ready to experience minimalist music? Here's how to get the MN-1 running:

### Prerequisites

*   **Python 3.x:** Ensure you have Python 3 (preferably 3.8 or later) installed on your system. You can download it from [python.org](https://www.python.org/).
*   **FFmpeg:** Required by the `pydub` library for loading various audio formats. Download and install it from [ffmpeg.org](https://ffmpeg.org/) and ensure it's added to your system's PATH.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone [repository-url] # Replace [repository-url] with the actual GitHub repository URL
    cd mn-1 # Navigate into the cloned directory
    ```

2.  **Install Dependencies:**
    It's highly recommended to use the provided `requirements.txt` file to install the specific versions of libraries used during development:
    ```bash
    pip install -r requirements.txt
    ```
    Alternatively, you can install the core dependencies manually (though versions might differ):
    ```bash
    pip install customtkinter pygame Pillow mutagen numpy pydub matplotlib
    ```

### Usage

1.  **Run the Player:**
    ```bash
    python MN-9.py
    ```
    *(On Windows, you can also use the provided `.exe` file found in the Bonus link below).*

2.  **Loading Music:** Click the `LOAD` button to open a file dialog and select `.mp3`, `.wav`, or `.flac` files.
3.  **Playback Controls:** Use the standard playback buttons (Play `▶`, Pause `II`, Previous `◄◄`, Next `►►`) via mouse clicks. Seek through the track by clicking or dragging on the main waveform display or the slider below it.

## Technical Details

*   **Language:** Python 3
*   **GUI:** CustomTkinter
*   **Audio Backend:** Pygame Mixer
*   **Audio Processing:** Pydub, Mutagen, NumPy
*   **Visualization:** Matplotlib
*   **Platform:** Cross-platform (tested on Windows, should run on macOS and Linux with dependencies installed).

## Contributing

MN-1 is an open-source project and welcomes contributions! If you'd like to contribute, please:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Make your changes (following clean coding practices and Python conventions).
4.  Test your changes thoroughly.
5.  Submit a pull request with a clear description of your changes.

We appreciate contributions that enhance the simplicity, functionality, and sound quality of MN-1, while staying true to the minimalist design philosophy.

## License

This project is licensed under the **[Your License Name Here - e.g., MIT License, GPL v3]**. See the `LICENSE` file for details. *(Remember to add a LICENSE file to your repository!)*

---

## Bonus

Since you read this far, might as well have some free tracks to listen to and the pre-compiled `.exe` file for Windows:

[**MN-1 Bonus Files (Google Drive)**](https://drive.google.com/drive/folders/1dzLRZiWVLEaIj0fswMHnzd7bWKeOt3cc?usp=sharing)

---

Enjoy the pure sound of MN-1!

*Bohemai*


