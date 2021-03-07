function submitForm() {
    console.log("submit event");
    let fd = new FormData(document.getElementById("fileinfo"));
    fd.append("label", "WEBUPLOAD");
    $.ajax({
        url: "/upload_document",
        type: "POST",
        data: fd,
        processData: false,  // tell jQuery not to process the data
        contentType: false   // tell jQuery not to set contentType
    }).done(function (data) {
    });
    return false;
}

$(document).ready(function () {
    // const socket = io.connect('http://127.0.0.1:5000');
    $('input[type=file]').change(function () {
        submitForm();
    });
});

// student list on select toggle (JS version)
let dropdown = document.querySelector('.dropdown');
dropdown.addEventListener('click', function (event) {
    event.stopPropagation();
    dropdown.classList.toggle('is-active');
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

    $.ajax({
        url: "/add_student",
        type: "POST",
        data: {
            "student_name": student_name,
            "student_age": student_age,
            "gender": $('input[name="sex"]:checked').val()
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