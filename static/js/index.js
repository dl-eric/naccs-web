$(document).ready(function(){
    $('.matches').slick({
      infinite: false,
      slidesToShow: 5,
      responsive: [
        {
            breakpoint: 1200,
            settings: {
                slidesToShow: 4,
            }
        },
        {
          breakpoint: 900,
          settings: {
            slidesToShow: 3,
          }
        },
        {
          breakpoint: 700,
          settings: {
            slidesToShow: 2,
          }
        },
        {
            breakpoint: 480,
            settings: {
                slidesToShow: 1,
            }
        }
      ]
    });
    $('.matches').css({opacity: 0.0, visibility: "visible"}).animate({opacity: 1}, 600);
});