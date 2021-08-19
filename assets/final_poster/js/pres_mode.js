
function pres_mode() {
    let state = 0;

    const state0 = document.getElementById("state0");
    const state1 = document.getElementById("state1");
    const state2 = document.getElementById("state2");
    const state3 = document.getElementById("state3");
    const state4 = document.getElementById("state4");
    const state5 = document.getElementById("state5");
    const state6 = document.getElementById("state6");
    const state7 = document.getElementById("state7");
    const state8 = document.getElementById("state8");
    const state9 = document.getElementById("state9");

    const last_state = 10

    function next_state() {
        state++;
        if (state > last_state) {
            state = last_state
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
        apply_state();
    }

    function make_visible(elem) {
        elem.classList.add("pres_visible");
    }
    function make_invisible(elem) {
        elem.classList.remove("pres_visible");
    }

    function all_visible() {
        state0.style.visibility = "visible";
        make_invisible(state1);
        make_invisible(state2);
        make_invisible(state3);
        make_invisible(state4);
        make_invisible(state5);
        make_invisible(state6);
        make_invisible(state7);
        make_invisible(state8);
        make_invisible(state9);
        document.getElementById("html").classList.add("presentation");
    }

    function apply_state() {
        console.log(`applying state ${state}`)
        state9.style.display = "block";

        all_visible();
        switch (state) {
            case 10:
                document.getElementById("html").classList.remove("presentation");
                state9.style.display = "none";
                make_invisible(state1);
                make_invisible(state2);
                make_invisible(state3);
                make_invisible(state4);
                make_invisible(state5);
                make_invisible(state6);
                make_invisible(state7);
                make_invisible(state8);
                make_invisible(state9);
                state0.style.visibility = "hidden";
                break;
            case 9:
                make_visible(state9)
                state0.style.visibility = "hidden";
                break;
            case 8:
                make_visible(state8)
                state0.style.visibility = "hidden";
                break;
            case 7:
                make_visible(state7)
                state0.style.visibility = "hidden";
                break;
            case 6:
                make_visible(state6)
                state0.style.visibility = "hidden";
                break;
            case 5:
                make_visible(state5)
                state0.style.visibility = "hidden";
                break;
            case 4:
                make_visible(state4)
                state0.style.visibility = "hidden";
                break;
            case 3:
                make_visible(state3)
                state0.style.visibility = "hidden";
                break;
            case 2:
                make_visible(state2)
                state0.style.visibility = "hidden";
                break;
            case 1:
                make_visible(state1)
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
            if (e.ctrlKey) {
                return;
            }

            switch (e.key) {
                case "ArrowRight": next_state(); break;
                case "ArrowLeft": prev_state(); break;
                case "`": set_state(0); break;
                case "1": set_state(1); break;
                case "2": set_state(2); break;
                case "3": set_state(3); break;
                case "4": set_state(4); break;
                case "5": set_state(5); break;
                case "6": set_state(6); break;
                case "7": set_state(7); break;
                case "8": set_state(8); break;
                case "9": set_state(9); break;
                case "0": set_state(10); break;
            }
        })
    } else {
        document.getElementById("html").classList.remove("presentation");
    }
}


document.addEventListener("readystatechange", function () {

    pres_mode();
})
