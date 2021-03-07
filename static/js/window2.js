$(document).ready(function () {
    let socket = io.connect('/');
    // socket.on('connect', function () {
    //     socket.emit('my event', {data: 'Connected from windows2.html'});
    // });

    socket.on('ppt_or_ppt_upload_signal', function (data) {
        // console.log('Received link: ', data["link"]);
        // $('#responsive-iframe').attr('src', data["link"]);
        // todo: loading in the init screen... iframe onload... specially needed for the ppt as we will be uploading to server
        $('#iframe-container').empty().append("<iframe class=\"responsive-iframe\" id=\"responsive-iframe\" allowFullScreen width=\"100%\" height=\"500px\"\n" +
            "                frameBorder=\"0\"\n" +
            "                src=\"" + data['link'] + "\">").show();
        $('#time_count_div').css('visibility', 'visible');
        $('#initial_box').hide();

    });

    // function click(x, y) {
    //     let ev = new MouseEvent('click', {
    //         'view': window,
    //         'bubbles': true,
    //         'cancelable': true,
    //         'screenX': x,
    //         'screenY': y
    //     });
    //
    //     let el = $('#responsive-iframe').elementFromPoint(x, y);
    //     console.log(el); //print element to console
    //     el.dispatchEvent(ev);
    // }


    // PDF/PPT  navigation signal receive
    socket.on('navigation_signal_receive', function (data) {

        let iframe = $('#responsive-iframe');

        if (data["action"] === "previous_page") {
            //find button inside iframe
            // let button = iframe.contents().find('#previous');
            // //trigger button click
            // button.trigger("click");
            $('#previous').click();
        } else if (data["action"] === "next_page") {
            $('#next').click();
            // click(600, 200);
        }

    });

    // show the selected student's data (name, star, diamond and etc.)
    // global variables
    let STUDENT_ID = null; // this is needed when sending signal to update star count in server

    socket.on('select_student_signal_receive', function (data) {
        // data -> {'name': 'Alex', 'star': 0, 'diamond': 0, 'id': 'this is needed to send signal to server to add stars'}

        // &nbsp; for space at right
        $('#student_name_div').empty().append("<h5 class=\"title is-5\" id=\"student_name\">" + `${data['name']}` + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</h5>");
        // star update
        let left_stars = parseInt(data['star']) % 10;// as there are 10 stars each, so current sprint progress
        if (left_stars == null)
            left_stars = 0;
        for (let i = 0; i < left_stars; i++)
            $(`#star_count_${i}`).css('color', 'gold'); // update the style -> make the color gold
        // clear the styles afters
        for (let i = left_stars; i < 10; i++) // as 0  index so for 10 items 0...9
            $(`#star_count_${i}`).css('color', '');
        // total
        $('#star_count').text(data['star'].toString());
        $('#diamond_count').text(data['diamond'].toString());
        // show if hidden previously => on first student choice
        if (STUDENT_ID == null) {
            $('#app_logo_section').empty().append("<figure class=\"image is-48x48\">\n" +
                "                    <img src=\"https://cdn4.iconfinder.com/data/icons/occupation-and-people-avatar-vol-2-2/128/man_avatar_student_young_people_male_graduated-512.png\"\n" +
                "                         alt=\"\">\n" +
                "                </figure>");
            // make star bar visible and others
            $('#student_name_div').css('visibility', 'visible');
            $('#stars_bar').css('visibility', 'visible');
            $('#stars_count_div').css('visibility', 'visible');
            $('#diamond_count_div').css('visibility', 'visible');
        }
        STUDENT_ID = data['id'];
    });

    // animation trigger receive from window 3

    // dice animation preset
    $("#dice-color").val("#323131");
    $("#dot-color").val("#ffd700");
    let rnd;
    let x, y;
    $("#dot-color").change(function () {
        const dot = $("#dot-color").val();
        $(".dot").css("background-color", dot);
    });
    $("#dice-color").change(function () {
        const dice = $("#dice-color").val();
        $(".side").css("background-color", dice);
    });

    // actual trigger functions
    socket.on('animation_trigger_emit_to_win2', function (data) {
        let animation_type = data['animation_type'];
        console.log("animation type from window2.js is " + animation_type);
        if (animation_type === "star") {
            document.getElementById('play_star_sound').click();
            confetti.start();
            $('#star_animation_div').show(1).delay(4500).hide(1);
            setTimeout(function () {
                confetti.stop();
                // send the id to server to update the record
                socket.emit('add_star_to_student_record', {'id': STUDENT_ID});
                // update stars & diamond counts in the top bar // todo: handle 9+1 = 10 => 0 and a diamond case
                let star_count = parseInt($('#star_count').text());
                if (star_count == null)
                    star_count = 0;
                star_count++;
                $('#star_count').text(star_count.toString());
                // if star_count (updated after + 1) is divisible by 10 then we add +1 star

                if (star_count % 10 === 0) {
                    let diamond_count = parseInt($('#diamond_count').text());
                    if (diamond_count == null)
                        diamond_count = 0;
                    diamond_count++;
                    $('#diamond_count').text(diamond_count.toString());
                }

                // todo: update ths stars in the bar and also handle the EDGE case of 10 stars -> diamond

            }, 4000);


        } else if (animation_type === "dice") {
            // dice animation code
            $('#dice_animation_div').show(1).delay(2000).hide(1);
            // e.preventDefault();
            rnd = Math.floor(Math.random() * 6 + 1);
            switch (rnd) {
                case 1:
                    x = 720;
                    y = 810;
                    break;
                case 6:
                    x = 720;
                    y = 990;
                    break;
                default:
                    x = 720 + (6 - rnd) * 90;
                    y = 900;
                    break;
            }
            $(".dice").css(
                "transform",
                "translateZ(-100px) rotateY(" + x + "deg) rotateX(" + y + "deg)"
            );
        }

    });

    let should_stop = false;

    // time trigger receive from window 3
    socket.on('timer_trigger_emit_to_win2', function (data) {
        let timer_data = data['timer_data'];
        // can be actually none or it can send to change the time (from settings of timer)
        if (timer_data === "None")
            // pop up the modal to set up time
            $('#timer_modal').removeClass("modal").addClass("modal is-active");
        else {
            console.log(data['start_or_end']);
            if (data['start_or_end'].toLowerCase() === 'end')
                should_stop = true;
            else {
                should_stop = false;
                const countDownDate = new Date();
                let hr = parseInt(data['timer_data']['hour']);
                if (hr)
                    countDownDate.setHours(countDownDate.getHours() + hr);
                let mn = parseInt(data['timer_data']['minutes']);
                if (mn)
                    countDownDate.setMinutes(countDownDate.getMinutes() + mn);
                let sc = parseInt(data['timer_data']['seconds']);
                if (sc)
                    // why +1 seconds ? because we miss 1 seconds to pass the info from window 3 to window 2
                    countDownDate.setSeconds(countDownDate.getSeconds() + sc + 1);

                let x = setInterval(function () {

                    // Get today's date and time
                    const now = new Date().getTime();

                    // Find the distance between now and the count down date
                    const distance = countDownDate - now;

                    // Time calculations for days, hours, minutes and seconds
                    // var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

                    // Output the result in an element with id="demo"
                    if (hours)
                        document.getElementById("time_count").innerHTML = (hours > 9 ? hours : "0" + hours) + ":"
                            + (minutes > 9 ? minutes : "0" + minutes) + ":" + (seconds > 9 ? seconds : "0" + seconds);
                    else
                        document.getElementById("time_count").innerHTML = (minutes > 9 ? minutes : "0" +
                            minutes) + ":" + (seconds > 9 ? seconds : "0" + seconds);

                    // If the count down is over, write some text
                    if (distance < 0 || should_stop) {
                        console.log("here");
                        clearInterval(x);
                        document.getElementById("time_count").innerHTML = "00:00";
                    }
                }, 1000);
            }
        }
    });

    // save the time settings and others util regarding this
    $('#save_time').click(function () {
        $.ajax({
            url: "/save_time_count",
            type: "POST",
            data: {
                "hour": $('#hours').val(),
                "minutes": $('#minutes').val(),
                "seconds": $('#seconds').val()
            }
        }).done(function (data) {
            if (data["status"] === 1) {
                $('#timer_modal').removeClass("modal is-active").addClass("modal");
            } else {
                // todo: show error something
            }
        });
    });


    // drawing tools and all
    let canvas = null;
    let ctx = null;


    socket.on('drawing_tools_trigger', function (data) {
        // draw, erase, color, thickness, text, full_clear
        let type_of_action = data['type_of_action'];

        if (type_of_action === 'draw' || type_of_action === "full_clear") {
            $('#drawing-div').empty().append(
                "<canvas id=\"drawing-board\" width=\"1500\" height=\"800\"></canvas>");
            // init from here
            canvas = document.getElementById("drawing-board");
            ctx = canvas.getContext("2d");
            ctx.lineWidth = "3";
            ctx.strokeStyle = "red"; // Green path
            ctx.globalCompositeOperation = "source-over";

        } else if (type_of_action === "erase") {
            // ctx.strokeStyle = 'green';
            ctx.globalCompositeOperation = "destination-out";
            ctx.arc(95, 50, 50, 0, 2 * Math.PI);
            ctx.fill();
        } else if (type_of_action === "thickness_size") {
            ctx.lineWidth = data["thickness_size"];
            ctx.globalCompositeOperation = "source-over";
        } else if (type_of_action === "color_change") {
            //  alert(type_of_action);
            ctx.strokeStyle = data["color"];
            ctx.globalCompositeOperation = "source-over";
        }


        // re initialize the draw board functions
        // is_draw = False means erase action
        let BB = canvas.getBoundingClientRect();
        let offsetX = BB.left;
        let offsetY = BB.top;

        let lastX, lastY;
        let isDown = false;

        canvas.onmousedown = handleMousedown;
        canvas.onmousemove = handleMousemove;
        canvas.onmouseup = handleMouseup;


        function handleMousedown(e) {
            e.preventDefault();
            e.stopPropagation();
            lastX = e.clientX - offsetX;
            lastY = e.clientY - offsetY;
            isDown = true;
        }

        function handleMouseup(e) {
            e.preventDefault();
            e.stopPropagation();
            isDown = false;
        }

        function handleMousemove(e) {
            e.preventDefault();
            e.stopPropagation();

            if (!isDown) {
                return;
            }

            let mouseX = e.clientX - offsetX;
            let mouseY = e.clientY - offsetY;

            ctx.beginPath();

            ctx.moveTo(lastX, lastY);
            ctx.lineTo(mouseX, mouseY);
            ctx.stroke();

            lastX = mouseX;
            lastY = mouseY;
        }

    });

    // star animation code
    var confetti = {
        maxCount: 150,
        speed: 2,
        frameInterval: 15,
        alpha: 1,
        gradient: !1,
        start: null,
        stop: null,
        toggle: null,
        pause: null,
        resume: null,
        togglePause: null,
        remove: null,
        isPaused: null,
        isRunning: null
    };
    !function () {
        confetti.start = s, confetti.stop = w, confetti.toggle = function () {
            e ? w() : s()
        }, confetti.pause = u, confetti.resume = m, confetti.togglePause = function () {
            i ? m() : u()
        }, confetti.isPaused = function () {
            return i
        }, confetti.remove = function () {
            stop(), i = !1, a = []
        }, confetti.isRunning = function () {
            return e
        };
        var t = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window
                .mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame,
            n = ["rgba(30,144,255,", "rgba(107,142,35,", "rgba(255,215,0,", "rgba(255,192,203,", "rgba(106,90,205,",
                "rgba(173,216,230,", "rgba(238,130,238,", "rgba(152,251,152,", "rgba(70,130,180,",
                "rgba(244,164,96,", "rgba(210,105,30,", "rgba(220,20,60,"
            ],
            e = !1,
            i = !1,
            o = Date.now(),
            a = [],
            r = 0,
            l = null;

        function d(t, e, i) {
            return t.color = n[Math.random() * n.length | 0] + (confetti.alpha + ")"), t.color2 = n[Math.random() *
            n.length | 0] + (confetti.alpha + ")"), t.x = Math.random() * e, t.y = Math.random() * i - i, t
                .diameter = 10 * Math.random() + 5, t.tilt = 10 * Math.random() - 10, t.tiltAngleIncrement = .07 *
                Math.random() + .05, t.tiltAngle = Math.random() * Math.PI, t
        }

        function u() {
            i = !0
        }

        function m() {
            i = !1, c()
        }

        function c() {
            if (!i)
                if (0 === a.length) l.clearRect(0, 0, window.innerWidth, window.innerHeight), null;
                else {
                    var n = Date.now(),
                        u = n - o;
                    (!t || u > confetti.frameInterval) && (l.clearRect(0, 0, window.innerWidth, window.innerHeight),
                        function () {
                            var t, n = window.innerWidth,
                                i = window.innerHeight;
                            r += .01;
                            for (var o = 0; o < a.length; o++) t = a[o], !e && t.y < -15 ? t.y = i + 100 : (t
                                    .tiltAngle += t.tiltAngleIncrement, t.x += Math.sin(r) - .5, t.y += .5 * (Math
                                    .cos(r) + t.diameter + confetti.speed), t.tilt = 15 * Math.sin(t.tiltAngle)
                            ), (t.x > n + 20 || t.x < -20 || t.y > i) && (e && a.length <= confetti
                                .maxCount ? d(t, n, i) : (a.splice(o, 1), o--))
                        }(),
                        function (t) {
                            for (var n, e, i, o, r = 0; r < a.length; r++) {
                                if (n = a[r], t.beginPath(), t.lineWidth = n.diameter, i = n.x + n.tilt, e = i + n
                                    .diameter / 2, o = n.y + n.tilt + n.diameter / 2, confetti.gradient) {
                                    var l = t.createLinearGradient(e, n.y, i, o);
                                    l.addColorStop("0", n.color), l.addColorStop("1.0", n.color2), t.strokeStyle = l
                                } else t.strokeStyle = n.color;
                                t.moveTo(e, n.y), t.lineTo(i, o), t.stroke()
                            }
                        }(l), o = n - u % confetti.frameInterval), requestAnimationFrame(c)
                }
        }

        function s(t, n, o) {
            var r = window.innerWidth,
                u = window.innerHeight;
            window.requestAnimationFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame ||
                window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window
                    .msRequestAnimationFrame || function (t) {
                    return window.setTimeout(t, confetti.frameInterval)
                };
            var m = document.getElementById("confetti-canvas");
            null === m ? ((m = document.createElement("canvas")).setAttribute("id", "confetti-canvas"), m
                .setAttribute("style", "display:block;z-index:999999;pointer-events:none;position:fixed;top:0"),
                document.body.prepend(m), m.width = r, m.height = u, window.addEventListener("resize",
                function () {
                    m.width = window.innerWidth, m.height = window.innerHeight
                }, !0), l = m.getContext("2d")) : null === l && (l = m.getContext("2d"));
            var s = confetti.maxCount;
            if (n)
                if (o)
                    if (n == o) s = a.length + o;
                    else {
                        if (n > o) {
                            var f = n;
                            n = o, o = f
                        }
                        s = a.length + (Math.random() * (o - n) + n | 0)
                    }
                else s = a.length + n;
            else o && (s = a.length + o);
            for (; a.length < s;) a.push(d({}, r, u));
            e = !0, i = !1, c(), t && window.setTimeout(w, t)
        }

        function w() {
            e = !1
        }
    }();


});