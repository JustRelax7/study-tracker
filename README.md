# Automated Study Tracker Daemon

A zero-friction, headless background daemon for Linux that replaces manual productivity timers. It continuously analyzes facial geometry to log deep-focus study sessions and gracefully handles system interruptions via OS-level event hooks.

## The Problem It Solves
Manual study timers introduce friction. Users frequently forget to start, stop, or pause them when stepping away from the workstation. This project eliminates that friction by moving the tracking to the operating system background, operating silently via systemd.

## Key Architecture & Features

* **Stateless Computer Vision:** Utilizes OpenCV Haar Cascades for rapid facial geometry detection without storing image data.
* **Extreme Optimization:** Engineered to maintain a continuous background footprint of < 3% CPU and ~74 MB RAM via aggressive spatial downscaling and grayscale matrix conversion. Frame detection executes in ~15ms.
* **OS-Level Event Interception:** Integrated with DBus APIs to listen for GNOME screen locks and ACPI lid-close events, automatically pausing the tracker without user input.
* **Debouncing Logic:** Implements a 5-minute hysteresis inactivity buffer to gracefully handle natural movements (e.g., looking away at a textbook or temporary absence), preventing fragmented session logs.

## Repository Structure

* `tracker_daemon.py`: The core computer vision and background tracking logic.
* `report.py`: Regex-based reporting tool to parse logs and calculate total deep-focus time.
* `calibrate.py`: Utility script to test camera positioning and threshold settings.
* `study-tracker.service`: Systemd user service configuration for automated lifecycle management.
* `study-tracker-hook`: ACPI / DBus interception script for handling suspend and lock states.
* `aliases.sh`: Bash shortcuts for rapid control of the daemon.

## Tech Stack

* **Python 3** (Core Logic, `psutil` for profiling)
* **OpenCV** (Haar Cascade Classifiers)
* **Linux Systemd** (User Service Daemonization)
* **DBus & ACPI** (Inter-Process Communication for OS hooks)
* **Bash & Regex** (Lifecycle management and log parsing)

