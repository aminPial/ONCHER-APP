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

// add button onclick
$('#add_button').click(function () {

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

        } else {

        }
    });
});