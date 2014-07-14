var counter = 0;

var remove_subgoal = function(e) {
  $(e.target).closest('li').remove();
};

var insert_subgoal = function() {
  counter++;

  src = $("li")[0];
  copy = $(src).clone();
  copy.find('input').attr('name', 'text_'+counter);
  copy.find('select').attr('name', 'type_'+counter);
  copy.find('a').click(remove_subgoal);
  $('ol').append(copy);
};

$("button.add").click(insert_subgoal);