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
    $('#toss_animation_trigger').click(function () {
        // check todo in star animation click function
        socket.emit('animation_trigger', {"data": "toss"});
    });

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

    // K/A switch
    let k_or_a = "K";
    $('#K_A_switch').click(function () {
        if (k_or_a === "K") {
            k_or_a = "A";
            $('#kids_trigger').css({'color': 'black'});
            $('#adult_trigger').css({'color': 'gold'});
        } else {
            k_or_a = "K";
            $('#adult_trigger').css({'color': 'black'});
            $('#kids_trigger').css({'color': 'gold'});
        }
        socket.emit('k_a_switch', {'k_or_a': k_or_a});
    });

    // games
    $('#games_start_trigger').click(function () {
        socket.emit('switch_to_games_receive', {'': 'games korte hbe'});
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

    // last game => game4 special function
    socket.on('game_4_init_emit_signal', function (data) {
        // this will be used for "SAY CAT" and etc.
        $('#image_name').text(data['image_name']); // has to be ALL CAPS
        $('#game_4_special').show();
    });

    // screenshot related triggers
    let student_object_data = null;
    let selected_lesson = null;
    // student object update on student-select trigger
    socket.on('select_student_signal_receive', function (data) {
        student_object_data = data['full_student_object_in_dict_format'];
    });
    socket.on('lesson_update_trigger', function (data) {
        selected_lesson = data['lesson'];
    });

    $('#take_screenshot').click(function () {
        socket.emit('take_screenshot', {
            'full_student_object_in_dict_format': student_object_data,
            'selected_lesson': selected_lesson,
            'is_continuous': false
        });
    });

    let is_on_now = false;
    let default_interval_for_ss = 5; // 5 seconds as default
    // we need a signal to update interval
    // normal on load & dynamic - on update (on fly) [both same, one is from W3.py and another is W2.py]
    socket.on('updated_ss_interval_time', function (data) {
        default_interval_for_ss = data['seconds'];
    });
    let interval_var = null;
    let send_data_interval = null;

    function openfolder() {
        let a = $('#switch_on_off');
        a.attr({'class': 'fal fa-pause'});
        setTimeout(function () {
            a.attr({'class': 'fa fa-pause'});
        }, 550);
    }

    $('#switch_on_off').click(function () {

        if (is_on_now) {
            //   alert("OFF");
            // then make it off
            clearInterval(interval_var);
            clearInterval(send_data_interval);
            interval_var = null;
            send_data_interval = null;
            $('#switch_on_off').attr({'class': 'fal fa-play'});
        } else {
            // alert("ON")
            if (default_interval_for_ss !== null && student_object_data !== null && selected_lesson !== null) {
                // execute the screenshot caller
                send_data_interval = setInterval(function () {
                    socket.emit('take_screenshot', {
                        'full_student_object_in_dict_format': student_object_data,
                        'selected_lesson': selected_lesson,
                        'is_continuous': true
                    });
                }, default_interval_for_ss * 1000); // sec => milli-sec

                openfolder();
                interval_var = setInterval(openfolder, 1100);

            } else {
                // todo: show this in the window 2
                alert("Missing lesson/student. Please select before taking ss");
            }
        }
        is_on_now = !is_on_now;
    });

    $('#timer-settings').click(function () {
        // this will be received in window 2 to show a pop up to change settings
        // that "What will be the interval?" of taking ss
        socket.emit('screenshot_timer_settings', {});
    });


});