$(document).ready(function () {
    let socket = io.connect('http://127.0.0.1:5000');
    // socket.on('connect', function () {
    //     socket.emit('my event', {data: 'Connected from windows2.html'});
    // });

    socket.on('my response', function (data) {
        console.log('Received link: ', data["link"]);
        // $('#responsive-iframe').attr('src', data["link"]);

        $('#iframe-container').empty().append("<iframe class=\"responsive-iframe\" id=\"responsive-iframe\" allowFullScreen width=\"100%\" height=\"500px\"\n" +
            "                frameBorder=\"0\"\n" +
            "                src=\"" + data['link'] + "\">")
        // $('#responsive-iframe').attr("src", $('#responsive-iframe').attr("src"));
    });

    function click(x, y) {
        let ev = new MouseEvent('click', {
            'view': window,
            'bubbles': true,
            'cancelable': true,
            'screenX': x,
            'screenY': y
        });

        let el = $('#responsive-iframe').elementFromPoint(x, y);
        console.log(el); //print element to console
        el.dispatchEvent(ev);
    }


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

});