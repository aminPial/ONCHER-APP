$(document).ready(function () {


    let socket = io.connect('/');

    // close_window
    $('#close_window').click(function () {
        socket.emit('close_window', {});
    });
    $('#maximize_window').click(function () {
        socket.emit('maximize_window', {});
    });
    $('#minimize_window').click(function () {
        socket.emit('minimize_window', {});
    });
    $('#settings_window').click(function () {
        // todo: show settings window here...
        // color scheme is the main one..
    });

    // Get all dropdowns on the page that aren't hoverable.
    const dropdowns = document.querySelectorAll('.dropdown:not(.is-hoverable)');

    if (dropdowns.length > 0) {
        // For each dropdown, add event handler to open on click.
        dropdowns.forEach(function (el) {
            el.addEventListener('click', function (e) {
                e.stopPropagation();
                el.classList.toggle('is-active');
            });
        });

        // If user clicks outside dropdown, close it.
        document.addEventListener('click', function (e) {
            closeDropdowns();
        });
    }

    /*
     * Close dropdowns by removing `is-active` class.
     */
    function closeDropdowns() {
        dropdowns.forEach(function (el) {
            el.classList.remove('is-active');
        });
    }

// Close dropdowns if ESC pressed
    document.addEventListener('keydown', function (event) {
        let e = event || window.event;
        if (e.key === 'Esc' || e.key === 'Escape') {
            closeDropdowns();
        }
    });


    // canvases and ctx-es | size will be equal
    let canvases = [];
    let ctx_es = [];
    let current_canvas = null;
    let current_doc_type = null; // 'pdf', 'ppt'
    let data = null;
    // is_drawing <type: boolean>
    // todo: make is_drawing null when moved to somewhere other than docs, e.g: games
    let is_drawing = null; // is_drawing = false means 'erasing' , null means other than draw and erase
    // let eraser_canvas = document.getElementById('eraser-circle');

    // todo: initially before even clicking the pen the shit is drawing,, fix this
    socket.on('study_doc_update', function (da) {
        data = da;
        let doc_container = $('#iframe-container');
        let loading_container = $('#loading_box');
        let initial_box = $('#initial_box');

        if (data['is_loading']) {
            show_notifications(true, "Doc is loading");
            // todo: show loading anim and all
            initial_box.hide();
            doc_container.hide();
            $('#student-report-input').hide();
            loading_container.show();
            $('#time_count_div').css('visibility', 'hidden');
        } else {

            // show top app bar
            $('#top-bar').show();

            doc_container.empty(); // clear all the content inside it

            let width = $(document).width() - 0; // extra space - X

            if (data['is_pdf']) {
                current_doc_type = 'pdf';
                // re-int
                canvases = [];
                ctx_es = [];
                // for (let i = 0; i < data['page_count']; i++) {
                //     // current image format is .png # you have to change it in window 1 and here to take effect the change
                //     doc_container.append("<img id= " + `"img_${i}"` + " style='margin-top: 8px;' " +
                //         `src="${data['parsed_pdf_dir_path'] + "/" + i + ".png"}"`
                //         + " alt=" + `"${i}"/>`);
                // }
                let ratio = data['width'] / data['height'];
                let height = width / ratio;

                for (let j = 0; j < data['page_count']; j++) {
                    doc_container.append("<canvas  " + " id=\"pdf_canvas_" + `${j}` + "\"" + ">\n" +
                        "            Your browser does not support the HTML5 canvas tag.\n" +
                        "        </canvas>\n");
                    //alert(`"${data['base_url']}${data['parsed_pdf_dir_path']}/${j}.png"`);
                    $(`#pdf_canvas_${j}`).attr({
                        'width': `${width}px`,
                        'height': `${height}px`
                    }).css({
                        // todo: BASE_URL, get from the JSON e.g: data['BASE_URL']
                        'background': `url("${data['base_url']}${data['parsed_pdf_dir_path']}/${j}.png")`,
                        'background-position': 'center',
                        'background-size': '100% 100%'
                    }).hover(function () {
                        //alert("hover: " + event.clientY + " " + event.clientX);
                        revise_canvas_on_click(j);
                    }).click(function () {
                        // alert("click: " + event.clientY + " " + event.clientX);
                        revise_canvas_on_click(j);
                    });

                    const myCanvas = document.getElementById(`pdf_canvas_${j}`);
                    canvases.push(myCanvas);
                    ctx_es.push(myCanvas.getContext('2d'));
                }
            } else {
                current_doc_type = 'ppt';
                // re-init
                canvases = [];
                ctx_es = [];
                // alert("Here");
                // for ppt, pptx
                doc_container.append("<iframe class=\"responsive-iframe\"  id=\"responsive-iframe\"" +
                    ` allowfullscreen  width=\"${width}px\" height=\"500px\"\n` +
                    "                frameBorder=\"0\"\n" +
                    "                src=\"" + data['ppt_url'] + "\">");

                $('#responsive-iframe').on('load', function () {
                    // code will run after iframe has finished loading
                    // alert("Loaded");
                    // context1.beginPath();
                    // context1.rect(188, 50, 200, 100);
                    // context1.fillStyle = 'yellow';
                    // context1.fill();
                    // context1.lineWidth = 7;
                    // context1.strokeStyle = 'green';
                    // context1.stroke();
                });
            }

            initial_box.hide();
            loading_container.hide();
            $('#student-report-input').hide();
            $('#view-student-report-div').hide();
            doc_container.show();
            $('#time_count_div').css('visibility', 'visible');
        }

    });


    function revise_canvas_on_click(index) {
        // todo: make this function efficient
        let canvas_to_render = canvases[index]; // this has js version
        let current_ctx = ctx_es[index];

        let doc_canvas = null;
        if (current_doc_type === 'ppt')
            doc_canvas = $(`#ppt_canvas`); // jquery version
        else
            doc_canvas = $(`#pdf_canvas_${index}`);

        let lastX, lastY;
        let isDown = false;

        // start
        canvas_to_render.onmousedown = handleMousedown;
        //  canvas_to_render.touchstart = handleMousedown;
        // draw
        canvas_to_render.onmousemove = handleMousemove;
        // canvas_to_render.touchmove = handleMousemove;
        // other
        canvas_to_render.onmouseup = handleMouseup;


        function handleMousedown(e) {
            if (is_drawing != null) {
                e.preventDefault();
                e.stopPropagation();

                lastX = e.pageX - $(document).scrollLeft() - doc_canvas.offset().left;
                lastY = e.pageY - $(document).scrollTop() - doc_canvas.offset().top;
                isDown = true;
            }
        }

        function handleMouseup(e) {
            if (is_drawing != null) {
                e.preventDefault();
                //  e.stopPropagation();
                isDown = false;

            }
        }

        function handleMousemove(e) {
            if (is_drawing !== null) {
                //  console.log("X: " + scrollX + " Y" + scrollY);
                e.preventDefault();
                e.stopPropagation();

                if (!isDown) {
                    return;
                }

                let mouseX = e.pageX - $(document).scrollLeft() - doc_canvas.offset().left;
                let mouseY = e.pageY - $(document).scrollTop() - doc_canvas.offset().top;
                //  console.log("X: " + lastX + " Y: " + lastY);
                //  console.log("X1: " + mouseX + " Y1: " + mouseY);

                if (is_drawing) {
                    // draw
                    current_ctx.beginPath();
                    current_ctx.moveTo(lastX, lastY);
                    current_ctx.lineTo(mouseX, mouseY);
                    current_ctx.lineCap = "round";
                    current_ctx.lineJoin = "round";
                    current_ctx.stroke();
                } else {
                    // eraser_canvas.width = 200;
                    // eraser_canvas.height = 200;
                    // eraser_canvas.style.left = `${lastX}px`;
                    // eraser_canvas.style.top = `${lastY}px`;
                    // erase
                    // alert("hi");
                    // todo: this worked but show a circle ...
                    current_ctx.arc(lastX, lastY, 8, 0, Math.PI * 2, false);
                    current_ctx.fill();
                }
                // update
                lastX = mouseX;
                lastY = mouseY;
            }
            // else { do nothing... }
        }
    }

    // drawing tools trigger from window -3
    socket.on('drawing_tools_trigger', function (payload) {
        // draw, erase, color, thickness, text, full_clear
        let type_of_action = payload['type_of_action'];

        // todo: ? for ppt
        if (type_of_action === 'draw' || type_of_action === "full_clear") {
            if (current_doc_type === 'ppt' && document.getElementById(`ppt_canvas`) === null) {
                //  alert("here");
                init_drawing_board_for_ppt();
            }
        }

        // let erase_circle = $('#eraser-circle');
        is_drawing = type_of_action !== "erase" && type_of_action !== "full_clear";

        let canvas_count = canvases.length;
        for (let c = 0; c < canvas_count; c++) {
            let ctx = ctx_es[c];
            let current_canvas = canvases[c];
            if (type_of_action === 'draw') {
                ctx.lineWidth = "3";
                ctx.strokeStyle = "red";
                ctx.globalCompositeOperation = "source-over";
            } else if (type_of_action === "full_clear") {
                // https://stackoverflow.com/questions/6893939/how-to-erase-on-canvas-without-erasing-background
                ctx.clearRect(0, 0, current_canvas.width, current_canvas.height);
            } else if (type_of_action === "erase") {
                ctx.globalCompositeOperation = "destination-out";
            } else if (type_of_action === "thickness_size") {
                ctx.lineWidth = payload["thickness_size"];
            } else if (type_of_action === "color_change") {
                ctx.strokeStyle = payload["color"];
            }
                // todo: draw text dynamically
            // https://www.youtube.com/watch?v=pRYF07gI8gk
            else {
                show_notifications(false, "No Action matched in draw tools");
            }
            ctx_es[c] = ctx;
        }

    });

    function init_drawing_board_for_ppt() {
        $('#drawing-div').empty().append("<canvas  " + " id=\"ppt_canvas" + "\"" + ">\n" +
            "            Your browser does not support the HTML5 canvas tag.\n" +
            "        </canvas>\n");
        $(`#ppt_canvas`).attr({
            'width': `${$(document).width() - 0}px`,
            'height': `${550}px` // todo: fix this based on height of window
        }).hover(function () {
            //alert("hover: " + event.clientY + " " + event.clientX);
            revise_canvas_on_click(0);
        }).click(function () {
            // alert("click: " + event.clientY + " " + event.clientX);
            revise_canvas_on_click(0);
        });

        const myCanvas1 = document.getElementById(`ppt_canvas`);
        // first we will clear all the canvas and context from the array
        // and push only them at [0] index
        canvases.push(myCanvas1);
        ctx_es.push(myCanvas1.getContext('2d'));
    }


    // students report form
    socket.on('students_list_update', function (data) {
        let st = $('#student-report-forms');
        st.empty();
        let student_list = data['students'];
        for (let k = 0; k < student_list.length; k++) {
            st.append();
        }
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
    // socket.on('navigation_signal_receive', function (data) {
    //
    //     let iframe = $('#responsive-iframe');
    //
    //     if (data["action"] === "previous_page") {
    //         //find button inside iframe
    //         // let button = iframe.contents().find('#previous');
    //         // //trigger button click
    //         // button.trigger("click");
    //         $('#previous').click();
    //     } else if (data["action"] === "next_page") {
    //         $('#next').click();
    //         // click(600, 200);
    //     }
    //
    // });

    // Toast notifications
    // show notifications and related triggers
    function show_notifications(is_positive, message) {
        document.getElementById(`${is_positive ? 'play_success_sound' : 'play_error_sound'}`).click();
        // $("#notific").animate({
        //     left: '250px',
        //     opacity: '0.5',
        //     height: '100px',
        //     width: '100px'
        // });

        $('#is-positive').text(is_positive ? `Hooray!` : 'Oops!');
        $('#notification-message').text(message)
        $('#notific').attr({
            'class': is_positive ? 'notification is-success is-light' :
                'notification is-danger is-light'
        }).show();
        setTimeout(function () {
            $('#notific').hide();
        }, 1000 * 4);
    }

    $('#close_notification').click(function () {
        $('#notific').hide(); // todo: maybe animate?
    });

    socket.on('receive_notification_message', function (data) {
        show_notifications(data['is_positive'], data['message'])
    })


    socket.on('screen_shots_taken', function (data) {
        show_notifications(true, `Screenshot saved as ${data['filename']}`);
    });

    // view ss report signal receiver
    // signal received from window-1 to open ss report in window-2
    socket.on('view_ss_report_open_signal_receive', function (data) {
        // prepare the data
        $('#student_report_of').text(`Student Report of ${data['name']}`)
        let reports_of_a_student = $('#reports_of_a_student');
        reports_of_a_student.empty();
        let length_of_reports = data['student_report_objects'].length;
        for (let u = 0; u < length_of_reports; u++) {
            reports_of_a_student.append(" <div class=\"box\">\n" +
                `                    <h5 class=\"subtitle is-5\" style=\"font-weight: bolder;\">Report Time: ${data['student_report_objects'][u]['when']}</h5>\n` +
                `                    <textarea class=\"textarea\" disabled style=\"resize: none\">${data['student_report_objects'][u]['report_saved']}\n` +
                "                </textarea>\n" +
                "                </div>");
        }
        // arrange elem
        $('#initial_box').hide();
        $('#choose_games').hide();
        $('#student-report-input').hide();
        $('#settings_box').hide();
        $('#view-student-report-div').show();

    });

    // one is 'choose ppt.pdf or flashcard page' and another is 'actual adding'
    // when in 1st one we go back to main initial box
    // and in 2nd we go back to 1st one
    let on_which_config_page_now = null;

    socket.on('configure_signal_receive', function (data) {
        // on get the show config page signal
//        $('#intro_screen').hide();
        $('#view-student-report-div').hide();
        $('#initial_box').hide();
        $('#choose_games').hide();
        $('#student-report-input').hide();
        $('#settings_box').show();
        on_which_config_page_now = '1'; // as we now go to 1st page of config
    });

    $('#configure-back').click(function () {
        $('#view-student-report-div').hide();
        $('#choose_games').hide();
        $('#student-report-input').hide();
        // when encounter 1st page
        if (on_which_config_page_now === '1') {
            $('#initial_box').show();
            $('#settings_box').hide();
            on_which_config_page_now = null;
        } else {
            // 2nd page
            $('#settings_cards').show();
            $('#grade_lesson_list_section').show();
            $('#add_ppt_pdf_div').hide();
            $('#add_flashcard').hide();
            on_which_config_page_now = '1';
        }
    });

    $('#upload_ppt_pdf').click(function () {
        $('#view-student-report-div').hide();
        $('#settings_cards').hide();
        $('#grade_lesson_list_section').hide();
        $('#add_ppt_pdf_div').show();
        $('#student-report-input').hide();
        $('#add_flashcard').hide();
        on_which_config_page_now = '2'; // we go 2nd page now
    });

    $('#flashcard_upload').click(function () {
        $('#view-student-report-div').hide();
        $('#settings_cards').hide();
        $('#grade_lesson_list_section').hide();
        $('#add_ppt_pdf_div').hide();
        $('#student-report-input').hide();
        $('#add_flashcard').show();
        on_which_config_page_now = '2'; // we go to 2nd page now
    });

    // report
    let students_object = null;

    socket.on('students_list_update', function (data) {
        students_object = data['students'];
        // alert("length => " + students_object.length);
        // now append to the section
        let student_report_forms = $('#student-report-forms');
        student_report_forms.empty();
        for (let t = 0; t < students_object.length; t++) {
            //  alert("t => " + t);
            student_report_forms.append("<div class=\"box\">\n" +
                "                                <div class=\"field\">\n" +
                `                                    <label class=\"label\" style=\"font-family: 'HP Simplified',serif;font-size: 20px;\">${t + 1}. ${students_object[t]['name']}</label>\n` +
                "                                    <div class=\"control\">\n" +
                `                                        <textarea class=\"textarea\" placeholder=\"write student report of ${students_object[t]['name']} here\" id='report-${students_object[t]['id']}'></textarea>\n` +
                "                                    </div>\n" +
                "                                </div>\n" +
                "                            </div>");
        }
    });

    $('#report-save-submit').click(function (e) {
        e.preventDefault(); // also add preventDefault() to restrict page refreshing
        // prepare data
        //  alert("length from report save => " + students_object.length);
        let report = [];
        for (let h = 0; h < students_object.length; h++) {
            report.push({
                'student-id': students_object[h]['id'],
                'report': $(`#report-${students_object[h]['id']}`).val() // e.g: id ="report-1"
            });
        }
        // alert("Data here " + JSON.stringify(report));

        $.ajax({
            url: "/student_report_submit",
            type: "POST",
            data: {
                "report": JSON.stringify(report)
            },
            // processData: false,  // tell jQuery not to process the data
            // contentType: false   // tell jQuery not to set contentType
        }).done(function (data) {
            //   alert("data " + data['status']);
            if (data["status"] === 0) {
                show_notifications(false, "Something is wrong while saving student report");
            } else {
                // todo: show a success notifications...
                $('#student-report-input').hide();
                $('#choose_games').hide();
                $('#settings_box').hide();
                $('#iframe-container').hide();
                $('#loading_box').hide();
                $('#initial_box').show(); // todo: shouldn't it be the initial box.. intro ?
            }
        });

    });
    $('#report-save-cancel').click(function () {
        $('#view-student-report-div').hide();
        $('#student-report-input').hide();
        $('#choose_games').hide();
        $('#settings_box').hide();
        $('#iframe-container').hide();
        $('#loading_box').hide();
        $('#initial_box').show(); // todo: shouldn't it be the initial box.. intro ?
    });

    // initial box 'GO buttons' functions
    $('#add_ppt_pdf_go').click(function () {
        $('#view-student-report-div').hide();
        $('#initial_box').hide();
        $('#choose_games').hide();
        $('#student-report-input').hide();
        $('#settings_box').show();
        on_which_config_page_now = '1'; // as we now go to 1st page of config
    });
    $('#setup_class_timer_go').click(function () {
        $('#timer_modal').removeClass("modal").addClass("modal is-active");
    });
    $('#play_games_go').click(function () {
        $('#intro_screen').hide(1000);
        $('#choose_games').show(1200);
        $('#student-report-input').hide();
        $('#view-student-report-div').hide();
    });
    $('#view_ss_report_go').click(function () {
        // todo:
    });


    // slideshow

    let _index = 0;
    let _slides = [
        "https://png.pngtree.com/thumb_back/fw800/back_our/20190621/ourmid/pngtree-lively-cute-kindergarten-graduation-ceremony-board-poster-background-image_194026.jpg",
        "https://wallpapercave.com/wp/wp2346070.png",
        "https://images-na.ssl-images-amazon.com/images/I/81Zn5sySLLL.png"
    ];

    let _height = Math.ceil($(document).height() * 0.47);
    $('#slide-image').attr('src', _slides[_index % 3]).css('height', `${_height}`);
    _index++;
    let slide_0 = $('#slide-0');
    let slide_1 = $('#slide-1');
    let slide_2 = $('#slide-2');
    // $('#slide_image').css('height',`${_height}`);
    // todo: on slide with cursor

    function update_indicator_color(_i){
        if (_i === 0) {
                slide_0.css('color', 'gold');
                slide_1.css('color', 'grey');
                slide_2.css('color', 'grey');
            } else if (_i === 1) {
                slide_0.css('color', 'grey');
                slide_1.css('color', 'gold');
                slide_2.css('color', 'grey');
            } else {
                slide_0.css('color', 'grey');
                slide_1.css('color', 'grey');
                slide_2.css('color', 'gold');
            }
    }

    setInterval(
        function () {
            const __i = _index % 3;
            $('#slide-image').attr('src', _slides[__i]); //.css('height', `${_height}`);
            _index++;
            update_indicator_color(__i);
        }, 2500);

    slide_0.click(function () {
        $('#slide-image').attr('src', _slides[0]);
        update_indicator_color(0);
    });
    slide_1.click(function () {
        $('#slide-image').attr('src', _slides[1]);
        update_indicator_color(1);
    });
    slide_2.click(function () {
        $('#slide-image').attr('src', _slides[2]);
        update_indicator_color(2);
    });


    // GAMES <<<<
    socket.on('switch_to_games_emit', function (data) {
        // let initial = data['is_initial'];
        $('#intro_screen').hide(1000);
        $('#choose_games').show(1200);
        $('#student-report-input').hide();
        $('#view-student-report-div').hide();
    });

    let current_grade = null; // if null even after clicked the games, then show error to select grade
    socket.on('grade_lesson_update_trigger', function (data) {
        current_grade = `${data['grade']}`; // string type
    });
    // on click games
    // todo: on click games => we need to check if the lesson and grade for flashcards are selected or not.
    $('#game_1').click(function () {
        if (current_grade === null || current_grade.length === 0)
            show_notifications(false, "Please Select Grade and Lesson for Flashcard");
        else {
            $('#initial_box').hide(1000);
            $('#tik_tak_toe').show(1200);
        }
    });


    $('#game_2').click(function () {
        if (current_grade === null || current_grade.length === 0)
            show_notifications(false, "Please Select Grade and Lesson for Flashcard");
        else {
            $('#initial_box').hide(1000);
            $('#match_game').show(1200);
        }

    });

    $('#game_3').click(function () {
        if (current_grade === null || current_grade.length === 0)
            show_notifications(false, "Please Select Grade and Lesson for Flashcard");
        else {
            $('#initial_box').hide(1000);
            $('#find_game').show(1200);
        }
    });
    // this click function is inlined in window2.html
    // $('#game_4').click(function () {
    //     if (current_grade === null || current_grade.length === 0)
    //         show_notifications("Please Select Grade and Lesson for Flashcard");
    //     else {
    //         $('#initial_box').hide(1000);
    //         $('#listen_game').show(1200);
    //         socket.emit('game_4_initialize', {'': ''}); // special
    //     }
    // });


    // back funcs

    // first game
    $('#new_game_from_game_1').click(function () {
        $('#tik_tak_toe').hide(1000);
        $('#intro_screen').hide(); // <<<<<<<<< todo: change this to if a pdf/ppt is already selected
        $('#choose_games').show();
        $('#initial_box').show(1200);
    });
    $('#back_to_lesson_from_game_1').click(function () {
        // todo: enable all drawing related buttons and all in window and in other windows....
        $('#tik_tak_toe').hide(1000);
        $('#intro_screen').show(); // <<<<<<<<< todo: change this to if a pdf/ppt is already selected
        $('#choose_games').hide();
        $('#initial_box').show(1200);
        socket.emit('refresh_grades_as_per_docs', {});
        // we need to clear the game instance ...
        reset_game("none");
    });

    // second game
    $('#new_game_from_game_2').click(function () {
        $('#match_game').hide(1000);
        $('#intro_screen').hide(); // <<<<<<<<< todo: change this to if a pdf/ppt is already selected
        $('#choose_games').show();
        $('#initial_box').show(1200);
    });
    $('#back_to_lesson_from_game_2').click(function () {
        $('#match_game').hide(1000);
        $('#intro_screen').show(); // <<<<<<<<< todo: change this to if a pdf/ppt is already selected
        $('#choose_games').hide();
        $('#initial_box').show(1200);
        socket.emit('refresh_grades_as_per_docs', {});
    });

    // third game
    $('#new_game_from_game_3').click(function () {
        $('#find_game').hide(1000);
        $('#intro_screen').hide();
        $('#choose_games').show();
        $('#initial_box').show(1200);
        // we have to clear the timer and put it in initial position
        reset_the_game(false);
    });
    $('#back_to_lesson_from_game_3').click(function () {
        $('#find_game').hide(1000);
        $('#intro_screen').show();
        $('#choose_games').hide();
        $('#initial_box').show(1200);
        socket.emit('refresh_grades_as_per_docs', {});
        // we have to clear the timer
        // we have to clear the timer and put it in initial position
        reset_the_game(false);
    });

    // fourth game
    $('#new_game_from_game_4').click(function () {
        $('#listen_game').hide(1000);
        $('#intro_screen').hide();
        $('#choose_games').show();
        $('#initial_box').show(1200);

    });
    $('#back_to_lesson_from_game_4').click(function () {
        $('#listen_game').hide(1000);
        $('#intro_screen').show();
        $('#choose_games').hide();
        $('#initial_box').show(1200);
        socket.emit('refresh_grades_as_per_docs', {});
    });


    // show the selected student's data (name, star, diamond and etc.)
    // global variables
    let STUDENT_ID = null; // this is needed when sending signal to update star count in server

    // this variable is dependent on the K/A socket emit
    let k_or_a = "K";
    let current_student_data = null;


    socket.on('select_student_signal_receive', function (data) {
        current_student_data = data;
        update_student_bar();
    });

    function update_student_bar() {
        let data = current_student_data;
        // alert(k_or_a);
        // data -> {'name': 'Alex', 'star': 0, 'diamond': 0, 'id': 'this is needed to send signal to server to add stars'}

        // &nbsp; for space at right
        $('#student_name_div').empty().append("<h5 class=\"title is-5\" id=\"student_name\">" + `${data['name']}` + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</h5>");
        // star update
        let left_stars = parseInt(data['star']) % 10;// as there are 10 stars each, so current sprint progress
        if (left_stars == null)
            left_stars = 0;
        for (let i = 0; i < left_stars; i++) {
            $(`#star_count_${i}`).css('color', k_or_a === "K" ? 'gold' : 'green'); // update the style -> make the color gold
            document.getElementById(`star_count_${i}`).className = k_or_a === "K" ? "fa fa-star" : "fa fa-check";
        }
        // clear the styles afters
        for (let i = left_stars; i < 10; i++) { // as 0  index so for 10 items 0...9
            $(`#star_count_${i}`).css('color', '');
            document.getElementById(`star_count_${i}`).className = k_or_a === "K" ? "fa fa-star" : "fa fa-check";
        }
        // total
        $('#star_count').text(data['star'].toString());
        $('#diamond_count').text(data['diamond'].toString());
        if (k_or_a === "K") {
            document.getElementById("star_icon").className = "fa fa-star";
            $('#diamond_count_div').css({'visibility': 'visible', 'margin-left': '12px'});
            $('#star_icon').css({'font-size': '24px', 'color': 'gold'});
        } else {
            $('#diamond_count_div').css({'visibility': 'hidden', 'margin-left': '12px'});
            document.getElementById("star_icon").className = "fas fa-check";
            $('#star_icon').css({'font-size': '24px', 'color': 'green'});
        }
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
    }

    // animation trigger receive from window 3

    // dice animation preset
    let dice_color = $("#dice-color");
    let dot_color = $("#dot-color");
    dice_color.val("#323131");
    dot_color.val("#ffd700");
    let rnd;
    let x, y;
    dot_color.change(function () {
        const dot = $("#dot-color").val();
        $(".dot").css("background-color", dot);
    });
    dice_color.change(function () {
        const dice = $("#dice-color").val();
        $(".side").css("background-color", dice);
    });

    // actual trigger functions
    socket.on('animation_trigger_emit_to_win2', function (data) {
        let animation_type = data['animation_type'];
        //   console.log("animation type from window2.js is " + animation_type);
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
            document.getElementById('play_dice_sound').click();
        } else if (animation_type === "toss") {
            $('#toss_animation_div').show(1).delay(5000).hide(1);

            var flipResult = Math.random();
            $('#coin').removeClass();
            setTimeout(function () {
                if (flipResult <= 0.5) {
                    $('#coin').addClass('heads');
                } else {
                    $('#coin').addClass('tails');
                }
            }, 100);

        }

    });


    // K_A
    // todo: implement dynamic change here..... already selected and then when you choose K/A then update it..
    socket.on('k_a_emit_signal', function (data) {
        k_or_a = data['k_or_a'];
        update_student_bar();
    });


    let should_stop = false;

    // time trigger receive from window 3
    socket.on('timer_trigger_emit_to_win2', function (data) {
        let timer_data = data['timer_data'];
        // can be actually none or it can send to change the time (from settings of timer)
        if (timer_data === "None") {
            // pop up the modal to set up (timer data none means => pop up settings)
            $('#timer_modal').removeClass("modal").addClass("modal is-active");
        } else {
            console.log(data['start_or_end']);
            if (data['start_or_end'].toLowerCase() === 'end') {
                should_stop = true;
                // todo: show the student report card
            } else {
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
                    if (distance <= 0 || should_stop) {
                        clearInterval(x);
                        document.getElementById("time_count").innerHTML = "00:00";
                        // todo: show the student report card
                        $('#initial_box').hide();
                        $('#choose_games').hide();
                        $('#settings_box').hide();
                        $('#iframe-container').hide();
                        $('#loading_box').hide();
                        $('#student-report-input').show();
                        // here we need to send a trigger to window 3 that it ends...
                        // so that the button in window3 can have a the text "Start
                        socket.emit("timer_is_finished_trigger_9", {});
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


    // time trigger of screenshot
    socket.on('open_screenshot_timer_settings', function (data) {
        let timer_data = data['seconds'];
        // update  the value in the show text and input field
        $('#time-interval').text(timer_data + " seconds");
        $('#interval-seconds').val(timer_data.toString());
        $('#screenshot-timer-modal').removeClass("modal").addClass("modal is-active");
    });

    $('#save-interval-time').click(function () {
        $.ajax({
            url: "/save_time_interval_of_screenshot",
            type: "POST",
            data: {
                "seconds": $('#interval-seconds').val()
            }
        }).done(function (data) {
            if (data["status"] === 1) {
                $('#screenshot-timer-modal').removeClass("modal is-active").addClass("modal");
            } else {
                // todo: show error something
                show_notifications(false, "Error happened");
            }
        });
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



