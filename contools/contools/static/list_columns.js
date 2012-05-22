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
    $(".ShowCol1").click(function() {
       $("#Col1").css("display", "block");
       $("#Col2").css("display", "none");
       $("#Col3").css("display", "none");
       $("#Col4").css("display", "none");
       $("#Col5").css("display", "none");
       return false;
    });
    $(".ShowCol2").click(function() {
       $("#Col1").css("display", "none");
       $("#Col2").css("display", "block");
       $("#Col3").css("display", "none");
       $("#Col4").css("display", "none");
       $("#Col5").css("display", "none");
       return false;
    });
    $(".ShowCol3").click(function() {
       $("#Col1").css("display", "none");
       $("#Col2").css("display", "none");
       $("#Col3").css("display", "block");
       $("#Col4").css("display", "none");
       $("#Col5").css("display", "none");
       return false;
    });
    $(".ShowCol4").click(function() {
       $("#Col1").css("display", "none");
       $("#Col2").css("display", "none");
       $("#Col3").css("display", "none");
       $("#Col4").css("display", "block");
       $("#Col5").css("display", "none");
       return false;
    });
    $(".ShowCol5").click(function() {
       $("#Col1").css("display", "none");
       $("#Col2").css("display", "none");
       $("#Col3").css("display", "none");
       $("#Col4").css("display", "none");
       $("#Col5").css("display", "block");
       return false;
    });
  });

