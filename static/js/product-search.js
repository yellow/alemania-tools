$(document).ready(function() {
    $('form').submit(function (e) {
	var url = product_search_url; // send the form data here.
	$.ajax({
	    type: "POST",
	    url: url,
	    data: $('form').serialize(), // serializes the form's elements.
	    success: function (data) {
		// console.log(data)  // display the returned data in the console.
		results_div = document.getElementById('results')
		results_div.innerHTML = data
	    }
	});
	e.preventDefault(); // block the traditional submission of the form.
    });

    // Inject our CSRF token into our AJAX request.
    $.ajaxSetup({
	beforeSend: function(xhr, settings) {
	    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
		xhr.setRequestHeader("X-CSRFToken", csrf_token)
	    }
	}
    })
});
