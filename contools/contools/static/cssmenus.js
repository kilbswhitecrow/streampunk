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
// Based on the following, then converted to use jQuery:
//   Drop-down menus, based on code from:
//   http://www.cssdrive.com/index.php/examples/exampleitem/css_drop_down_menu/
//   which is Copyright CSS Drive 2004-2010.

$(document).ready(
  function() {
    $("#streampunk_cssdropdown > li").mouseover(function() {
          $(this).addClass("streampunk_main_menu_items over"),
          $(this).removeClass("streampunk_main_menu_items");
        });
    $("#streampunk_cssdropdown > li").mouseout(function() {
          $(this).addClass("streampunk_main_menu_items"),
          $(this).removeClass("streampunk_main_menu_items over");
        });
  });
