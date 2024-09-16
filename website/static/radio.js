var wsprefix = (window.location.protocol == "https:") ? "wss://" : "ws://";
var ws = new WebSocket(wsprefix + window.location.host + "/ws/radio/");
const audio = document.getElementById("audio");
const volslider = document.getElementById("volslider");
volslider.value = 50;
audio.volume = 0.5;
const playstop = document.getElementById("playstop");
const rc = document.getElementById("radiocanvas");
const rcx = rc.getContext("2d");
var mediaSource = new MediaSource();
var queue = [];
var sourceBuffer = null;
var isFirstBlock = true;
var waves = [];
waves.push({ "height": 50, "color": "#fff" });
var stopped = true;

ws.onopen = () => {
    // console.log("websocket opened")
}

// code adapted from: https://github.com/SamuelFisher/WebSocketAudio
function appendBlock() {
    if (sourceBuffer.updating) return;
    if (queue.length == 0) return;

    if (queue.length == 0 &&
        audio.currentTime > 2 &&
        audio.currentTime > this.sourceBuffer.buffered.start(0) + 5) {
        sourceBuffer.remove(0, this.audio.currentTime - 1);
        return;
    }

    // Determine next append time
    // var appendTime = 0;
    // if (!this.isFirstBlock) {
    //     appendTime = this.sourceBuffer.buffered.end(0);
    // }
    this.isFirstBlock = false;

    // Append audio segment
    // sourceBuffer.timestampOffset = appendTime;
    sourceBuffer.appendBuffer(this.queue.shift());

    // Print stats
    // console.log("current time: " + audio.currentTime + " buffered time: " + appendTime)
}

mediaSource.addEventListener("sourceopen", function () {
    sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");
    sourceBuffer.addEventListener("updateend", function (_) {
        appendBlock();
    });
    ws.onmessage = (e) => {
        if (audio.error != null) {
            window.location.reload();
            waves.push({ "height": waves[waves.length - 1].height, "color": "#d00" });
        }

        var reader = new FileReader();
        reader.addEventListener("loadend", () => {
            queue.push(reader.result);
            appendBlock();
            if (!stopped)
                waves.push({ "height": waves[waves.length - 1].height, "color": "#0d0" });
        });
        reader.readAsArrayBuffer(e.data);
    }
});

audio.src = URL.createObjectURL(mediaSource);

if (!audio.paused || audio.currentTime)
    playstop.innerHTML = "⏹︎";
playstop.onclick = () => {
    if (playstop.innerHTML == "⏵︎") {
        audio.play();
        audio.currentTime = 1e101; // hack to jump to end of stream
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
    if (!stopped)
        waves.push({ "height": bounded, "color": "#fff" });
}, 250);

volslider.oninput = (e) => {
    audio.volume = e.target.value / 100;
}