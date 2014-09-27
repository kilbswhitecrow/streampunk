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
// var rooms = { 'main': 1, 'prog1': 1, 'prog2':1 };
// var slots = { '2pm': 1, '3pm': 1, '4pm': 1, '5pm':1 };

// Our main item table. It's an object keyed by item id. It's important
// that the room and slot fields match the values in the dimension
// objects.

// var items = {
//   123: { title: "Opening ceremony", room: "main", slot: "2pm", url: "/streampunk/streampunk/item/123/" },
//   456: { title: "Filk concert", room: "prog1", slot: "2pm", url: "/streampunk/streampunk/item/456/" },
//   789: { title: "Streampunk demo", room: "main", slot: "3pm", url: "/streampunk/streampunk/item/789/" },
//   111: { title: "Duelling", room: "prog2", slot: "3pm", url: "/streampunk/streampunk/item/111/" },
//   222: { title: "Hanggliding", room: "main", slot: "4pm", url: "/streampunk/streampunk/item/222/" },
//   333: { title: "Fire breathing", room: "prog1", slot: "4pm", url: "/streampunk/streampunk/item/333/" },
//   444: { title: "Cabaret", room: "prog2", slot: "4pm", url: "/streampunk/streampunk/item/444/" },
//   555: { title: "Closing ceremony", room: "main", slot: "5pm", url: "/streampunk/streampunk/item/555/" },
// };

// Links defined in the grid HTML template:

// var grid_info_url = "/streampunk/api/grid/<pk>/";
// var room_info_url = "/streampunk/api/rooms/";

// Empty tables for populating.

var items = { };
var rooms = { };
var roomids = { };
var slots = { };
var slotids = { };
var slotsarr = [];  // Only needed while this is static data.
var keymap = { };

// STATIC DATA IN THE NEW FORMAT. THIS WILL BE RETRIEVED DYNAMICALLY.

