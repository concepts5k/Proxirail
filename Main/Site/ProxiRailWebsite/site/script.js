document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("page-loaded");

    const welcomeSection =
        document.querySelector("#welcome");

    const petWaySection =
        document.querySelector("#pet-way");

    const railroadButtons =
        document.querySelectorAll(".railroad-option");

    const railroadDisplay =
        document.querySelector("#railroadDisplay");

    const selectedRailId =
        document.querySelector("#selectedRailId");

    const reducedMotion =
        window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        ).matches;

    /*
        Updated automatic sequence:

        1. Welcome text appears
        2. Train starts after 1.2 seconds
        3. Train slows and stops
        4. Page scrolls to PET Way
    */

    const introDelay = 1200;
    const trainAnimationTime = 3200;
    const pauseAfterTrain = 800;

    if (welcomeSection && petWaySection) {
        if (reducedMotion) {
            window.setTimeout(() => {
                petWaySection.scrollIntoView({
                    behavior: "auto",
                    block: "start"
                });
            }, 2500);
        } else {
            window.setTimeout(() => {
                welcomeSection.classList.add(
                    "auto-sequence"
                );
            }, introDelay);

            window.setTimeout(() => {
                petWaySection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            },
            introDelay +
            trainAnimationTime +
            pauseAfterTrain);
        }
    }

    /*
        Railroad ID selection
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
