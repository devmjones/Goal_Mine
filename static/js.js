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

