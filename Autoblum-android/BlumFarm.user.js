// ==UserScript==
// @name         Auto-Blum-mizegerddev
// @version      1.1
// @match        https://telegram.blum.codes/*
// @grant        none
// ==/UserScript==

// Watermark: https://t.me/mizegerddev & https://github.com/mizegerd-tech

// Game settings configuration
let GAME_SETTINGS = {
    BombHits: Math.floor(Math.random() * 2), // Random bomb hits between 0 and 1
    IceHits: Math.floor(Math.random() * 2) + 2, // Random ice hits between 2 and 3
    flowerSkipPercentage: Math.floor(Math.random() * 11) + 15, // Random skip percentage between 15 and 25
    minDelayMs: 2000, // Minimum delay in milliseconds
    maxDelayMs: 5000, // Maximum delay in milliseconds
};

// Game state flags
let isGamePaused = true;
let isSettingsOpen = false;

try {
    console.log('Script started');

    // Initialize game statistics
    let gameStats = {
        score: 0,
        bombHits: 0,
        iceHits: 0,
        flowersSkipped: 0,
        isGameOver: false,
    };

    // Override Array.prototype.push to handle game elements
    const originalPush = Array.prototype.push;
    Array.prototype.push = function (...items) {
        if (!isGamePaused) {
            items.forEach(item => handleGameElement(item));
        }
        return originalPush.apply(this, items);
    };

    // Handle different types of game elements
    function handleGameElement(element) {
        if (!element || !element.item) return;

        const { type } = element.item;
        switch (type) {
            case "CLOVER":
                processFlower(element);
                break;
            case "BOMB":
                processBomb(element);
                break;
            case "FREEZE":
                processIce(element);
                break;
        }
    }

    // Process flower elements
    function processFlower(element) {
        const shouldSkip = Math.random() < (GAME_SETTINGS.flowerSkipPercentage / 100);
        if (shouldSkip) {
            gameStats.flowersSkipped++;
        } else {
            gameStats.score++;
            clickElement(element);
        }
    }

    // Process bomb elements
    function processBomb(element) {
        if (gameStats.bombHits < GAME_SETTINGS.BombHits) {
            gameStats.score = 0;
            clickElement(element);
            gameStats.bombHits++;
        }
    }

    // Process ice elements
    function processIce(element) {
        if (gameStats.iceHits < GAME_SETTINGS.IceHits) {
            clickElement(element);
            gameStats.iceHits++;
        }
    }

    // Simulate a click on the game element
    function clickElement(element) {
        element.onClick(element);
        element.isExplosion = true;
        element.addedAt = performance.now();
    }

    // Check if the game is completed
    function checkGameCompletion() {
        const rewardElement = document.querySelector('#app > div > div > div.content > div.reward');
        if (rewardElement && !gameStats.isGameOver) {
            gameStats.isGameOver = true;
            logGameStats();
            resetGameStats();
            if (window.__NUXT__.state.$s$0olocQZxou.playPasses > 0) {
                startNewGame();
            }
        }
    }

    // Log game statistics
    function logGameStats() {
        console.log(`Game Over. Stats: Score: ${gameStats.score}, Bombs: ${gameStats.bombHits}, Ice: ${gameStats.iceHits}, Flowers Skipped: ${gameStats.flowersSkipped}`);
    }

    // Reset game statistics
    function resetGameStats() {
        gameStats = {
            score: 0,
            bombHits: 0,
            iceHits: 0,
            flowersSkipped: 0,
            isGameOver: false,
        };
    }

    // Get a random delay within the specified range
    function getRandomDelay() {
        return Math.random() * (GAME_SETTINGS.maxDelayMs - GAME_SETTINGS.minDelayMs) + GAME_SETTINGS.minDelayMs;
    }

    // Start a new game after a delay
    function startNewGame() {
        setTimeout(() => {
            const newGameButton = document.querySelector("#app > div > div > div.buttons > button:nth-child(2)");
            if (newGameButton) {
                newGameButton.click();
            }
            gameStats.isGameOver = false;
        }, getRandomDelay());
    }

    // Observe mutations in the DOM to check for game completion
    const observer = new MutationObserver(mutations => {
        for (const mutation of mutations) {
            if (mutation.type === 'childList') {
                checkGameCompletion();
            }
        }
    });

    // Start observing the app element
    const appElement = document.querySelector('#app');
    if (appElement) {
        observer.observe(appElement, { childList: true, subtree: true });
    }

    // Create controls container
    const controlsContainer = document.createElement('div');
    controlsContainer.style.position = 'fixed';
    controlsContainer.style.top = '10%';
    controlsContainer.style.left = '25%';
    controlsContainer.style.backgroundColor = 'black';
    controlsContainer.style.transform = 'translateX(-50%)';
    controlsContainer.style.zIndex = '9999';
    controlsContainer.style.padding = '10px 20px';
    controlsContainer.style.borderRadius = '10px';
    document.body.appendChild(controlsContainer);

    // Add channel link
    const OutGamePausedTrue = document.createElement('a');
    OutGamePausedTrue.textContent = 'کانال ما: @mizegerddev';
    OutGamePausedTrue.style.color = 'white';
    controlsContainer.appendChild(OutGamePausedTrue);

    const lineBreak = document.createElement('br');
    controlsContainer.appendChild(lineBreak);

    // Create pause button
    const pauseButton = document.createElement('button');
    pauseButton.textContent = '▶';
    pauseButton.style.padding = '4px 8px';
    pauseButton.style.backgroundColor = '#5d2a8f';
    pauseButton.style.color = 'white';
    pauseButton.style.border = 'none';
    pauseButton.style.borderRadius = '10px';
    pauseButton.style.cursor = 'pointer';
    pauseButton.style.marginRight = '5px';
    pauseButton.onclick = toggleGamePause;
    controlsContainer.appendChild(pauseButton);

    // Create settings button
    const settingsButton = document.createElement('button');
    settingsButton.textContent = 'تنظیمات ربات';
    settingsButton.style.padding = '4px 8px';
    settingsButton.style.backgroundColor = '#5d2a8f';
    settingsButton.style.color = 'white';
    settingsButton.style.border = 'none';
    settingsButton.style.borderRadius = '10px';
    settingsButton.style.cursor = 'pointer';
    settingsButton.onclick = toggleSettings;
    controlsContainer.appendChild(settingsButton);

    // Create settings container
    const settingsContainer = document.createElement('div');
    settingsContainer.style.display = 'none';
    settingsContainer.style.marginTop = '10px';
    controlsContainer.appendChild(settingsContainer);

    // Create input for game settings
    function createSettingInput(label, settingName, min, max) {
        const settingDiv = document.createElement('div');
        settingDiv.style.marginBottom = '5px';
        settingDiv.style.color = 'white';

        const labelElement = document.createElement('label');
        labelElement.textContent = label;
        labelElement.style.display = 'block';
        labelElement.style.color = 'white';
        settingDiv.appendChild(labelElement);

        const inputElement = document.createElement('input');
        inputElement.type = 'number';
        inputElement.value = GAME_SETTINGS[settingName];
        inputElement.min = min;
        inputElement.max = max;
        inputElement.style.width = '50px';
        inputElement.addEventListener('input', () => {
            GAME_SETTINGS[settingName] = parseInt(inputElement.value, 10);
        });
        settingDiv.appendChild(inputElement);

        return settingDiv;
    }

    // Toggle settings visibility
    function toggleSettings() {
        isSettingsOpen = !isSettingsOpen;
        if (isSettingsOpen) {
            settingsContainer.style.display = 'block';
            settingsContainer.innerHTML = '';
            settingsContainer.appendChild(createSettingInput('بمب', 'BombHits', 0, 10));
            settingsContainer.appendChild(createSettingInput('یخ', 'IceHits', 0, 10));
            settingsContainer.appendChild(createSettingInput('درصد نادیده گرفتن', 'flowerSkipPercentage', 0, 100));
        } else {
            settingsContainer.style.display = 'none';
        }
    }

    // Toggle game pause state
    function toggleGamePause() {
        isGamePaused = !isGamePaused;
        pauseButton.textContent = isGamePaused ? '▶' : '❚❚';
    }

} catch (e) {
    console.log('Failed to initiate the game script');
}

// Watermark: https://t.me/mizegerddev & https://github.com/mizegerd-tech