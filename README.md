\# Universal Media Downloader



A Python-based media downloading backend that detects supported URLs and downloads videos, audio, and images using platform-specific extraction and processing tools.



\## 🚀 Current Features



\- URL validation for HTTP and HTTPS links

\- Automatic media type detection

\- Video downloading

\- Audio extraction and MP3 conversion

\- Direct image downloading

\- Best available video and audio selection

\- FFmpeg-based video/audio merging

\- Sequential, non-overwriting filenames

\- Temporary file cleanup

\- FFprobe-based media validation

\- Instagram post and carousel detection

\- Instagram image carousel downloading

\- Instagram carousel image previews

\- Mixed Instagram carousel detection

\- Automated test suite with pytest



\## 📌 Supported Media



\### YouTube



\- Videos

\- Shorts

\- Audio extraction



\### Instagram



\- Single image posts

\- Single video posts

\- Image carousels

\- Mixed image/video carousels



\### Direct Image URLs



Supported image formats include:



\- JPG / JPEG

\- PNG

\- WEBP

\- GIF

\- BMP

\- TIFF

\- AVIF



\## ⚠️ Current Instagram Carousel Limitation



Instagram carousel videos are detected but are not currently downloaded in V1.



For mixed carousels:



\- Images can be previewed and downloaded.

\- Video items are detected.

\- Carousel video downloading is planned for a future version.



\## 🏗️ Project Structure



```text

UniversalMediaBot/

│

├── downloads/                  # Generated media files

├── logs/                       # Runtime logs

├── manual/                     # Manual real-world tests

│   ├── compatibility\_test.py

│   ├── download\_test.py

│   └── instagram\_mixed\_carousel\_test.py

│

├── src/

│   ├── detector.py             # URL/media detection

│   ├── downloader.py           # Video/audio downloading

│   ├── file\_manager.py         # Sequential filename management

│   ├── image\_downloader.py     # Direct image downloading

│   ├── media\_service.py        # Main media workflow

│   ├── processors.py           # FFmpeg/FFprobe processing

│   ├── validators.py           # URL validation

│   │

│   ├── platforms/

│   │   └── instagram.py        # Instagram extraction

│   │

│   └── services/

│       ├── carousel\_service.py # Carousel session management

│       └── preview\_service.py  # Image preview handling

│

├── tests/                      # Automated tests

│

├── .gitignore

├── requirements.txt

└── README.md

