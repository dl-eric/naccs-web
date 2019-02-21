$(document).ready(function(){
    $('.matches').slick({
      infinite: false,
      slidesToShow: 5,
    });
    $('.matches').css({opacity: 0.0, visibility: "visible"}).animate({opacity: 1}, 600);
});