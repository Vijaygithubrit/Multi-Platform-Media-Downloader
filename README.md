# UniversalMediaBot

A modular Python-based media downloader backend that detects public media URLs, determines the available media type, downloads video, audio, and images, processes media with FFmpeg, and safely stores final files with automatic sequential naming.

The current version is a stable local CLI backend designed as the foundation for a future Telegram media downloader bot.

---

## 🚀 Features

### 🎬 Video & Audio

- Automatic media type detection
- Best available video quality
- Best available audio source
- Video + audio stream merging with FFmpeg
- Audio extraction and MP3 conversion
- FFprobe verification of downloaded video
- Automatic sequential filenames
- Temporary-file processing before permanent storage
- Safe final-file handling

### 🖼️ Image Downloads

Supports direct image URLs including:

- JPG / JPEG
- PNG
- WEBP
- GIF
- BMP
- TIFF
- AVIF

The downloader determines the image format using HTTP content type and URL information.

### 🌐 Current Platform Support

The backend currently supports workflows involving:

- YouTube videos
- YouTube Shorts
- Instagram posts
- Instagram Reels
- Instagram images
- Instagram videos
- Instagram image carousels
- Instagram mixed image/video carousels
- Facebook posts
- Facebook Reels
- Direct image URLs
- Other websites supported by configured `yt-dlp` extractors

> Platform support depends on the underlying extractor and the current behavior of each website. Support for a site does not guarantee that every individual URL will work.

---

## 📸 Instagram Carousel Support

Instagram carousels receive dedicated handling.

### Image-only carousels

Supported operations:

- Download all supported images
- Select specific items
- Preview individual images
- Download remaining items
- Select more items during the same session

### Mixed image/video carousels

Images are currently supported.

Carousel videos are detected but downloading them is intentionally deferred to a future version.

Example:

```text
Item 1 → Image → Supported
Item 2 → Video → Not yet supported
Item 3 → Image → Supported
