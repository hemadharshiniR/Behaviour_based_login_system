// =======================================
// BEHAVIOR TRACKING SYSTEM
// =======================================


// =======================================
// KEYSTROKE DYNAMICS TRACKING
// =======================================

// Store keydown timestamps (unique per event)
let keyDownTimestamps = [];

// Track last key release time
let lastKeyUpTime = null;

// Required array
let typingSpeed = [];  // Stores hold duration per key

// Detailed arrays
let keyHoldTimes = [];
let keyDelayTimes = [];

let firstKeyTime = null;
let lastKeyTime = null;

document.addEventListener("DOMContentLoaded", function () {

    const inputs = document.querySelectorAll(
        "input[type='text'], input[type='password']"
    );

    inputs.forEach(input => {

        input.addEventListener("keydown", function (event) {

            let currentTime = performance.now();

            if (!firstKeyTime) {
                firstKeyTime = currentTime;
            }

            keyDownTimestamps.push({
                key: event.key,
                time: currentTime
            });

        });

        input.addEventListener("keyup", function (event) {

            let currentTime = performance.now();

            // Find matching keydown (latest one)
            for (let i = keyDownTimestamps.length - 1; i >= 0; i--) {
                if (keyDownTimestamps[i].key === event.key) {

                    let holdDuration =
                        currentTime - keyDownTimestamps[i].time;

                    keyHoldTimes.push(holdDuration);
                    typingSpeed.push(holdDuration);

                    keyDownTimestamps.splice(i, 1);
                    break;
                }
            }

            // Calculate delay between keys
            if (lastKeyUpTime !== null) {
                let delay = currentTime - lastKeyUpTime;
                keyDelayTimes.push(delay);
            }

            lastKeyUpTime = currentTime;
            lastKeyTime = currentTime;
        });

    });

});


// =======================================
// GET KEYSTROKE SUMMARY
// =======================================

function getKeystrokeData() {

    let avgHold =
        keyHoldTimes.length > 0
            ? keyHoldTimes.reduce((a, b) => a + b) / keyHoldTimes.length
            : 0;

    let avgDelay =
        keyDelayTimes.length > 0
            ? keyDelayTimes.reduce((a, b) => a + b) / keyDelayTimes.length
            : 0;

    let totalTypingTime =
        typingSpeed.reduce((a, b) => a + b, 0);

    let typingDuration =
        firstKeyTime && lastKeyTime
            ? (lastKeyTime - firstKeyTime) / 1000
            : 0;

    let typingRate =
        typingDuration > 0
            ? typingSpeed.length / typingDuration
            : 0;

    return {
        average_hold_time: avgHold.toFixed(2),
        average_delay_between_keys: avgDelay.toFixed(2),
        total_typing_time: totalTypingTime.toFixed(2),
        total_keys_pressed: typingSpeed.length,
        typing_speed_keys_per_sec: typingRate.toFixed(2)
    };
}



// =======================================
// MOUSE BEHAVIOR TRACKING
// =======================================

let mouseMovements = [];
let lastMouseTime = null;
let lastMousePosition = null;

let totalDistance = 0;
let clickCount = 0;
let movementEvents = 0;

document.addEventListener("mousemove", function (event) {

    let currentTime = performance.now();
    let currentPosition = {
        x: event.clientX,
        y: event.clientY
    };

    if (lastMousePosition && lastMouseTime) {

        let dx = currentPosition.x - lastMousePosition.x;
        let dy = currentPosition.y - lastMousePosition.y;

        let distance = Math.sqrt(dx * dx + dy * dy);
        totalDistance += distance;

        let timeDiff = currentTime - lastMouseTime;

        if (timeDiff > 0) {
            let speed = distance / timeDiff; // px/ms
            mouseMovements.push(speed);
        }

        movementEvents++;
    }

    lastMousePosition = currentPosition;
    lastMouseTime = currentTime;
});


// Track clicks
document.addEventListener("click", function () {
    clickCount++;
});


// =======================================
// GET MOUSE SUMMARY
// =======================================

function getMouseData() {

    let avgSpeed =
        mouseMovements.length > 0
            ? mouseMovements.reduce((a, b) => a + b) / mouseMovements.length
            : 0;

    return {
        total_mouse_distance: totalDistance.toFixed(2),
        average_mouse_speed: avgSpeed.toFixed(4),
        total_clicks: clickCount,
        movement_events: movementEvents
    };
}
