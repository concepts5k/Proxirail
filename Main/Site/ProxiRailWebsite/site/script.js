document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("page-loaded");

    const welcomeSection =
        document.querySelector("#welcome");

    const petWayButton =
        document.querySelector("#petWayButton");

    const petWaySection =
        document.querySelector("#pet-way");

    const railroadButtons =
        document.querySelectorAll(".railroad-option");

    const railroadDisplay =
        document.querySelector("#railroadDisplay");

    const selectedRailId =
        document.querySelector("#selectedRailId");

    let transitionIsRunning = false;

    /*
        Welcome-to-PET-Way sequence:

        1. Fade the welcome information
        2. Bring in the train
        3. Fade in the pedestrian
        4. Slow and stop the train
        5. Pause
        6. Scroll to PET Way
    */

    if (
        welcomeSection &&
        petWayButton &&
        petWaySection
    ) {
        petWayButton.addEventListener("click", () => {
            if (transitionIsRunning) {
                return;
            }

            transitionIsRunning = true;

            const reducedMotion =
                window.matchMedia(
                    "(prefers-reduced-motion: reduce)"
                ).matches;

            if (reducedMotion) {
                petWaySection.scrollIntoView({
                    behavior: "auto",
                    block: "start"
                });

                transitionIsRunning = false;
                return;
            }

            welcomeSection.classList.add("is-departing");

            /*
                The train stops after 4.2 seconds.
                This adds a 750-millisecond pause.
            */

            window.setTimeout(() => {
                petWaySection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }, 4950);

            /*
                Reset the scene after scrolling so it can
                play again if the visitor returns to the top.
            */

            window.setTimeout(() => {
                welcomeSection.classList.remove("is-departing");
                transitionIsRunning = false;
            }, 6500);
        });
    }

    /*
        Railroad ID buttons
    */

    railroadButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const railId = button.dataset.railId;

            railroadButtons.forEach((otherButton) => {
                otherButton.classList.remove("selected");
            });

            button.classList.add("selected");

            if (selectedRailId) {
                selectedRailId.textContent = railId;
            }

            if (railroadDisplay) {
                railroadDisplay.hidden = false;

                window.setTimeout(() => {
                    railroadDisplay.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }, 100);
            }
        });
    });
});