
function pres_mode() {
    let state = 0;

    const state0 = document.getElementById("state0");
    const state1 = document.getElementById("state1");
    const state2 = document.getElementById("state2");
    const state3 = document.getElementById("state3");

    function next_state() {
        state++;
        if (state > 4) {
            state = 4
        }

        apply_state();
    }

    function prev_state() {
        state--;
        if (state < 0) {
            state = 0;
        }

        apply_state();
    }

    function set_state(n) {
        state=n
    }


    function all_visible() {
        state0.style.visibility = "visible";
        state1.style.display = "none";
        state2.style.display = "none";
        state3.style.display = "none";
        document.getElementById("html").classList.add("presentation");
        document.getElementById("online-version").style.display = "none";
    }

    function apply_state() {
        console.log(`applying state ${state}`)

        all_visible();
        switch (state) {
            case 4:
                document.getElementById("html").classList.remove("presentation");
                state3.style.display = "flex";
                state2.style.display = "flex";
                state1.style.display = "flex";
                state0.style.visibility = "hidden";

                document.getElementById("online-version").style.display = "block";
                break;
            case 3:
                state3.style.display = "flex";
                state0.style.visibility = "hidden";
                break;
            case 2:
                state2.style.display = "flex";
                state0.style.visibility = "hidden";
                break;
            case 1:
                state1.style.display = "flex";
                state0.style.visibility = "hidden";
                break;
            case 0: break;
        }
    }

    function pres_mode() {
        return window.location.search.includes("pres");
    }



    if (pres_mode() && !document.getElementById("html").classList.contains("mobile")) {
        document.getElementById("html").classList.add("presentation");

        state = 0;
        apply_state();

        window.addEventListener("keyup", function(e) {
            switch (e.key) {
                case "ArrowRight": next_state(); break;
                case "ArrowLeft": prev_state()1; break;
            }
        })
    } else {
        document.getElementById("html").classList.remove("presentation");
    }
}


document.addEventListener("readystatechange", function () {

    pres_mode();
})
