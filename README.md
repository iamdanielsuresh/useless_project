<img width="1280" alt="readme-banner" src="https://github.com/user-attachments/assets/35332e92-44cb-425b-9dff-27bcf1023c6c">

# Voice-Controlled Volume Adjuster 🎯

## Basic Details
### Team Name: KrazyPitz
### Team Members
- Team Lead: Daniel Suresh - CUSAT
- Member 2: Sreeram P - CUSAT
- Member 3: Niju Roy - CUSAT

### Project Description
A voice-controlled application that turns your music up or down based on how loudly you yell at it! The app uses real-time audio processing to detect voice intensity and adjusts system volume accordingly.

### The Problem (that doesn't exist)
Control your volume by yelling—because who needs buttons when you have lungs? In a world where touching volume controls is just too mainstream, we bring you the solution nobody knew they needed!

### The Solution (that nobody asked for)
An app that adjusts your device's volume based on how loudly you yell—perfect for those moments when your voice needs to be heard... by your speakers! 

## ✨ Key Features
- 🎤 Real-time voice intensity detection
- 🎚️ Dynamic volume adjustment with smoothing
- 📊 Multiple visualization modes with live graphs
- 🔧 Smart calibration system for any environment
- 💻 Cross-platform compatibility (Windows/Mac/Linux)
- ⚡ Low-latency performance optimization
- 🎵 Optional audio feedback
- 🔄 Auto-recovery from audio stream failures
- ⌨️ Convenient keyboard shortcuts

## 🛠️ Technical Details

### System Requirements
- Python 3.8 or higher
- Operating System: Windows 10+, macOS 10.15+, or Linux (with PulseAudio)
- Microphone access
- Admin privileges (for system volume control)

### Dependencies
```
python >= 3.8
tkinter >= 8.6
sounddevice >= 0.4.4
numpy >= 1.21.0
matplotlib >= 3.4.0
pygame >= 2.1.0
pycaw >= 20181226 (Windows only)
comtypes >= 1.1.10 (Windows only)
```

### Project Structure
```
voice_volume_controller/
├── main.py                 # Application entry point
├── config/
│   └── settings.json      # User configuration
├── src/
│   ├── audio/
│   │   ├── processor.py   # Audio processing
│   │   └── controller.py  # Volume control
│   ├── gui/
│   │   ├── main_window.py # Main interface
│   │   └── widgets.py     # Custom widgets
│   └── utils/
│       ├── calibration.py # Calibration logic
│       └── logging.py     # Logging setup
├── logs/                  # Application logs
└── tests/                 # Unit tests
```

### Detailed Installation Guide

#### 1. Basic Installation
```bash
# Clone the repository
git clone https://github.com/iamdanielsuresh/useless_project.git

# Navigate to project directory
cd useless_project

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install required packages
pip install -r requirements.txt
```

#### 2. Platform-Specific Setup

##### Windows
```bash
# Install Windows-specific dependencies
pip install pycaw comtypes
```

##### Linux
```bash
# Install PulseAudio development files
sudo apt-get install libpulse-dev python3-dev
```

##### macOS
```bash
# No additional steps required
```

### Troubleshooting Common Installation Issues

1. **Missing Compiler Error**
   ```bash
   # Windows
   pip install wheel
   
   # Linux
   sudo apt-get install python3-dev build-essential
   ```

2. **PortAudio Error**
   ```bash
   # Linux
   sudo apt-get install portaudio19-dev
   
   # macOS
   brew install portaudio
   ```

## 🎮 Usage Guide

### Quick Start
1. Launch the application:
   ```bash
   python main.py
   ```
2. Click "Start Calibration" and follow the prompts
3. Make some noise to calibrate
4. Click "Start Monitoring" to begin voice control

### Keyboard Shortcuts
- `Space`: Toggle monitoring
- `C`: Start calibration
- `Esc`: Exit application
- `↑`: Increase sensitivity
- `↓`: Decrease sensitivity

### Calibration Guide
1. **Environment Setup**
   - Find a quiet space
   - Keep consistent distance from microphone
   - Close other audio applications

2. **Calibration Process**
   - Click "Start Calibration"
   - Make noise at different volumes
   - Wait for 15 seconds
   - Check calibration results

3. **Fine-tuning**
   - Adjust sensitivity slider
   - Test with different volumes
   - Recalibrate if environment changes

### Visualization Modes

1. **Line Graph**
   - Real-time intensity tracking
   - Historical volume changes
   - Adjustable time window

2. **Bar Graph**
   - Current intensity level
   - Current volume level
   - Instant feedback

3. **Meter**
   - VU meter style display
   - Professional audio visualization
   - Peak level indicators

## 🔧 Advanced Configuration

### Configuration File (settings.json)
```json
{
  "sensitivity": 1.0,
  "max_history": 100,
  "update_interval": 100,
  "audio_feedback": true,
  "visualization_mode": "Line Graph",
  "calibration": {
    "min": 0,
    "max": 100
  }
}
```

### Performance Optimization
- Adjust `update_interval` for smoother/faster response
- Modify `max_history` for memory usage
- Enable/disable audio feedback
- Fine-tune calibration values

## 🐛 Troubleshooting Guide

### Common Issues

1. **No Audio Input**
   - Check microphone permissions
   - Verify default input device
   - Run audio diagnostics

2. **High Latency**
   ```python
   # Adjust these values in config
   "update_interval": 50,  # Decrease for faster response
   "max_history": 50      # Decrease for better performance
   ```

3. **Calibration Problems**
   - Ensure quiet environment
   - Check microphone sensitivity
   - Verify audio input levels

### Error Recovery
The application includes automatic recovery for:
- Audio stream failures
- Volume control errors
- System integration issues

## Team Contributions
- Daniel Suresh: 
  - Project architecture
  - Core audio processing implementation
  - Performance optimization
- Sreeram P:
  - GUI development
  - Visualization components
  - Documentation
- Niju Roy:
  - Cross-platform compatibility
  - Testing and debugging
  - Windows volume control integration

## Known Limitations
- May require recalibration in different noise environments
- Brief latency during initial startup
- System volume control requires appropriate permissions
- Performance may vary based on system specifications

## Future Improvements
- [ ] Machine learning-based noise detection
- [ ] Mobile app version
- [ ] Network-based remote control
- [ ] Custom visualization plugins
- [ ] Voice command integration
- [ ] Multi-device support

## Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---
Made with ❤️ at TinkerHub Useless Projects

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProject--24-24?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)
