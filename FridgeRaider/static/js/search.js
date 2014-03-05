$(document).ready(function(){
   $('.selectpicker').selectpicker();

   $(".remIngred").click(function(){
      tr = $(this).parent().parent();
      tr.toggleClass('danger');
      $(this).toggleClass('glyphicon-repeat');
  });
});

$('#ingredientsForm').submit(function(event) {
   existing = ""
   $('.existing-ingredient').each(function() {
      tr = $(this).parent('tr')
      if ( ! tr.hasClass('danger') ) {
         existing += this.textContent + ",";
      };
   });

   var input = $("<input>")
               .attr("type", "hidden")
               .attr("name", "existing").val(existing);
   $('#ingredientsForm').append($(input));
});