var gridinfo = {
//     "slots": [
//         {
//             "id": 76, 
//             "start": 1080, 
//             "length": 22, 
//             "day": 1, 
//             "startText": "6pm", 
//             "slotText": "6-7pm", 
//             "visible": true, 
//             "isDefault": false, 
//             "isUndefined": false, 
//             "order": 118
//         }, 
//         {
//             "id": 77, 
//             "start": 1140, 
//             "length": 22, 
//             "day": 1, 
//             "startText": "7pm", 
//             "slotText": "7-8pm", 
//             "visible": true, 
//             "isDefault": false, 
//             "isUndefined": false, 
//             "order": 119
//         }, 
//         {
//             "id": 78, 
//             "start": 1200, 
//             "length": 22, 
//             "day": 1, 
//             "startText": "8pm", 
//             "slotText": "8-9pm", 
//             "visible": true, 
//             "isDefault": false, 
//             "isUndefined": false, 
//             "order": 120
//         }, 
//         {
//             "id": 79, 
//             "start": 1260, 
//             "length": 22, 
//             "day": 1, 
//             "startText": "9pm", 
//             "slotText": "9-10pm", 
//             "visible": true, 
//             "isDefault": false, 
//             "isUndefined": false, 
//             "order": 121
//         }
//     ], 
//     "items": [
//         {
//             "id": 1, 
//             "title": "Opening Ceremony", 
//             "room": 5, 
//             "start": 78, 
//             "length": 22, 
//             "slots": [
//                 {
//                     "id": 78, 
//                     "start": 1200, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "8pm", 
//                     "slotText": "8-9pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 120
//                 }
//             ], 
//             "people": [
//                 {
//                     "id": 6, 
//                     "name": "Deria Book"
//                 }, 
//                 {
//                     "id": 3, 
//                     "name": "Jayne Cobb"
//                 }
//             ]
//         }, 
//         {
//             "id": 2, 
//             "title": "Closing Ceremony", 
//             "room": 8, 
//             "start": 78, 
//             "length": 21, 
//             "slots": [
//                 {
//                     "id": 78, 
//                     "start": 1200, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "8pm", 
//                     "slotText": "8-9pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 120
//                 }
//             ], 
//             "people": [
//                 {
//                     "id": 6, 
//                     "name": "Deria Book"
//                 }, 
//                 {
//                     "id": 3, 
//                     "name": "Jayne Cobb"
//                 }
//             ]
//         }, 
//         {
//             "id": 3, 
//             "title": "Bid Session", 
//             "room": 7, 
//             "start": 76, 
//             "length": 22, 
//             "slots": [
//                 {
//                     "id": 76, 
//                     "start": 1080, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "6pm", 
//                     "slotText": "6-7pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 118
//                 }
//             ], 
//             "people": []
//         }, 
//         {
//             "id": 4, 
//             "title": "Art Auction", 
//             "room": 6, 
//             "start": 76, 
//             "length": 24, 
//             "slots": [
//                 {
//                     "id": 76, 
//                     "start": 1080, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "6pm", 
//                     "slotText": "6-7pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 118
//                 }, 
//                 {
//                     "id": 77, 
//                     "start": 1140, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "7pm", 
//                     "slotText": "7-8pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 119
//                 }
//             ], 
//             "people": [
//                 {
//                     "id": 10, 
//                     "name": "Ripper"
//                 }, 
//                 {
//                     "id": 2, 
//                     "name": "Malcolm Reynolds"
//                 }
//             ]
//         }, 
//         {
//             "id": 5, 
//             "title": "Masquerade and Cabaret", 
//             "room": 9, 
//             "start": 78, 
//             "length": 24, 
//             "slots": [
//                 {
//                     "id": 78, 
//                     "start": 1200, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "8pm", 
//                     "slotText": "8-9pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 120
//                 }, 
//                 {
//                     "id": 79, 
//                     "start": 1260, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "9pm", 
//                     "slotText": "9-10pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 121
//                 }
//             ], 
//             "people": [
//                 {
//                     "id": 10, 
//                     "name": "Ripper"
//                 }
//             ]
//         }, 
//         {
//             "id": 6, 
//             "title": "Disco", 
//             "room": 9, 
//             "start": 76, 
//             "length": 24, 
//             "slots": [
//                 {
//                     "id": 76, 
//                     "start": 1080, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "6pm", 
//                     "slotText": "6-7pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 118
//                 }, 
//                 {
//                     "id": 77, 
//                     "start": 1140, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "7pm", 
//                     "slotText": "7-8pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 119
//                 }
//             ], 
//             "people": [
//                 {
//                     "id": 8, 
//                     "name": "Buffy Summers"
//                 }, 
//                 {
//                     "id": 11, 
//                     "name": "The Key"
//                 }, 
//                 {
//                     "id": 5, 
//                     "name": "River Tam"
//                 }
//             ]
//         }, 
//         {
//             "id": 8, 
//             "title": "Tolkien: All you need?", 
//             "room": 6, 
//             "start": 78, 
//             "length": 22, 
//             "slots": [
//                 {
//                     "id": 78, 
//                     "start": 1200, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "8pm", 
//                     "slotText": "8-9pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 120
//                 }
//             ], 
//             "people": [
//                 {
//                     "id": 10, 
//                     "name": "Ripper"
//                 }
//             ]
//         }, 
//         {
//             "id": 9, 
//             "title": "Are all cons rubbish these days, or what?", 
//             "room": 5, 
//             "start": 76, 
//             "length": 22, 
//             "slots": [
//                 {
//                     "id": 76, 
//                     "start": 1080, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "6pm", 
//                     "slotText": "6-7pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 118
//                 }
//             ], 
//             "people": []
//         }, 
//         {
//             "id": 10, 
//             "title": "Interview with Shepherd Book", 
//             "room": 5, 
//             "start": 77, 
//             "length": 22, 
//             "slots": [
//                 {
//                     "id": 77, 
//                     "start": 1140, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "7pm", 
//                     "slotText": "7-8pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 119
//                 }
//             ], 
//             "people": []
//         }, 
//         {
//             "id": 11, 
//             "title": "Jayne Cobb in Conversation", 
//             "room": 7, 
//             "start": 78, 
//             "length": 22, 
//             "slots": [
//                 {
//                     "id": 78, 
//                     "start": 1200, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "8pm", 
//                     "slotText": "8-9pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 120
//                 }
//             ], 
//             "people": []
//         }, 
//         {
//             "id": 12, 
//             "title": "First Timers (Friday)", 
//             "room": 8, 
//             "start": 77, 
//             "length": 21, 
//             "slots": [
//                 {
//                     "id": 77, 
//                     "start": 1140, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "7pm", 
//                     "slotText": "7-8pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 119
//                 }
//             ], 
//             "people": []
//         }, 
//         {
//             "id": 13, 
//             "title": "First Timers (Saturday)", 
//             "room": 7, 
//             "start": 77, 
//             "length": 21, 
//             "slots": [
//                 {
//                     "id": 77, 
//                     "start": 1140, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "7pm", 
//                     "slotText": "7-8pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 119
//                 }
//             ], 
//             "people": []
//         }, 
//         {
//             "id": 14, 
//             "title": "Stewards' Briefing (Friday)", 
//             "room": 8, 
//             "start": 77, 
//             "length": 21, 
//             "slots": [
//                 {
//                     "id": 77, 
//                     "start": 1140, 
//                     "length": 22, 
//                     "day": 1, 
//                     "startText": "7pm", 
//                     "slotText": "7-8pm", 
//                     "visible": true, 
//                     "isDefault": false, 
//                     "isUndefined": false, 
//                     "order": 119
//                 }
//             ], 
//             "people": []
//         }
//     ], 
//     "id": 7, 
//     "name": "Friday 6-10pm", 
//     "gridOrder": 3
};

