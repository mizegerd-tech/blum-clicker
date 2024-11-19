

# 🌸 Blum Clicker (Android & Windows Versions)

**Blum Clicker** is an advanced automation tool designed to enhance your experience with the **Blum Telegram Bot**. This tool supports both **Android** and **Windows** platforms, enabling automated interactions like clicking bombs, ice, and flowers in the game. Customizable settings allow you to fine-tune the bot for optimal gameplay.


![banner](https://github.com/user-attachments/assets/19b2e792-e3e9-470d-b977-1e9bad6543ed)

---

## 📱 Android Version

The **Android** version of **blum Clicker** uses the **Misee Browser** and custom scripts to interact with the Blum bot.

### Installation Guide

1. **Install Misee Browser**  
   Download and install the Misee Browser from the [Google Play Store](https://play.google.com/store/apps/details?id=site.mises.browser).

2. **Install Required Extensions**  
   Install the following extensions in the browser:
   - **Ignore X-Frame Headers**: Allows iframing of all pages.
     [Extension Link](https://chrome.google.com/webstore/detail/ignore-x-frame-headers)
   - **Violentmonkey**: Add scripts for automation.
     [Extension Link](https://chrome.google.com/webstore/detail/violentmonkey/jinjaccalgkegednnccohejagnlnfdag)

3. **Add Script and Set Up Telegram**  
   - Add the provided **Auto-Blum-mizegerddev** script to the **Violentmonkey** extension.
   - Launch Telegram within the **Misee Browser** and open the **Blum Bot**.

4. **Script Settings**  
   - Set **Bomb Hits** between 0 to 10.
   - Set **Ice Hits** between 0 to 10.
   - Set **Skip Percentage** between 0% to 100%.

### Key Features (Android)
- **Auto-click for Game Elements**: Automates the clicking of flowers, bombs, and ice.
- **Customizable Settings**: Easily adjust the script for bomb and ice hits and flower skip percentage.
- **Runs Directly in Browser**: Uses Misee Browser with extensions to seamlessly interact with the bot.

---

## 💻 Windows Version

The **Windows** version automates interactions with the **Blum Telegram Bot** using a combination of color detection and automated clicking.

### Requirements
- **Python 3.7+**
- Install the required libraries by running:
   ```bash
   pip install numpy opencv-python pygetwindow pywinauto pyfiglet keyboard mss
   ```

### Installation Guide

1. **Clone the Repository**
   Clone or download the project and navigate to the folder in a terminal.

   ```bash
   git clone https://github.com/mizegerd-tech/blum-clicker.git
   cd YourProject
   ```

2. **Run the Script**
   Start the script by running:
   ```bash
   python blum_clicker_windows.py
   ```

3. **Select Blum Window**
   The script will display a list of active windows with **Blum** or **Telegram** in the title. Select the correct window where the bot is running.

4. **Configure Settings**
   - **Target Percentage**: Enter a number between **0.01 and 1** to reduce game errors.
   - **Ice Click**: Choose whether the script should automatically click on ice:
     - `1`: Yes
     - `2`: No

5. **Activate the Script**
   Press **F6** to start or pause the clicker.

### Key Features (Windows)
- **Automated Interaction**: Automatically clicks bombs, ice, and flowers based on real-time detection.
- **Customizable Settings**: Define target click percentage, ice collection, and detection sensitivity.
- **Hotkey Control**: Use **F6** to toggle the script's operation.

---

## 🎮 Game Settings for Both Versions

- **Bomb Hits**: Automatically set between 0 and 10 (customizable).
- **Ice Hits**: Automatically set between 0 and 10 (customizable).
- **Skip Flower Percentage**: Randomly set between 15% and 25% (customizable).
- **Random Delays**: Random delay for clicks between 2 to 5 seconds to mimic natural interaction.

---

## 🚀 Additional Information

- **Telegram Support**:  
   If you encounter any issues, feel free to [contact us on Telegram](https://t.me/mizegerd_dev).
   
- **Join Our Channel**:  
   For the latest updates and features, join our [Telegram Channel](https://t.me/mizegerddev).
