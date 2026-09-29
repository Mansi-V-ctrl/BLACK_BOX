document.addEventListener("DOMContentLoaded", function () {

    /* ==========================================
       FLASH MESSAGE AUTO CLOSE
    ========================================== */

    const flashMessages =
        document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transform = "translateY(-8px)";
            message.style.transition = "0.35s ease";

            setTimeout(function () {
                message.remove();
            }, 350);

        }, 3500);

    });


    /* ==========================================
       PASSWORD SHOW / HIDE
    ========================================== */

    const toggles =
        document.querySelectorAll(".password-toggle");

    toggles.forEach(function (toggle) {

        toggle.addEventListener("click", function () {

            const targetId =
                toggle.getAttribute("data-target");

            const input =
                document.getElementById(targetId);

            if (!input) return;


            if (input.type === "password") {

                input.type = "text";

                toggle.textContent = "HIDE";

            } else {

                input.type = "password";

                toggle.textContent = "SHOW";

            }

        });

    });


    /* ==========================================
       BUTTON LOADING
       Only applies to demo transaction button
    ========================================== */

    const paymentForm =
        document.getElementById("paymentForm");

    const runButton =
        document.getElementById("runButton");

    if (paymentForm && runButton) {

        paymentForm.addEventListener("submit", function () {

            runButton.classList.add("loading");

            const title =
                runButton.querySelector("strong");

            const subtitle =
                runButton.querySelector("small");

            if (title) {
                title.textContent = "RUNNING...";
            }

            if (subtitle) {
                subtitle.textContent =
                    "Capturing application events";
            }

        });

    }


    /* ==========================================
       NUMBER INPUT
    ========================================== */

    const numberInputs =
        document.querySelectorAll('input[type="number"]');

    numberInputs.forEach(function (input) {

        input.addEventListener("input", function () {

            if (Number(input.value) < 1) {
                input.value = 1;
            }

        });

    });

});