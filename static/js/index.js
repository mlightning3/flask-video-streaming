capture_status = true;
light_status = true;
gray_status = true;
resolution_status = true;
focus_status = true;

var d = new Date();
var today = d.getFullYear().toString() + "-" + (d.getMonth() + 1).toString() + "-" + d.getDate().toString();

// Records video, flips state of button and sends state of button back to server to toggle start stop
$('#video_capture').on('click touch', function() {
    url_params = $("#Form2").serializeArray();
    filename = url_params[0].value;
    console.log(capture_status);

    if(filename === ""){
	$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Filename must not be left empty. </strong></h4>");

    }else{
	capture_status = !capture_status;
	$('#cap_status').val(capture_status);      // Put our state into the html
	url_params = $("#Form2").serializeArray(); // Grab the changes we make to the html
	
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
		if(capture_status){
		    $('#MediaTable').append(
			"<tr>" +
			    "<td>" + today + "</td>" +
			    "<td><a href=\"/media/" + filename + ".avi\" target=\"_blank\">" + filename + ".avi</a></td>" +
			    "</tr>");
		}

		    console.log(JSON.stringify(url_params, null, '\t'));
		},
		error: function(error) {
		    console.log(error.responseText);
		}
	    });
    }
});

// Takes a picture when button is pressed
$('#snapshot').on('click touch', function() {
    url_params = $("#Form").serializeArray();
    filename = url_params[0].value;

    if(filename === ""){
	$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Filename must not be left empty. </strong></h4>");

    }else{
	$.ajax({
	    url: '/snapshot',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		$('#ReturnText').replaceWith("<h4 id='ReturnText'><strong> Picture: " + filename  +".jpg written. </strong></h4>");
		$('#MediaTable').append(
		    "<tr>" +
			"<td>" + today + "</td>" +
			"<td><a href=\"/media/" + filename + ".jpg\" target=\"_blank\">" + filename + ".jpg</a></td>" +
			"</tr>");
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		console.log(error.responseText);
	    }
	});
    }
});

// Sends value of the light button back to flask server
$('#light').on('click touch', (function() {
    light_status = !light_status;
	$('#light_status').val(light_status);      // Put our state into the html
	url_params = $("#Form3").serializeArray(); // Grab the changes we make to the html

	if(!light_status){
	    $(this).removeClass('indigo');
	    $(this).addClass('red');
	}else{
	    $(this).removeClass('red');
	    $(this).addClass('indigo');
	}

	$.ajax({
	    url: '/light',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});

// Sends slider value back to flask server
var valueOfSlider;
$( "#slider" ).slider({
    change: function(){
        valueOfSlider = $( this ).slider( "value" );
        $.getJSON('/set_brightness', {
            value:valueOfSlider
        });
    }
});

// Changes the image between grayscale and normal
// Should help latency by reducing the amount of data sent with image
$('#grayscale').on('click touch', function() {
    gray_status = !gray_status;
	$('#gray_status').val(gray_status);      // Put our state into the html
	url_params = $("#Form4").serializeArray(); // Grab the changes we make to the html

	if(!gray_status){
	    $(this).removeClass('indigo');
	    $(this).addClass('red');
	}else{
	    $(this).removeClass('red');
	    $(this).addClass('indigo');
	}

	$.ajax({
	    url: '/grayscale',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});

// Changes between a scaled down image and normal
// Should help latecy by reducing the amount of data sent with image
$('#resolution').on('click touch', function() {
    resolution_status = !resolution_status;
	$('#resolution_status').val(resolution_status);      // Put our state into the html
	url_params = $("#Form5").serializeArray(); // Grab the changes we make to the html

	if(!resolution_status){
	    $(this).removeClass('indigo');
	    $(this).addClass('red');
	}else{
	    $(this).removeClass('red');
	    $(this).addClass('indigo');
	}

	$.ajax({
	    url: '/resolution',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});

// Toggles the autofocus on supported cameras
$('#autofocus').on('click touch', function() {
    focus_status = !focus_status;
	$('#focus_status').val(focus_status);      // Put our state into the html
	url_params = $("#Form6").serializeArray(); // Grab the changes we make to the html

	if(!focus_status){
	    $(this).removeClass('indigo');
	    $(this).addClass('red');
	}else{
	    $(this).removeClass('red');
	    $(this).addClass('indigo');
	}

	$.ajax({
	    url: '/autofocus',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});

// Sets the focus back to the middle on supported cameras
$('#set_focus').on('click touch', function() {
	url_params = $("#Form7").serializeArray();

	$.ajax({
	    url: '/set_focus',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});

// Steps the focus up on supported cameras
$('#focus_pos').on('click touch', function() {
	url_params = $("#Form8").serializeArray();

	$.ajax({
	    url: '/step_focus',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});

// Steps the focus down on supported cameras
$('#focus_neg').on('click touch', function() {
	url_params = $("#Form9").serializeArray();

	$.ajax({
	    url: '/step_focus',
	    data: url_params,
	    type: 'GET',
	    contentType:'application/json;charset=UTF-8',
	    success: function(response) {
		console.log(response);
		console.log(JSON.stringify(url_params, null, '\t'));
	    },
	    error: function(error) {
		    console.log(error.responseText);
	    }
	});
});