const audio = document.getElementById("audio");
const volslider = document.getElementById("volslider");
volslider.value = 50;
audio.volume = 0.5;
const playstop = document.getElementById("playstop");
const rc = document.getElementById("radiocanvas");
const rcx = rc.getContext("2d");
var waves = [];
waves.push({ "height": 50, "color": "#fff" });
var stopped = true;

function setsource() {
    if (window.location.hostname == "localhost") {
        audio.src = "http://localhost:8003/";
    } else {
        audio.src = window.location.host + "/radio";
    }
}

playstop.onclick = () => {
    if (playstop.innerHTML == "⏵︎") {
        setsource(); // hack to jump to end of stream
        audio.play();
        playstop.innerHTML = "⏹︎";
        stopped = false;
    } else if (playstop.innerHTML == "⏹︎") {
        audio.pause();
        playstop.innerHTML = "⏵︎";
        stopped = true;
    }
}

rcx.fillStyle = "#000";
rcx.fillRect(0, 0, rc.width, rc.height);

function randint(min, max) {
    const minCeiled = Math.ceil(min);
    const maxFloored = Math.floor(max);
    return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled);
}

var waveinterval = setInterval(function () {
    rcx.fillStyle = "#000";
    rcx.fillRect(0, 0, rc.width, rc.height);

    for (var i = 0; i < 150; i++) {
        var wi = (waves.length - 1) - i;
        if (wi < 0) continue;
        if (rc.width - (i * 5) + 2 < 0) {
            waves.shift();
            continue;
        }

        rcx.strokeStyle = waves[wi].color;
        rcx.beginPath();
        rcx.moveTo(rc.width - (i * 5) + 2, rc.height - 10);
        rcx.lineTo(rc.width - (i * 5) + 2, rc.height - 10 - waves[wi].height);
        rcx.stroke();
    }

    var newheight = waves[waves.length - 1].height + randint(-10, 12);
    var bounded = Math.max(Math.min(100, newheight), 5);
    if (!stopped && (!audio.paused || audio.currentTime))
        waves.push({ "height": bounded, "color": "#fff" });
}, 250);

volslider.oninput = (e) => {
    audio.volume = e.target.value / 100;
}