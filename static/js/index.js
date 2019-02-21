$(document).ready(function(){
    $('.matches').slick({
      infinite: false,
      slidesToShow: 4,
      responsive: [
        {
            breakpoint: 1000,
            settings: {
                slidesToShow: 3,
            }
        },
        {
          breakpoint: 820,
          settings: {
            slidesToShow: 2,
          }
        },
        {
            breakpoint: 600,
            settings: {
                slidesToShow: 1,
            }
        }
      ]
    });
    $('.matches').css({opacity: 0.0, visibility: "visible"}).animate({opacity: 1}, 600);
});