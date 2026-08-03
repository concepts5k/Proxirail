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
        Automatic opening sequence:

        1. Display the title and subheading for 10 seconds
        2. Start the train and pedestrian animation
        3. Wait for the animation to finish
        4. Scroll to the PET Way section
    */

    const readingTime = 10000;
    const trainAnimationTime = 2600;
    const pauseAfterTrain = 600;

    if (welcomeSection && petWaySection) {
        if (reducedMotion) {
            window.setTimeout(() => {
                petWaySection.scrollIntoView({
                    behavior: "auto",
                    block: "start"
                });
            }, readingTime);
        } else {
            /*
                Begin the train animation after
                the visitor has had 10 seconds to read.
            */

            window.setTimeout(() => {
                welcomeSection.classList.add(
                    "auto-sequence"
                );
            }, readingTime);

            /*
                Scroll after the train animation finishes.
            */

            window.setTimeout(() => {
                petWaySection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }, readingTime + trainAnimationTime + pauseAfterTrain);
        }
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
