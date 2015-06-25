var page_loaded_time;
var hint_clicked_time;
var n_buttons;

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
    data = {'answer': value, 'time': time_elapsed, 'hint': !$("#hint_button").is(":visible"), 'hint_time':hint_clicked_time};
    set_data('/_validate', data);
}

function reset_buttons() {
    for (i = 0; i < n_buttons; i++) {
         $("#button" + i).attr("class", "btn");
         document.getElementById("button" + i).disabled = false;
    }
}

function set_data(url, post_data) {
    $("#buttons").hide()
    $.post(url, post_data,
           function(data) {
               if (data.halfway) {
                   window.location.href = '/the_screen_in_between';
               } else if (data.done) {
                   window.location.href = '/preference'
               } else {
                   $("#loadimg").show()
                   n_buttons = data.choices.length;

                   // create the required buttons
                   $("#answers").html("");
                   fmt_string = '<li><button class="btn" id="buttonNUM" onclick="validate_choice(NUM)"></button></li>';
                   for (i = 0; i < n_buttons; ++i) {
                       $("#answers").append(fmt_string.replace(/NUM/g, i));
                       $("#button" + i).html(data.choices[i]);
                   }

                   reset_buttons();

                   $("#question").html(data.question);
                   $("#item").html(data.item);
                   $("#loadimg").hide()
                   $("#hint").html("")
                   $("#hint_button").show()
                   $("#buttons").show()
               }},
               'json');

    hint_clicked_time = 0;
    page_loaded_time = new Date();
}

function validate_freeform() {
    text = $("#freeform-input").val().toLowerCase();
    $("#freeform-input").val("");
    return validate(text);
}

function validate_choice(choice) {
    //disable buttons
    for (i = 0; i < n_buttons; i++) {
         document.getElementById("button" + i ).disabled = true;
    }

    //first validate for button colors
    $.post('/javascript_validate', {},
           function(data) {
                $("#button" + choice).attr("class", "btn_wrong");
                $("#button" + data.correct_id).attr("class", "btn_right");
           },
           'json');
    //real validation after a short moment
    setTimeout(function(){
            text = $("#button" + choice).html();
            validate(text);
        }, 1000);

}

function show_hint() {
    hint_clicked_time = new Date() - page_loaded_time;
    $.post('/giveHint', {},
           function(data) {
                $("#hint").html(data.hint);
           },
           'json');
    $("#hint_button").hide()
}

