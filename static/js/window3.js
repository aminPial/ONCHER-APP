$(document).ready(function () {
    let socket = io.connect('/');
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
        // todo: make animation like the AWARD ICON pops up from W3 to W2... and thus hide the star icon from W3
        // make the animation trigger icon -> disable
       // $('#star_animation_trigger').unbind('click');
        socket.emit('animation_trigger', {"data": "star"});
        // then after X ms make it enable again
        // setTimeout(function () {
        //         $('#star_animation_trigger').bind('click');
        //     }, 4500);
    });

    // todo: games

    // todo: toss


    // dice
    $('#dice_animation_trigger').click(function () {
        // check todo in star animation click function
        socket.emit('animation_trigger', {"data": "dice"});
    });




    // timer trigger
    $('#start_end_timer_button').click(function () {
        let st = $('#start_end_timer_button');
        let start_or_end = st.text().toLowerCase();
        if (start_or_end === 'start')
            st.text("End");
        else
            st.text("Start");
        // todo: if no time is set then pop up (response from the server that time has not set)
        socket.emit('timer_trigger', {'start_or_end': start_or_end});
    });
    // open time settings
    $('#timer_settings').click(function () {
        socket.emit('open_time_settings', {'': ''});
    });


    // drawing tools send signals
    $('#draw_tool').click(function () {
        socket.emit('drawing_tools_signal_receive', {'type_of_action': 'draw'});
    });
    $('#erase_tool').click(function () {
        socket.emit('drawing_tools_signal_receive', {'type_of_action': 'erase'});
    });

    $('#clear_tool').click(function () {
        socket.emit('drawing_tools_signal_receive', {'type_of_action': 'full_clear'});
    });

    $('#color_pick_tool').click(function () {
        $('#toolbar').hide(500)
        $('#colors').show(200);
    });
    // close color select
    $('#close_color_select').click(function () {
        $('#toolbar').show(500)
        $('#colors').hide(200);
    });


    $('#thickness_tool').click(function () {
        $('#toolbar').hide(500)
        $('#thickness').show(200);
    });

    // close thickness select
    $('#close_thickness_select').click(function () {
        $('#toolbar').show(500)
        $('#thickness').hide(200);
    });


});