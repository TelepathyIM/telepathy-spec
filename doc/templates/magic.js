$(document).ready(main);

function main() {
  h5s = $('.rationale h5')

  /* Un-hide the rationale headers */
  h5s.css('display', 'block');

  /* Hide all the rationales... */
  h5s.next().hide();

  /* ...and then make clicking the headers unhide them. */
  h5s.click(function () {
    $(this).next().slideToggle();
  });
}
