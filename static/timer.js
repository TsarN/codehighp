(function() {
    var timers = [];
    function initTimer(timer) {
        var seconds = parseInt(timer.dataset.timer);
        timers.push({
            el: timer,
            seconds: seconds
        });
    }

    function padZero(x) {
        if (x < 10) return '0' + x.toString();
        return x.toString();
    }

    function formatTime(seconds) {
        if (seconds <= 0) return "00:00:00";
        var sec = seconds % 60;
        seconds = Math.floor(seconds / 60);
        var min = seconds % 60;
        seconds = Math.floor(seconds / 60);
        var hour = seconds % 24;
        seconds = Math.floor(seconds / 24);
        var days = seconds;

        s = "";
        if (days >= 1) {
            if (days === 1) {
                s = "1 day ";
            } else {
                s = days.toString() + " days ";
            }
        }
        s += padZero(hour) + ":" + padZero(min) + ":" + padZero(sec);
        return s;
    }

    function updateTimers() {
        for (var i = 0; i < timers.length; ++i) {
            timers[i].seconds--;
            timers[i].el.innerText = formatTime(timers[i].seconds);
        }
    }

    function initTimers() {
        var els = document.getElementsByClassName('timer');
        for (var i = 0; i < els.length; ++i) {
            initTimer(els[i]);
        }
        for (var i = 0; i < timers.length; ++i) {
            timers[i].el.innerText = formatTime(timers[i].seconds);
        }
        setInterval(updateTimers, 1000);
    }

    initTimers();
})();
