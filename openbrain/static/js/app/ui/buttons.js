/* ***************************************************************************
 * Button control
 * ***************************************************************************/

// START RT button
$("#startRTBtn").click(
    function() {
        if (currentImageID < maxNumberOfImages) {
            setSpriteInterval();
        } else {
            clearInterval(interval);
        }
    });


// STOP RT button
$("#stopRTBtn").click(function() {
    clearInterval(interval);
});


// NEXT button
$("#nextBtn").click(function() {
    if (currentImageID < maxNumberOfImages) {
    currentImageID = lastValidImageID + 1;
    //getSprite(currentImageID);
    }
});


// PREVIOUS button
$("#prevBtn").click(function() {
    if (currentImageID > 1) {
        currentImageID--;
        //getSprite(currentImageID);
        prevBtnPressed = true;
    }
});


// "Not found" Modal buttons
$("#stopRTModalButton").click(() => {
    clearInterval(interval);
    $("#not-found-modal").modal("hide");
});


$("#btnSaveSettings").click(function() {
    if((displayMode === "overlay" &&
        document.getElementById("roi_file").files.length !== 0) ||
        displayMode === "fMRI") {

        if ($("#exp_name").val()) {
            // Update variables in global scope
            experimentName = $("#exp_name").val();
            maxNumberOfImages = $("#no_of_volumes").val();
            repetitionTime = $("#repetition_time").val();

            // Send experiment settings to server
            $.ajax({
                url: "/api/settings",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                                        "experiment_name": experimentName,
                                        "repetition_time": repetitionTime,
                                        "number_of_volumes": maxNumberOfImages,
                                        "display_mode": displayMode,
                                        "overlay_filename": roiFileName
                                        }),
                success: function (response) {
                    console.log("Settings updated");
                },
                error: function (error) {
                    console.log(error);
                }
            });

            // Hide experiment settings form
            $("#settingsForm").attr("class", "d-none");

            // Display visualization control buttons and canvas
            $("#vizControlButtons").attr("class", ".d-block");
            $("#vizCanvas").attr("class", ".d-block");
        }
    }
});


// "Start RT Simulation" button
$("#startRTSimBtn").click(function() {
    $.ajax({
        url: "/api/sim/" + repetitionTime + "/" + maxNumberOfImages,
        type: "GET",
        success: function (response) {
            console.log("Started RT simulation script", $(this));
            $("#startRTSimBtn").attr("disabled", true);
            $("#stopRTSimBtn").attr("disabled", false);
        },
        error: function (error) {
            console.log(error);
        }
    });
});

