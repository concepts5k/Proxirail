document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("page-loaded");

    /*
        Prototype measurements.

        Replace the values below with real pipeline output.
        Later, swap this object for a fetch() against a JSON
        file written by measure().

        A railroad with no entry here is treated as "no data
        recorded" rather than silently keeping the previous
        railroad's numbers on screen.
    */

    const railData = {
        "Grade Crossing Sample": {
            minPet: "18.4 seconds",
            avgPet: "18.53 seconds",
            conflicts: "2",
            risk: "Intermediate",
            video: "Figures/viz_web.mp4"
        },

        "Intersection Sample": {
            minPet: "2.32 seconds",
            avgPet: "14.20 seconds",
            conflicts: "11",
            risk: "High",
            video: "Figures/vis.mp4"
        }
    };

    /* --- Elements ------------------------------------------ */

    const welcomeSection = document.querySelector("#welcome");
    const petWaySection = document.querySelector("#pet-way");

    const railroadButtons =
        document.querySelectorAll(".railroad-option");

    const railroadDisplay = document.querySelector("#railroadDisplay");
    const selectedRailId = document.querySelector("#selectedRailId");

    const minPet = document.querySelector("#minPet");
    const avgPet = document.querySelector("#avgPet");
    const conflictCount = document.querySelector("#conflictCount");
    const riskCategory = document.querySelector("#riskCategory");

    const crossingFeed = document.querySelector("#crossingFeed");
    const feedMessage = document.querySelector("#feedMessage");

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    const EM_DASH = "\u2014";

    /*
        Hide decorative images that fail to load, so a missing
        asset shows nothing rather than a broken-image icon.

        An image can finish failing before this script runs, and
        its error event is gone by then. Checking naturalWidth on
        an already-complete image catches those.
    */

    function hideBrokenImage(image) {
        image.style.display = "none";
    }

    document
        .querySelectorAll("[data-optional-image]")
        .forEach((image) => {
            image.addEventListener("error", () => {
                hideBrokenImage(image);
            });

            if (image.complete && image.naturalWidth === 0) {
                hideBrokenImage(image);
            }
        });

    /*
        Automatic welcome sequence:

        1. Welcome text fades in (CSS, on page load)
        2. Page scrolls to PET Way after a short pause
    */

    const welcomeHoldDuration = 2500;

    function goToPetWay(behavior) {
        if (!petWaySection) {
            return;
        }

        petWaySection.scrollIntoView({
            behavior: behavior,
            block: "start"
        });
    }

    if (welcomeSection && petWaySection) {
        window.setTimeout(() => {
            goToPetWay(reducedMotion ? "auto" : "smooth");
        }, welcomeHoldDuration);
    }

    /* --- Crossing feed ------------------------------------- */

    /*
        Show a message instead of a broken player when a
        clip is missing or cannot be decoded.
    */

    function showFeedMessage(text) {
        if (!crossingFeed || !feedMessage) {
            return;
        }

        crossingFeed.pause();
        crossingFeed.removeAttribute("src");
        crossingFeed.load();
        crossingFeed.hidden = true;

        feedMessage.textContent = text;
        feedMessage.hidden = false;
    }

    function playFeed(source) {
        if (!crossingFeed || !feedMessage) {
            return;
        }

        crossingFeed.pause();
        crossingFeed.hidden = false;
        feedMessage.hidden = true;
        crossingFeed.src = source;
        crossingFeed.load();
    }

    if (crossingFeed) {
        crossingFeed.addEventListener("error", () => {
            /*
                Ignore the error fired while clearing the
                source in showFeedMessage().
            */

            if (!crossingFeed.getAttribute("src")) {
                return;
            }

            showFeedMessage(
                "Crossing feed unavailable for this railroad."
            );
        });
    }

    /* --- Railroad ID selection ----------------------------- */

    function clearMetrics() {
        [minPet, avgPet, conflictCount].forEach((element) => {
            if (element) {
                element.textContent = EM_DASH;
            }
        });

        if (riskCategory) {
            riskCategory.textContent = EM_DASH;
            riskCategory.className = "metric-value";
        }
    }

    function showMetrics(data) {
        if (minPet) {
            minPet.textContent = data.minPet;
        }

        if (avgPet) {
            avgPet.textContent = data.avgPet;
        }

        if (conflictCount) {
            conflictCount.textContent = data.conflicts;
        }

        if (riskCategory) {
            riskCategory.textContent = data.risk;

            riskCategory.className =
                "metric-value risk-" + data.risk.toLowerCase();
        }
    }

    railroadButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const railId = button.dataset.railId;

            railroadButtons.forEach((otherButton) => {
                otherButton.classList.remove("selected");
                otherButton.setAttribute("aria-pressed", "false");
            });

            button.classList.add("selected");
            button.setAttribute("aria-pressed", "true");

            if (selectedRailId) {
                selectedRailId.textContent = railId;
            }

            const data = railData[railId];

            if (data) {
                showMetrics(data);
                playFeed(data.video);
            } else {
                /*
                    No measurements for this railroad yet.
                    Clear the panel so stale numbers from the
                    previous selection are not shown.
                */

                clearMetrics();

                showFeedMessage(
                    "No measurements recorded for this railroad yet."
                );
            }

            if (railroadDisplay) {
                railroadDisplay.hidden = false;

                window.setTimeout(() => {
                    railroadDisplay.scrollIntoView({
                        behavior: reducedMotion ? "auto" : "smooth",
                        block: "start"
                    });
                }, 100);
            }
        });
    });
});
