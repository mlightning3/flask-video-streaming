var d = new Date();
var today = d.getFullYear().toString() + "-" + (d.getMonth() + 1).toString() + "-" + d.getDate().toString();

$('#add').click(function() {
	url_params = $("#Form").serialize();
	//filename = formvals[0].value;
	filename = $("#Form").serializeArray()[0].value;

	if(filename === ""){
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Filename must not be left empty. </strong></h4>");

	}else{
	$.ajax({
		url: '/database/add',
		data: JSON.stringify(url_params, null, '\t'),
		type: 'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(response) {
			console.log(response);
			$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Picture: " + filename  +" added. </strong></h4>");
			$('#MediaTable').append(
				"<tr>" +
				"<td>" + today + "</td>" +
				"<td><a href=\"/media/" + filename + ".jpg\">" + filename + "</a></td>" +
				"</tr>");
			console.log(JSON.stringify(url_params, null, '\t'));
		},
		error: function(error) {
			console.log(error.responseText);
		}
	});
	}
});

$('#remove').click(function() {
	url_params = $("#Form2").serialize();
	//filename = formvals[0].value;
	filename = $("#Form2").serializeArray()[0].value;

	if(filename === ""){
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Filename must not be left empty. </strong></h4>");

	}else{
	$.ajax({
		url: '/database/remove',
		data: JSON.stringify(url_params, null, '\t'),
		type: 'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(response) {
			console.log(response);
			$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Picture: " + filename  +".jpg removed. </strong></h4>");
			//$('#MediaTable').append(
			//	"<tr>" +
			//	"<td>" + today + "</td>" +
			//	"<td><a href=\"/media/" + filename + ".jpg\">" + filename + ".jpg</a></td>" +
			//	"</tr>");
			console.log(JSON.stringify(url_params, null, '\t'));
			location.reload(true); // Force the page to reload to get the list of items in the database without having to try to find and delete the item in the table
		},
		error: function(error) {
			console.log(error.responseText);
		}
	});
	}
});

$('#new').click(function() {
	$.ajax({
		url: '/database/new',
		type: 'GET',
		success: function(response) {
			console.log(response);
			location.reload(true); // Force the page to reload to get the new database without having to try to delete all the items in the table
		},
		error: function(error) {
			console.log(error.responseText);
		}
	});
});

