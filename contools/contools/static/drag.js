// This file is part of Streampunk, a Django application for convention programmes
// Copyright (C) 2014 Stephen Kilbane
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


// We have two objects listing our dimensions. They're like this
// so we can iterate over them with "var x in things".
var rooms = { 'main': 1, 'prog1': 1, 'prog2':1 };
var slots = { '2pm': 1, '3pm': 1, '4pm': 1, '5pm':1 };

// Our main item table. It's an object keyed by item id. It's important
// that the room and slot fields match the values in the dimension
// objects.

var items = {
  123: { title: "Opening ceremony", room: "main", slot: "2pm" },
  456: { title: "Filk concert", room: "prog1", slot: "2pm" },
  789: { title: "Streampunk demo", room: "main", slot: "3pm" },
  111: { title: "Duelling", room: "prog2", slot: "3pm" },
  222: { title: "Hanggliding", room: "main", slot: "4pm" },
  333: { title: "Fire breathing", room: "prog1", slot: "4pm" },
  444: { title: "Cabaret", room: "prog2", slot: "4pm" },
  555: { title: "Closing ceremony", room: "main", slot: "5pm" },
};

// Something for messing around with, to see how redraws work.
var moves = [
  { iid: 456, title: "Filk concert", room: "prog2", slot: "5pm" },
  { iid: 789, title: "Streampunk workshop", room: "main", slot: "3pm" },
  { iid: 111, title: "Duelling", room: "prog1", slot: "3pm" },
  { iid: 222, title: "Hanggliding", room: "main", slot: "2pm" },
  { iid: 333, title: "Fire making", room: "prog1", slot: "5pm" },
];

var movecount = 0;

// When invoked, this makes a change to the drawn table, and to
// the item list, according to the changes in moves[].
function clobber_item() {
  var move = moves[movecount++];
  var iid = move.iid;
  // We've deliberately created a <div> that uses the item's id as
  // its id, so we can have jQuery delete that div directly.
  $("#"+iid).remove();

  // Update the item so that it'll be different next time we draw
  // the table.
  items[iid].title = move.title;
  items[iid].room = move.room;
  items[iid].slot = move.slot;
}


// Populate the top row of the table with headings for the X dimension.
function mkheaders(things) {
  var row = $('<tr></tr>');
  row.append("<th></th>");
  for (var i in things) {
    row.append('<th>' + i + '</th>');
  }
  return row;
}

// Create a row at position Y in the table.
// keyfn will return a key for each <td> in the row. That key is based
// on the combined X and Y dimensions. It's important that the key is
// the same, regardless of whether we're doing X x Y or Y x X, so that
// we can access the cell in one go.

function mkrow(keyfn, y, xs) {
  var row = $('<tr><th>' + y + '</th></tr>');
  for (var x in xs) {
    var key = keyfn(y, x);
    var cell = $('<td id=' + key + ' class="dropTarget"></td>');
    row.append(cell);
    // We just create the cell as empty, at this point.
  }
  return row;
}

// Draw the table, using the Y dimension and the X dimension.
// keyfn is a function for combining the two coords to give the id
// of the cell.
function mktable(keyfn, ys, xs) {
  // Delete the table, if it's previously been drawn.
  zap_table();

  // We use 'item_table' for the table itself, separate from
  // the div which will contain the table, so that we can delete
  // the table, but not the div in which it lives.
  var t = $('<table border="1" id="item_table"></table>');
  t.append(mkheaders(xs));
  for (var y in ys) {
    t.append(mkrow(keyfn, y, xs));
  }
  // Once we've assembled the table, insert it into the page at
  // the planned location.
  $("#tableloc").append(t);
}

function zap_table() {
  // Delete the table, if it exists, but leave its div intact.
  $("#item_table").remove();
}

// Populate the table, using the items.
// Keyfn will combine the room and slot fields into the id of
// the cell to contain them.
function filltable(keyfn) {
  for (var iid in items) {
    var item = items[iid];
    var room = item.room;
    var slot = item.slot;
    var key = keyfn(room, slot);
    // Create a new div for each item, using the item's id as the
    // id of the div. It's possible for several items to be in the
    // same cell, so each gets its own div. Later, we want to be able
    // to delete just one item's div without affecting the others in
    // the same cell.
    var div = $('<div id=' + iid + ' class="draggable">' + item.title + '</div>');
    $('#'+key).append(div);
  }
}

// One version of the key function, for Y x X tables.
function normkey(x, y) {
  return x + '_' + y;
}

// Another version of the key function, for X x Y tables.
function swapkey(x, y) {
  return normkey(y, x);
}

// Give a key, return a room/slot object.
function splitkey(key) {
  var bits = key.split('_');
  return { room: bits[0], slot: bits[1] };
}

function roomxslot_table() {
  mktable(normkey, rooms, slots);
  filltable(normkey);
  setup_dragging();
}

function slotxroom_table() {
  mktable(swapkey, slots, rooms);
  filltable(normkey);
  setup_dragging();
}

function setup_dragging() {
  // Allow each of the divs to be draggable.
  $(".draggable").draggable({
    // Make sure dragged things are at front.
    zIndex: 1,
    // Return to its location, if cancelled.
    revert: true,
    // Mark differently, while being dragged.
    start: function(event, ui) {
      ui.helper.addClass("beingDragged");
    },
    stop: function(event, ui) {
      ui.helper.removeClass("beingDragged");
    }
  });

  // Make each of the cells a target for the
  // div being dragged.
  $(".dropTarget").droppable({
    hoverClass: "droppable",
    drop: function(event, ui) {
      var draggeddiv = ui.draggable;
      var targettd = $(event.target);
      // We can append the moved item directly to
      // the new location in the drawn table...
      targettd.append(draggeddiv);
      // but that'll be lost when we re-draw it, so
      // we also need to modify the source table.
      var targetid = targettd.attr("id");
      var room_and_slot = splitkey(targetid);
      var iid = draggeddiv.attr("id");
      items[iid].room = room_and_slot.room;
      items[iid].slot = room_and_slot.slot;
    }
  });
}


$(document).ready(
  function() {
    // Populate our table
    roomxslot_table();

  }
);
