$("#volume").slider({
  min: 0,
  max: 100,
  value: 0,
  range: "min"
});

$("#time").slider({
  min: 0,
  max: 100,
  value: 0,
  range: "min"
});

$(".ui-slider-handle").mousedown(function() {
  $(this).addClass("handle-scale");
});
$(".ui-slider-handle").mouseup(function() {
  $(this).removeClass("handle-scale");
});

$(".play-button").click(function() {
  if ($(this).hasClass("fa-play-circle")) {
    $(this).removeClass("fa-play-circle");
    $(this).addClass("fa-pause-circle");
  } else {
    $(this).removeClass("fa-pause-circle");
    $(this).addClass("fa-play-circle");
  }
});

$(".favorite").click(function() {
  if (
    $(this)
      .children("i")
      .hasClass("far")
  ) {
    $(this)
      .children("i")
      .removeClass("far");
    $(this)
      .children("i")
      .addClass("fas");
  } else {
    $(this)
      .children("i")
      .addClass("far");
    $(this)
      .children("i")
      .removeClass("fas");
  }
});

$(".option").click(function() {
  $(this).toggleClass("active");
});

$(".arrow").mousedown(function() {
  $(this).addClass("mouse-click");
});
$(".arrow").mouseup(function() {
  $(this).removeClass("mouse-click");
});

$(".menu-icon").click(function() {
  $(".menu").css("height", "100%");
  $(".blur").addClass("active");
});
$(".close-icon").click(function() {
  $(".menu").css("height", "0px");
  $(".blur").removeClass("active");
});

$(".bluetooth-item").click(function() {
  if ($(this).hasClass("active")) {
    $(this).removeClass("active");
  } else {
    $(".bluetooth-item").removeClass("active");
    $(this).addClass("active");
  }
});

$(".fa-bluetooth").click(function() {
  $(".bluetooth").css("height", "100%");
  $(".blur").addClass("active");
});
$(".close-bluetooth").click(function() {
  $(".bluetooth").css("height", "0px");
  $(".blur").removeClass("active");
  if ($(".bluetooth-item").hasClass("active")) {
    $(".fa-bluetooth").addClass("active");
  } else {
    $(".fa-bluetooth").removeClass("active");
  }
});
