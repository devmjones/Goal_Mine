
var counter = 0;

var remove_subgoal = function(e) {
  $(e.target).closest('li').remove();
};

var insert_subgoal = function() {
  counter++;
  $("input[name=max_counter]").val(counter);

  src = $("li.myinput")[0];
  copy = $(src).clone();
  copy.find('input').attr('name', 'text_'+counter).val("");
  copy.find('select').attr('name', 'type_'+counter);
  copy.find('a').click(remove_subgoal);
  $(src).closest('ol').append(copy);
};

$("button.add").click(insert_subgoal);

//tally data collection
$('.tally button').click(function(evt) {
    counter = $(evt.target).closest('.tally').find('input');
    current_val = parseInt(counter.val());
    counter.val((current_val + 1).toString());
});


//tf buttons
$('.tf .btn').click(function(evt) {
    counter = $(evt.target).closest('.input-group').find('input');
    current_val = parseInt(counter.val());
    counter.val((current_val + 1).toString());
});


///stopwatch
   var stopwatch_interval = null;
      $('#startstop').click(function(e) {
        if($(e.target).text() == 'Start') {
          stopwatch_interval = setInterval(function() {
            i =  parseInt($('input.stopwatch').val())+1;
            $('input.stopwatch').val(i.toString());
            minutes = Math.floor(i/60).toString();
            if(minutes.length == 1) minutes='0'+minutes
            seconds = (i%60).toString();
            if(seconds.length == 1) seconds = '0'+seconds
            $('#stopwatch').text(minutes+':'+seconds);
          }, 1000);
          $('#startstop').text('Stop');
        } else {
          clearInterval(stopwatch_interval);
          $('#startstop').text('Start');
        }
      });

$(function() {

    $('.delete-student').click(function(evt) {
        bootbox.confirm("Are you sure?!", function(result) {
            if(result) {
                var id = $(evt.target).data('student-id');
                window.location = "/student/" + id + "/delete";
            }
        });
    });

});


//$(function() {
//
//    $('.delete-goal').click(function(evt) {
//        bootbox.confirm("Are you sure?!", function(result) {
//            if(result) {
//                var id = $(evt.target).data('goal-id');
//                window.location = "/student/" + id + "/delete";
//            }
//        });
//    });
//
//});