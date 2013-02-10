/*
** Script to toggle all of the selection boxes in a tables2 table.
** Based on an approach by Adrian J. Moreno, as described in this article:
** http://iknowkungfoo.com/blog/index.cfm/2008/7/9/Check-All-Checkboxes-with-JQuery
*/
function toggle_checkboxes(id, cls) {
  $("." + cls + ":checkbox").attr('checked', $('#' + id).is(':checked'));
}
