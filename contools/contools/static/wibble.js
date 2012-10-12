// Experiment in DajaxICE

function my_js_callback(data) {
  var x = 2;
  var y = 3;
  if (data)
    alert(data.message);
  else
    alert("Oh dear");
}

function fill_para(data) {
  $("#booga").append("WIBBLE:" + data);
  return false;
}

function show_con_name(data) {
  $("#con_name").append(data.con_name);
  return false;
}

function update_page() {
  Dajaxice.streampunk.con_name(show_con_name);
}

$(document).ready(
  function() {
    update_page();
  });

