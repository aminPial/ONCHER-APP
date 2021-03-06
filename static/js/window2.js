$(document).ready(function () {
    let socket = io.connect('/');
    // socket.on('connect', function () {
    //     socket.emit('my event', {data: 'Connected from windows2.html'});
    // });

    socket.on('my response', function (data) {
        console.log('Received link: ', data["link"]);
        // $('#responsive-iframe').attr('src', data["link"]);

        $('#iframe-container').empty().append("<iframe class=\"responsive-iframe\" id=\"responsive-iframe\" allowFullScreen width=\"100%\" height=\"500px\"\n" +
            "                frameBorder=\"0\"\n" +
            "                src=\"" + data['link'] + "\">");
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

    // animation trigger receive from window 3
    socket.on('animation_trigger_emit_to_win2', function (data) {
        let animation_type = data['animation_type'];
        console.log("animation type from window2.js is " + animation_type);
        if (animation_type === "star") {
            document.getElementById('play_star_sound').click();
            $('.animation_div').show(1).delay(4500).hide(1);
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
            ctx.arc(95, 50, 40, 0, 2 * Math.PI);
            ctx.fill();
        } else if (type_of_action === "thickness_size") {
            ctx.lineWidth = data["thickness_size"];
            ctx.globalCompositeOperation = "source-over";
        }
        else if (type_of_action === "color_change") {
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

});