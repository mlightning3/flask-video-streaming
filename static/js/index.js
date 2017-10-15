capture_status = true;

var d = new Date();
var today = d.getFullYear().toString() + "-" + (d.getMonth() + 1).toString() + "-" + d.getDate().toString();

$('#video_capture').click(function() {
	//url_params = $("#Form2").serialize();
	//filename = formvals[0].value;
	url_params = $("#Form2").serializeArray();
	filename = url_params[0].value;
	console.log(capture_status);

	if(filename === ""){
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Filename must not be left empty. </strong></h4>");

	}else{
		capture_status = !capture_status;
		$("#cap_status").val(capture_status);

	
	if(!capture_status){
		$('#video_capture span').html('Stop Capture');
		$(this).removeClass('indigo');
		$(this).addClass('red');
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Recording... </strong></h4>");

	}else{
		$('#video_capture span').html('Start Capture');
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Wrote video file. </strong></h4>");
		$(this).removeClass('red');
		$(this).addClass('indigo');
	}

	$.ajax({
		url: '/video_capture',
		data: url_params,
		type: 'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(response) {
		$('#MediaTable').append(
				"<tr>" +
				"<td>" + today + "</td>" +
				"<td><a href=\"/media/" + filename + ".avi\">" + filename + ".avi</a></td>" +
				"</tr>");

			console.log(JSON.stringify(url_params, null, '\t'));
		},
		error: function(error) {
			console.log(error.responseText);
		}
	});
	}



});

$('#snapshot').click(function() {
	url_params = $("#Form").serialize();
	//filename = formvals[0].value;
	filename = $("#Form").serializeArray()[0].value;

	if(filename === ""){
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Filename must not be left empty. </strong></h4>");

	}else{
	$.ajax({
		url: '/snapshot',
		data: JSON.stringify(url_params, null, '\t'),
		type: 'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(response) {
			console.log(response);
			$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Picture: " + filename  +".jpg written. </strong></h4>");
			$('#MediaTable').append(
				"<tr>" +
				"<td>" + today + "</td>" +
				"<td><a href=\"/media/" + filename + ".jpg\">" + filename + ".jpg</a></td>" +
				"</tr>");
			console.log(JSON.stringify(url_params, null, '\t'));
		},
		error: function(error) {
			console.log(error.responseText);
		}
	});
	}
});


