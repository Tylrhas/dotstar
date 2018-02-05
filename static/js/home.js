$(".file").click(function () {
    //enable the start and stop button and add selected class to the file button
    if ($(this).is('#selected-file')) {  
        //enable all files
        $('.file').prop('disabled', false); 
        //disables the controls
        $('.controls .btn').prop('disabled', true);
        $(this).removeAttr('id'); 
    } else {  //<-- if checkbox was unchecked
        $('.file').not(this).prop('disabled', true); // <-- disable all but selected file
        //add selected class
        $(this).attr("id", "selected-file");
        //enables the controls
        $('.controls .btn').prop('disabled', false);
    }
});

$('#reset').click(function () {
    //deselect the image and disable the start and stop buttons
});

$('#start').click(function () {
    //on start button click enable the stop button and send the API call to the server to start the painting
});

$('#stop').click(function () {
    //on stop run api call to turn off the painting function
});