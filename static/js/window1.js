

// on click settings, send signal to window 2
$('#configure').click(function () {
    // let socket = io.connect('/');
    socket.emit('configure_signal_emitter', {});
});


// student list on select toggle (JS version)
// let dropdown = document.querySelector('.dropdown');
// dropdown.addEventListener('click', function (event) {
//     event.stopPropagation();
//     dropdown.classList.toggle('is-active');
// });


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


let is_student_form_active = false;

// add button onclick => add new student
$('#add_button').click(function () {
    if (is_student_form_active) {
        // change the active icon CROSS to ADD
        $('#add_button').empty().append("<i class=\"fas fa-plus\"></i>");
        // show elem
        $('#grade_section').show(200);
        $('#student_notes_text').show(200);
        $('#lesson_plan_section').show(200);
        $('#student_info_section_2').show(200);
        $('#student_info_section_1').show(200);
        $('#file_upload_section').show(200);
        // show elem
        $('#student_add_form').hide(500);
    } else {
        // change the active icon ADD to CROSS
        $('#add_button').empty().append("<i class=\"fa fa-window-close\"></i>");
        // hide elem
        $('#grade_section').hide(200);
        $('#student_notes_text').hide(200);
        $('#lesson_plan_section').hide(200);
        $('#student_info_section_2').hide(200);
        $('#student_info_section_1').hide(200);
        $('#file_upload_section').hide(200);
        // show elem
        $('#student_add_form').show(500);
    }
    is_student_form_active = !is_student_form_active; // reverse it
});

// student data input check on the fly and animate and change colors


// add student data (send an ajax request with the data after checking)
$('#add_student').click(function () {
    let student_name = $('#student_name').val();
    let student_age = $('#student_age').val();
    let student_grade = $('#student_grade').val();

    $.ajax({
        url: "/add_student",
        type: "POST",
        data: {
            "student_name": student_name,
            "student_age": student_age,
            "gender": $('input[name="sex"]:checked').val(),
            'student_grade':student_grade
        }
        // },
        // processData: false,  // tell jQuery not to process the data
        // contentType: false   // tell jQuery not to set contentType
    }).done(function (data) {
        if (data["status"] === 1) {
            // // alert("successfully added");
            //  // change the active icon CROSS to ADD
            //  $('#add_button').empty().append("<i class=\"fas fa-plus\"></i>");
            //  // show elem
            //  $('#grade_section').show(200);
            //  $('#student_notes_text').show(200);
            //  $('#lesson_plan_section').show(200);
            //  $('#student_info_section_2').show(200);
            //  $('#student_info_section_1').show(200);
            //  // show elem
            //  $('#student_add_form').hide(500);
            //  is_student_form_active = !is_student_form_active; // reverse it
            location.href = "/window_1"
        } else {
            alert("failed");
        }
    });
});