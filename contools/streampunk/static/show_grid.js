// This file is part of Streampunk, a Django application for convention programmes
// Copyright (C) 2012 Stephen Kilbane
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

$(document).ready(
  function() {
    $("#ShowRoomBySlot").click(function() {
       $("#RoomBySlot").css("display", "block");
       $("#SlotByRoom").css("display", "none");
       return false;
    });
    $("#ShowSlotByRoom").click(function() {
       $("#SlotByRoom").css("display", "block");
       $("#RoomBySlot").css("display", "none");
       return false;
    });
    $("#ShowPeeps").click(function() {
       $(".personname").css("display", "inline");
       return false;
    });
    $("#HidePeeps").click(function() {
       $(".personname").css("display", "none");
       return false;
    });
    $("#ShowFill").click(function() {
       $(".FillSlot").css("display", "inline");
       return false;
    });
    $("#HideFill").click(function() {
       $(".FillSlot").css("display", "none");
       return false;
    });
  });