var roominfo = [
//     {
//         "id": 5, 
//         "name": "Main Hall"
//     }, 
//     {
//         "id": 6, 
//         "name": "Second Hall"
//     }, 
//     {
//         "id": 7, 
//         "name": "Programme 1"
//     }, 
//     {
//         "id": 8, 
//         "name": "Programme 2"
//     }, 
//     {
//         "id": 9, 
//         "name": "Video"
//     }, 
//     {
//         "id": 10, 
//         "name": "Ops"
//     }, 
//     {
//         "id": 4, 
//         "name": "Everywhere"
//     }, 
//     {
//         "id": 3, 
//         "name": "Nowhere"
//     }
];

// We've moved the item to start at the specified slot. The
// item occupies the number of slots given, so return an array
// which contains all the slots that the item now occupies. For
// a real system, we'd be doing an AJAX post to modify the item's
// start, and would get back an updated item in response, so it
// doesn't matter that this is buggy, in that it can only return
// the slots that are in this grid: if we have an item that uses
// multiple slots, and we move it to the end of the grid, then it'll
// get truncated to be a shorter item.
function newslots(slot, numslots) {
  var ix = slotsarr.indexOf(slot);
  return slotsarr.slice(ix, ix+numslots);
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

  lastkeyfn = keyfn;

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

// Given an item, return the contents of the item's cell.
function cellcontent(item) {
  var content = '<a href="' +
                item.url +
                '">' +
                item.title +
                '</a>';
  for (var i = 0; i < item.people.length; i++) {
    var person = item.people[i];
    content += '<br />' +
               '<a href="' +
               person.url +
               '">' +
               person.name +
               '</a>';
  }
  return content;
}

// Remove a given item from the drawn table, because we're going
// to place it somewhere else.
function unplaceitem(iid) {
  var cls = itemclass(iid);
  $("." + cls).remove();
}

// Populate the table, using the items.
// Keyfn will combine the room and slot fields into the id of
// the cell to contain them.
function placeitem(iid) {
  var item = items[iid];
  var room = item.room;
  for (var slotnum in item.slots) {
    var slot = item.slots[slotnum];
    // The item can cover several slots, and they might not be slots
    // that are in this grid.
    if (slots[slot]) {
      var key = normkey(room, slot);
      var divid = itemid(iid, slot);
      var cls = itemclass(iid);
      // Create a new div for this item. We can have several items
      // appearing in the same cell, and we can have an item that
      // spans several cells. We want to be able to remove all the
      // divs that correspond to one item, without affecting the
      // divs that correspond to other items, so:
      // - The div gets a class based on the item (so all divs for
      //   the item have the same class).
      // - The div gets an id that corresponds to the item and slot.
      var div = $('<div id=' +
                  divid +
                  ' class="' +
                  cls +
                  ' draggable">' +
                  cellcontent(item) +
                  '</div>');
      $(div).draggable(draggable_config);
      $('#'+key).append(div);
    }
  }
}

function filltable(keyfn) {
  for (var iid in items) {
    placeitem(iid);
  }
}

// One version of the key function, for Y x X tables.
function normkey(x, y) {
  return keymap[x] + '_' + keymap[y];
}

// Another version of the key function, for X x Y tables.
function swapkey(x, y) {
  return normkey(y, x);
}

// Give a key, return a room/slot object.
function splitkey(key) {
  var bits = key.split('_');
  return { room: keymap[bits[0]], slot: keymap[bits[1]] };
}

// Get an id for a given item's div, using the item id and the slot.
function itemid(item, slot) {
  return item + '@' + keymap[slot];
}

// Break an itemid into the iid and slot, again.
function split_itemid(item_id) {
  var bits = item_id.split('@');
  return { iid: bits[0], slot: keymap[bits[1]] };
}

// Get a class for an item's div, using the item id.
function itemclass(item) {
  return 'item' + item;
}

var lastkeyfn = normkey;

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

// We've dragged an item to a new location, so update its state to
// reflect that.
function moveitem(iid, room, slot) {
  items[iid].room = room;
  items[iid].slots = newslots(slot, items[iid].slots.length);
}

var draggable_config = {
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
};

var droppable_config = {
    hoverClass: "droppable",
    drop: function(event, ui) {
      var draggeddiv = ui.draggable;
      var targettd = $(event.target);
      // We can append the moved item directly to
      // the new location in the drawn table,
      // but that'll be lost when we re-draw it, so
      // we also need to modify the source table.
      var targetid = targettd.attr("id");
      var room_and_slot = splitkey(targetid);
      var item_id = draggeddiv.attr("id");
      var iid_and_slot = split_itemid(item_id);
      var iid = iid_and_slot.iid;

      unplaceitem(iid);
      moveitem(iid, room_and_slot.room, room_and_slot.slot);
      placeitem(iid);
    }
};

function setup_dragging() {
  // Allow each of the divs to be draggable.
  $(".draggable").draggable(draggable_config);

  // Make each of the cells a target for the
  // div being dragged.
  $(".dropTarget").droppable(droppable_config);
}

function mkkeymap(thing) {
  var spaceless = thing.replace(" ", "-");
  keymap[thing] = spaceless;
  keymap[spaceless] = thing;
}

function mkslots() {
  for (var i = 0; i < gridinfo["slots"].length; i++) {
    var id = gridinfo["slots"][i].id;
    var startText = gridinfo["slots"][i].startText;
    slots[startText] = id;
    slotids[id] = startText;
    slotsarr.push(startText);  // Only needed while this is static data.
    mkkeymap(startText);
  }
}

function mkrooms() {
  for (var i = 0; i < roominfo.length; i++) {
    var id = roominfo[i].id;
    var name = roominfo[i].name;
    rooms[name] = id;
    roomids[id] = name;
    mkkeymap(name);
  }
}

function mkitem(item) {
  var id = item.id;
  var title = item.title;
  var room = roomids[item.room];
  // Should come from the Serializer, not be computed.
  var url = "/streampunk/streampunk/item/" + id + "/";
  var islots = [];
  for (var i = 0; i < item.slots.length; i++) {
    islots.push(item.slots[i].startText);
  }
  var people = [];
  for (var i = 0; i < item.people.length; i++) {
    var person = item.people[i];
    person['url'] = "/streampunk/streampunk/person/" + person.id + "/";
    people.push(person);
  }
  items[id] = { "title": title, "room": room, "slots": islots, "url": url, "people": people };
}

function mkitems() {
  for (var i = 0; i < gridinfo["items"].length; i++) {
    mkitem(gridinfo["items"][i]);
  }
}

// Steps (c) and (d)
function allinfofetched() {
  // Create shorthand arrays
  mkrooms();
  mkslots();
  mkitems();
  // Populate our table
  roomxslot_table();
}

// Step (b) part II - invoked when the grid info is received.
// Kick off Step (c)
function setgridinfo(data) {
  gridinfo = data;
  allinfofetched();
}

// Step (a) part II - invoked when the room info is received.
// Step (b) part I - fetch grid info.
function setroominfo(data) {
  // Save the retrieved info
  roominfo = data;
  // Now ask for the grid info
  $.getJSON(grid_info_url, "", setgridinfo);
}

// Step (a) part I - fetch the room info.
function fetchrooms() {
  $.getJSON(room_info_url, "", setroominfo);
}

$(document).ready(
  function() {
    // Retrieve dynamic info
    // Logically, our sequence is:
    // (a) Fetch room info
    // (b) Fetch grid info
    // (c) Create shorthand arrays
    // (d) Build table
    // Because we're waiting on separate Ajax queries, 
    // step (b) is triggered when (a) completes, and steps
    // (c) and (d) are triggered when (b) completes.
    fetchrooms();
  }
);
