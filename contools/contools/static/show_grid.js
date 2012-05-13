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

