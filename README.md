<h4 align="center"> If you find this GitHub repo useful, please consider giving it a star! ⭐️ </h4> 
<p align="center">
    <a href="https://spyboy.in/twitter">
      <img src="https://img.shields.io/badge/-TWITTER-black?logo=twitter&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.in/">
      <img src="https://img.shields.io/badge/-spyboy.in-black?logo=google&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.blog/">
      <img src="https://img.shields.io/badge/-spyboy.blog-black?logo=wordpress&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.in/Discord">
      <img src="https://img.shields.io/badge/-Discord-black?logo=discord&style=for-the-badge">
    </a>
  
</p>

<p align="center">
  <img width="20%" src="https://github.com/spyboy-productions/CamXploit/blob/main/CCTV recon.jpg" />
</p>



CamXploit is a reconnaissance tool designed to help researchers and security enthusiasts check if an IP address is hosting an exposed CCTV camera. It scans common camera ports, checks for login pages, tests default credentials, and provides useful search links for further investigation.  

⚠️ **Disclaimer:** This tool is intended for educational and security research purposes **only**. Unauthorized scanning of systems you do not own is illegal. Use responsibly.  

### ☁️ Run It Instantly on Google Colab (No Installation Needed)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/spyboy-productions/CamXploit/blob/main/CamXploit.ipynb)

---

## 🆕 What's New in v2.0.1
- Massive port scan: Now scans 1000+ ports, including custom and high camera ports
- CP Plus (CP-UVR-0401E1-IC2) and DVR/NVR detection
- Enhanced live stream detection (RTSP/HTTP/RTMP/MMS, with real stream validation)
- Multi-threaded authentication and password brute-force (much faster)
- Improved camera indicator analysis (brand, model, login forms, titles)
- Comprehensive IP/location info with Google Maps/Earth links
- Improved error handling and progress reporting

---

## 🚀 **Features**  

✔️ **Scans all common CCTV ports**  
✔️ **Detects exposed camera login pages**  
✔️ **Checks if the device is a camera stream**  
✔️ **Identifies camera brands & known vulnerabilities**  
✔️ **Tests for default credentials on login pages**  
✔️ **Provides manual search links (Shodan, Censys, Zoomeye, Google Dorking)**  
✔️ **Google Dorking suggestions for deeper recon**  
✔️ **Enhanced Camera Detection** with detailed port analysis and brand identification  
✔️ **Live Stream Detection** for RTSP, RTMP, HTTP, and MMS protocols  
✔️ **Comprehensive IP & Location Information** with Google Maps/Earth links  
✔️ **Multi-threaded Port Scanning** for faster results  
✔️ **Enhanced Error Handling** and SSL support  
✔️ **Detailed Camera Brand Detection** (Hikvision, Dahua, Axis, Sony, Bosch, Samsung, Panasonic, Vivotek, CP Plus)  
✔️ **ONVIF Protocol Support** for standardized camera communication  
✔️ **Smart Brute-force Protection** with rate limiting  
✔️ **Detailed Port Analysis** showing server information and authentication types  

---

## 📚 Supported Brands & Devices
- Hikvision, Dahua, Axis, Sony, Bosch, Samsung, Panasonic, Vivotek, CP Plus, and most generic DVR/NVRs
- CP Plus DVRs (e.g., CP-UVR-0401E1-IC2) with custom ports
- Any device exposing RTSP, HTTP, RTMP, or MMS video streams

---

## 🛠️ **Installation**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/spyboy-productions/CamXploit.git
```
```
cd CamXploit
```  
```bash
pip install -r requirements.txt
```
---
```
python CamXploit.py
```
Enter the **public IP address** of the target device when prompted.  

### **🔍 What It Does:**  
1️⃣ **Scans open ports** (Common CCTV ports)  
2️⃣ **Checks if a camera is present**  
3️⃣ If a camera is found, it:  
   - Searches for **login pages**  
   - Checks **default credentials**  
   - Identifies **camera brand & vulnerabilities**  
   - Detects **live streams** (RTSP, RTMP, HTTP, MMS)  
   - Provides **location information** with maps  
   - Shows **server details** and authentication types  
4️⃣ Provides **manual search URLs** for deeper investigation

---

## 📂 Environment Configuration

Create a `.env` file in the project root to tune the web interface. The server reads
this file automatically on startup. Example:

```ini
CAMXPLOIT_PATH=CamXploit.py
FFMPEG_PATH=ffmpeg
MAX_WORKERS=4
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

`CAMXPLOIT_PATH` and `FFMPEG_PATH` let you point to custom binaries. `MAX_WORKERS`
controls how many IPs are scanned concurrently, and the Flask host/port options allow
the service to bind to a different interface.
The `.env` file is ignored by Git so your local configuration stays private.

---

## ⚡ Usage Tips
- Scanning all ports (1000+) may take several minutes, depending on your network and target.
- The tool uses multi-threading for port, login, and password checks for speed.
- If you see "No camera found" but you know a camera is present, check the open ports and look for custom ports in the output.
- For best results, run as administrator/root to avoid local firewall issues.

---

## 📚 Troubleshooting
- If no open ports are found, ensure the target is online and not behind a strict firewall.
- If live streams are not detected, try accessing the URLs manually in VLC or a browser.
- For best detection, ensure your Python version is 3.6+ and all dependencies are installed.

---

## 📸 **Example Output**  

<img width="100%" align="centre" src="https://github.com/spyboy-productions/CamXploit/blob/main/demo.png" />

---


## 🤖 **To-Do & Future Features**  
- [x] Add multi-threaded scanning for speed  
- [x] Expand camera brand detection  
- [ ] Implement logging feature  
- [ ] Add screenshot capture functionality  
- [ ] Implement report generation  
- [ ] Add network range scanning  
- [ ] Implement MAC address lookup  

---
## 🙌 **Contributions**  
Feel free to submit issues, suggestions, or pull requests!  

<h4 align="center"> If you find this GitHub repo useful, please consider giving it a star! ⭐️ </h4> 
