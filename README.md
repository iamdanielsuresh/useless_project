# Voice-Controlled Volume Adjuster 🎯
### Where Volume Control Gets Vocal

## Basic Details
### Team Name: KrazyPitz
### Team Members
| Role | Name | Institution |
|------|------|-------------|
| Team Lead | Daniel Suresh | CUSAT |
| Member | Sreeram P | CUSAT |
| Member | Niju Roy | CUSAT |

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
voice-controlled-volume-adjuster/
├── Screenshots/           # Application screenshots
├── venv/                 # Virtual environment (auto-generated)
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT License
├── main.py             # Application entry point
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── volume_control_config.json  # Configuration file
└── volume_control.log  # Application logs
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

### Configuration
The project uses JSON configuration files:
- `volume_control_config.json` - Contains user settings and calibration data

Default configuration:
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

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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