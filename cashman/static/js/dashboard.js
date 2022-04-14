$(document).ready(function() {

    $('#groupForm').hide();

    $("#grp-add-btn").click(() => {
        $('#groupForm').toggle(500);
    });

    // Attach a submit handler to the form
    $("#groupForm").submit(function (event) {

        // Stop form from submitting normally
        event.preventDefault();

        const form = $(this);
        const formData = {
            name: $("#name").val(),
            description: $("#description").val(),
        };
        // alert(`${JSON.stringify(formData)}`)
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: JSON.stringify(formData),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                // refresh the list
                $('#groupForm').trigger("reset");
                location.reload();
            },
            error: function (error) {
                console.log(JSON.stringify(error));
                alert('Something went wrong from our side. Please try later!');
            }
        });

    });

});