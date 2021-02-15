$(document).ready(function () {
    let socket = io.connect('http://127.0.0.1:5000');
    // socket.on('connect', function () {
    //     socket.emit('my event', {data: 'Connected from windows3.html'});
    // });
    // todo: let window3 know what has been loaded => ppt or pdf, according that we will emit signal
    $('#previous_page').click(function () {
        socket.emit('navigation_signal_emit', {"data": "previous_page"});
    });
    $('#next_page').click(function () {
        socket.emit('navigation_signal_emit', {"data": "next_page"});
    });


    // animation trigger

    // 1. star animation
    $('#star_animation_trigger').click(function () {
        socket.emit('animation_trigger', {"data": "star"});
    });

});