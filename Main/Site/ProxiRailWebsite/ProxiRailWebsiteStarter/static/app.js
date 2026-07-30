
const searchInput = document.querySelector("#searchInput");
const sortSelect = document.querySelector("#sortSelect");
const grid = document.querySelector("#intersectionGrid");
const emptyState = document.querySelector("#emptyState");
const presentationButton = document.querySelector("#presentationModeButton");

function updateCards() {
    if (!grid || !searchInput || !sortSelect) {
        return;
    }

    const query = searchInput.value.trim().toLowerCase();
    const sortMode = sortSelect.value;
    const cards = Array.from(grid.querySelectorAll(".intersection-card"));

    cards.forEach((card) => {
        card.hidden = !card.dataset.name.includes(query);
    });

    const visibleCards = cards.filter((card) => !card.hidden);

    visibleCards.sort((a, b) => {
        if (sortMode === "distance") {
            return Number(a.dataset.distance) - Number(b.dataset.distance);
        }

        if (sortMode === "name") {
            return a.dataset.name.localeCompare(b.dataset.name);
        }

        return Number(b.dataset.riskRank) - Number(a.dataset.riskRank);
    });

    visibleCards.forEach((card) => grid.appendChild(card));
    if (emptyState) {
        emptyState.hidden = visibleCards.length !== 0;
    }
}

if (searchInput && sortSelect) {
    searchInput.addEventListener("input", updateCards);
    sortSelect.addEventListener("change", updateCards);
    updateCards();
}

function drawMockChart(chart) {
    let values;

    try {
        values = JSON.parse(chart.dataset.points);
    } catch {
        return;
    }

    if (!Array.isArray(values) || values.length < 2) {
        return;
    }

    const polyline = chart.querySelector(".trend-line");
    const pointsGroup = chart.querySelector(".trend-points");

    if (!polyline || !pointsGroup) {
        return;
    }

    const width = 700;
    const height = 250;
    const padding = 24;
    const maxValue = Math.max(...values, 7);
    const minValue = 0;

    const points = values.map((value, index) => {
        const x = padding + (index / (values.length - 1)) * (width - padding * 2);
        const normalized = (value - minValue) / (maxValue - minValue);
        const y = height - padding - normalized * (height - padding * 2);
        return { x, y, value };
    });

    polyline.setAttribute(
        "points",
        points.map((point) => `${point.x},${point.y}`).join(" ")
    );

    pointsGroup.replaceChildren();

    points.forEach((point) => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", point.x);
        circle.setAttribute("cy", point.y);
        circle.setAttribute("r", "6");
        circle.setAttribute("class", "trend-point");

        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        title.textContent = `${point.value.toFixed(1)} seconds PET`;
        circle.appendChild(title);
        pointsGroup.appendChild(circle);
    });
}

document.querySelectorAll(".mock-chart").forEach(drawMockChart);

if (presentationButton) {
    presentationButton.addEventListener("click", () => {
        const enabled = document.body.classList.toggle("presentation-mode");
        presentationButton.textContent = enabled
            ? "Exit presentation"
            : "Presentation mode";
    });
}

/* Smooth navigation between the Welcome page and the separate demo page. */
function fadeNavigate(url) {
    if (!url) {
        return;
    }

    document.body.classList.add("page-fade-out");

    window.setTimeout(() => {
        window.location.href = url;
    }, 750);
}

document.querySelectorAll("[data-transition-url]").forEach((element) => {
    element.addEventListener("click", (event) => {
        event.preventDefault();
        fadeNavigate(element.dataset.transitionUrl);
    });
});

/* Separate crossing demonstration. */
const crossingScene = document.getElementById("crossingScene");
const crossingTrain = document.getElementById("crossingTrain");
const frontPerson = document.getElementById("frontPerson");
const cameraBeam = document.getElementById("cameraBeam");
const crossingAlert = document.getElementById("crossingAlert");
const holdCrossingTrainButton = document.getElementById("holdCrossingTrainButton");
const resetCrossingDemoButton = document.getElementById("resetCrossingDemoButton");
const crossingTrainStatus = document.getElementById("crossingTrainStatus");
const crossingCameraStatus = document.getElementById("crossingCameraStatus");
const crossingPersonStatus = document.getElementById("crossingPersonStatus");
const crossingInstruction = document.getElementById("crossingInstruction");

let crossingProgress = 0;
let crossingHoldTimer = null;
let crossingHolding = false;
let returnTimer = null;

