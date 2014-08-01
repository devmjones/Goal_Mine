//subgoal fields
var counter = 0; //initializing a counter

var remove_subgoal = function(e) {  //assigning function to remove_subgoal. e is event object because we are using this as an event handler.
  $(e.target).closest('li').remove(); //target is a property of the event object that refers to the element (the a tag) that was the source of the event (clicking)
};                                    //closest is a jquery method that finds the closest element matching the selector for it's argument. Goes up tree

var insert_subgoal = function() { //don't need e because we don't need to refer to it. We don't need to know which field we just added.
  counter++;
  $("input[name=max_counter]").val(counter); //every time value is added to the counter, that number is stored in the max counter. This way it knows when to stop iterating if someone deletes a field.

  src = $("li.myinput")[0]; //an li tag with the class my input. jQuery always returns a list
  copy = $(src).clone();
  copy.find('input').attr('name', 'text_'+counter).val(""); //selecting input tags Find goes down tree
  copy.find('select').attr('name', 'type_'+counter);
  copy.find('a').click(remove_subgoal); //attaches the event handler remove subgoal to that delete link
  $(src).closest('ol').append(copy);
};

$("button.add").click(insert_subgoal);

//tally data collection
$('.tally button').click(function(evt) {
    counter = $(evt.target).closest('.tally').find('input'); //getting the input (a number, thus calling it counter) instead of just the button#}
    current_val = parseInt(counter.val()); //stuff entered into a form is returned as a string, so we have to make it an integer so we can add to it#}
    counter.val((current_val + 1).toString()); //adding to it, then turning it back into a string so the form will take it. May not need#}
});


//tf buttons
$('.tf .btn').click(function(evt) {
    counter = $(evt.target).closest('.input-group').find('input'); //getting the input (a number, thus calling it counter) instead of just the button#}
    current_val = parseInt(counter.val()); //stuff entered into a form is returned as a string, so we have to make it an integer so we can add to it#}
    counter.val((current_val + 1).toString()); //adding to it, then turning it back into a string so the form will take it. May not need#}
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




