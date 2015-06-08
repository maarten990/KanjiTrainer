var page_loaded_time;

$(document).ready(function() {
    $("#freeform-input").keydown(function(event) {
        if (event.keyCode == 13) {
            $("#freeform-button").click();
        }
    });

    $(document).keydown(function(event) {
        switch (event.keyCode) {
            case 49:
                $("#button0").click();
                break;
            case 50:
                $("#button1").click();
                break;
            case 51:
                $("#button2").click();
                break;
            case 52:
                $("#button3").click();
                break;
        }
    });

    set_data('/_initial_data', '');
})

function validate(value) {
    time_elapsed = new Date() - page_loaded_time;
    data = {'answer': value, 'time': time_elapsed};
    set_data('/_validate', data);
}

function set_data(url, post_data) {
    $("#buttons").hide()
    $("#loadimg").show()
    $.post(url, post_data,
           function(data) {
               if (data.end_of_chunk) {
                   window.location.href = '/game_over';
               } else {
                   $("#button0").html(data.choices[0]);
                   $("#button1").html(data.choices[1]);
                   $("#button2").html(data.choices[2]);
                   $("#button3").html(data.choices[3]);
                   $("#question").html(data.question);
                   $("#item").html(data.item);
                   $("#loadimg").hide()
                   $("#buttons").show()
                   $("#hint").html("")
               }},
               'json');

    page_loaded_time = new Date();
}

function validate_freeform() {
    text = $("#freeform-input").val().toLowerCase();
    $("#freeform-input").val("");
    return validate(text);
}

function validate_choice(choice) {
    text = $("#button" + choice).html();
    validate(text);
}

function show_hint() {
    $.post('/giveHint', {},
           function(data) {
                $("#hint").html(data.hint);
           },
           'json');
    $("#hint_button").hide()
}