function setCrossingStatus(train, camera, person, instruction) {
    if (crossingTrainStatus) crossingTrainStatus.textContent = train;
    if (crossingCameraStatus) crossingCameraStatus.textContent = camera;
    if (crossingPersonStatus) crossingPersonStatus.textContent = person;
    if (crossingInstruction) crossingInstruction.textContent = instruction;
}

function renderCrossingScene() {
    if (!crossingTrain || !crossingScene) {
        return;
    }

    const travel = crossingProgress * 1.55;
    const scale = 0.58 + crossingProgress * 0.0062;

    crossingTrain.style.transform =
        `translate(-50%, ${travel}px) scale(${scale})`;

    if (frontPerson) {
        const walkingOffset = Math.sin(crossingProgress / 8) * 4;
        frontPerson.style.transform =
            `translateX(${walkingOffset}px)`;
    }

    if (crossingProgress < 34) {
        crossingScene.classList.add("camera-active");
        crossingScene.classList.remove("warning-stage", "critical-stage");

        setCrossingStatus(
            "Logo approaching",
            "Camera tracking the crossing zone",
            "Front-facing pedestrian visible",
            "Continue holding to move the train logo toward the crossing."
        );
        return;
    }

    if (crossingProgress < 70) {
        crossingScene.classList.add("camera-active", "warning-stage");
        crossingScene.classList.remove("critical-stage");

        setCrossingStatus(
            "Logo near the crossing",
            "Pedestrian and train activity detected",
            "Pedestrian remains in the monitored zone",
            "The prototype now shows a warning condition."
        );
        return;
    }

    crossingScene.classList.add(
        "camera-active",
        "warning-stage",
        "critical-stage"
    );

    setCrossingStatus(
        "Demonstration complete",
        "Camera maintained visual awareness",
        "Pedestrian remained visible from the front",
        "Returning to the Welcome title in a moment..."
    );
}

function stopCrossingHold() {
    crossingHolding = false;

    if (holdCrossingTrainButton) {
        holdCrossingTrainButton.classList.remove("active");
        holdCrossingTrainButton.textContent = "Hold to move the train logo";
    }

    if (crossingHoldTimer) {
        window.clearInterval(crossingHoldTimer);
        crossingHoldTimer = null;
    }
}

function completeCrossingDemo() {
    stopCrossingHold();

    if (returnTimer) {
        window.clearTimeout(returnTimer);
    }

    returnTimer = window.setTimeout(() => {
        fadeNavigate("/#welcome");
    }, 2400);
}

function startCrossingHold(event) {
    if (event) {
        event.preventDefault();
    }

    if (
        !holdCrossingTrainButton ||
        crossingHolding ||
        crossingProgress >= 82
    ) {
        return;
    }

    crossingHolding = true;
    holdCrossingTrainButton.classList.add("active");
    holdCrossingTrainButton.textContent = "Holding — logo moving";

    crossingHoldTimer = window.setInterval(() => {
        crossingProgress = Math.min(82, crossingProgress + 1.4);
        renderCrossingScene();

        if (crossingProgress >= 82) {
            completeCrossingDemo();
        }
    }, 55);
}

function resetCrossingDemo() {
    if (returnTimer) {
        window.clearTimeout(returnTimer);
        returnTimer = null;
    }

    stopCrossingHold();
    crossingProgress = 0;

    if (crossingTrain) {
        crossingTrain.style.transform =
            "translate(-50%, 0) scale(0.58)";
    }

    if (frontPerson) {
        frontPerson.style.transform = "translateX(0)";
    }

    if (crossingScene) {
        crossingScene.classList.remove(
            "camera-active",
            "warning-stage",
            "critical-stage"
        );
    }

    setCrossingStatus(
        "Waiting",
        "Monitoring the crossing",
        "Front view detected",
        "Hold the yellow button. When the demonstration reaches its final stage, the page will fade and return to the Welcome title."
    );
}

if (holdCrossingTrainButton) {
    ["mousedown", "touchstart", "pointerdown"].forEach((eventName) => {
        holdCrossingTrainButton.addEventListener(eventName, startCrossingHold);
    });

    ["mouseup", "mouseleave", "touchend", "touchcancel", "pointerup", "pointercancel"].forEach((eventName) => {
        holdCrossingTrainButton.addEventListener(eventName, stopCrossingHold);
    });
}

if (resetCrossingDemoButton) {
    resetCrossingDemoButton.addEventListener("click", resetCrossingDemo);
}

if (crossingScene) {
    resetCrossingDemo();
}
