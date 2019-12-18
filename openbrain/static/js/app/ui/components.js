$("#volume-range-slider").on("input", function(elem) {
    // Get value and convert it from String to Int
    var currentSliderValue = parseInt($(this).val());
    if (currentSliderValue < currentImageID) {
        clearInterval(interval);
        prevBtnPressed = true;
    }
    currentImageID = currentSliderValue;
    //getSprite(currentImageID);
});


$("#mode-select").on("change", function() {
    displayMode = this.value;
    if (displayMode === "overlay") {
        // Display the file selector
        $("#file-selector").addClass("d-block");
    } else if (displayMode == "fMRI") {
        // Hide the file selector
        $("#file-selector").removeClass("d-block").addClass("d-none");
    }
});

$("#operation-mode-select").on("change", function() {
    operationMode = this.value;
    if (operationMode === "real-time") {
        $("#startRTSimBtn").removeClass("d-none");
        $("#exp-dropdown-col").removeClass("d-block").addClass("d-none");
    } else if (operationMode == "prev-experiment") {
        $("#exp-dropdown-col").addClass("d-block");
        $("#startRTSimBtn").addClass("d-none");
    }
});


$("#roi_file").change(function(e) {
    roiFileName = e.target.files[0].name;
    $("label[for = customFile]").text(roiFileName);
});


$("#exp-dropdown").on("change", function() {
    selectedExperiment = this.value;

    if(selectedExperiment !== "none") {
        $.ajax({
            url: '/api/settings/' + selectedExperiment,
            type: 'GET',
            success: function (response) {
                // Set values in corresponding fields
                $("#exp_name").val(selectedExperiment);
                $("#no_of_volumes").val(response.exp_volumes_nr);
                $("#repetition_time").val(response.exp_repetition_time);
            },
            error: function (error) {
                console.log('Error occurred while retrieving experiment data: ' + error);
            }
        });
    }
});
