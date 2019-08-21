// Define global scope variables
var interval = null;
var currentImageID = 0;
var maxNumberOfImages = 155;
var repetitionTime = 2000;
var lastValidImageID = 0;
var maxValidImageID = 0;
var canvasParamsUpdated = false;
var roiFileName = null;
var prevBtnPressed = false;
var displayMode = "fMRI";
var currentTraceID = 0;
var brain;
var experimentName;

// Default sprite params for template image
var sprite_params = {
    canvas: "3Dviewer",
    sprite: "spriteImg",
    nbSlice: {"X": 74, "Y": 84, "Z": 65},
    min: 0.0,
    max: 1269.0,
    colorCrosshair: "#de101d",
    flagCoordinates: true,
    crosshair: true,
    affine: [
         [2.9729700088500977, 0.0, 0.0, -106.54425907135008],
         [0.0, 2.9729700088500977, 0.0, -119.65008878707886],
         [0.0, 0.0, 2.9729700088500977, -70.0960693359375],
         [0.0, 0.0, 0.0, 1.0]
         ]
    };


// Hide the file selector
$( document ).ready(function(){
    $("#file-selector").addClass("d-none");
});


// Initialize the brainsprite canvas with template params
$( window ).load(function(){
    brain = brainsprite(sprite_params);
});

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
        getSprite(currentImageID);
    }
});


// PREVIOUS button
$("#prevBtn").click(function() {
    if (currentImageID > 1) {
        currentImageID--;
        getSprite(currentImageID);
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

/* ***************************************************************************
 * Slider, dropdown select and file selector control
 * ***************************************************************************/

$("#volume-range-slider").on("input", function(elem) {
    var currentSliderValue = $(this).val();
    getSprite(currentSliderValue);
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


$("#roi_file").change(function(e) {
    roiFileName = e.target.files[0].name;
    $("label[for = customFile]").text(roiFileName);
});


/* ***************************************************************************
 * Plotting functions
 * ***************************************************************************/

var addNewTrace = (voxel_coordinates) => {
    if (currentTraceID === 1) {
        // If a trace already exists, delete it
        Plotly.deleteTraces(voxel_value_graph, 0);
        currentTraceID--;
    }

    // Generate a random color
    var randomColor = "#000000".replace(/0/g,function(){return (~~(Math.random()*16)).toString(16);});

    // Get the values of the currently selected oxel and plot them
    getVoxelValue(voxel_coordinates, function(response) {
        Plotly.plot('voxel_value_graph', [{
            x: Object.keys(response.voxel_values),
            y: Object.values(response.voxel_values),
            mode: 'lines',
            name: '(' + parseInt(voxel_coordinates.x) + ', ' +
                    parseInt(voxel_coordinates.y) + ', ' +
                    parseInt(voxel_coordinates.z) + ')',
            line: {color: randomColor}
        }]);
    });
}


var extendCurrentTrace = (trace_id, voxel_coordinates) => {
    // Allow the extension on the x-axis only when the previous button has not
    // been pressed
    if(!prevBtnPressed){
            if (trace_id === 0){
                // If no trace has been added yet, then add a new one
                addNewTrace(voxel_coordinates);
                currentTraceID++;
            } else {
                // Get the values of the selected voxel and extend the
                // current trace with the voxel value in the last
                // processed volume
                getVoxelValue(voxel_coordinates, function(response) {
                    y_value = response.voxel_values[currentImageID - 1];
                    Plotly.extendTraces('voxel_value_graph', {
                        x: [[currentImageID]],
                        y: [[ y_value ]]
                    }, [trace_id - 1]);
                });
            }
    }
}

/* ***************************************************************************
 * Data retrieval functions
 * ***************************************************************************/

var getSprite = (imageID) => {
    // Get the sprite data from the server for the requested image, based on
    // the display mode
    if (displayMode === 'fMRI'){
        $.ajax({
            url: '/api/sprite/' + experimentName + '/' + imageID,
            type: 'GET',
            success: function (response) {       
                updateCurrentBackgroundSprite(response, imageID);

                let voxel_coordinates = {
                    x: brain.coordinatesSlice.X,
                    y: brain.coordinatesSlice.Y,
                    z: brain.coordinatesSlice.Z
                    };

                extendCurrentTrace(currentTraceID, voxel_coordinates);
            },
            error: function (error) {
                // If an image is not found, then show modal
                $('#not-found-modal').modal('show');
            }
        });
    } else if (displayMode === 'overlay') {
        $.ajax({
            url: '/api/sprite/overlay/' + experimentName + '/' + imageID,
            type: 'GET',
            success: function (response) {       
                updateCurrentBackgroundSprite(response, imageID, true, true);
                let voxel_coordinates = {
                    x: brain.coordinatesSlice.X,
                    y: brain.coordinatesSlice.Y,
                    z: brain.coordinatesSlice.Z
                    };
                extendCurrentTrace(currentTraceID, voxel_coordinates);
            },
            error: function (error) {
                // If an image is not found, then show modal
                $('#not-found-modal').modal('show');
            }
        });
    } 
}


var getVoxelValue = (voxel_coordinates, success_callback) => {
    // Get the values of the selected voxel
    return $.ajax({
        url: '/api/voxel',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ "experiment_name": experimentName, "image_id": currentImageID, "voxel_coordinates": voxel_coordinates }),
        success: function (response) {
            success_callback(response);
        },
        error: function (error) {
            console.log(error);
        }
    });
}


/* ***************************************************************************
 * Brain canvas update functions
 * ***************************************************************************/


var setSpriteInterval = () => {
    // Sets an interval that calls the getSprite function every
    // <repetitionTime> milliseconds
    interval = setInterval(function() {
        if (currentImageID < maxNumberOfImages) {
            currentImageID = lastValidImageID + 1;
            getSprite(currentImageID);
        }
    }, repetitionTime);
}


var updateCurrentBackgroundSprite = (response,
                                     imageID,
                                     overlay=false,
                                     colormap=false) => {
     // Set the sprite images
     $("#spriteImg").attr("src", response.sprite_img);

    if (overlay === true) {
        $("#overlayImg").attr("src", response.stat_map_b64);
    }

    if (colormap === true) {
        $("#colorMap").attr("src", response.cm_b64);
    }

    lastValidImageID = currentImageID;

    // Execute after #spriteImg starts being loaded
    $("#spriteImg").load(function() {
        if (!canvasParamsUpdated) {
            // If the canvas params are not yet updated, then update them
            sprite_params = response.sprite_params;

            sprite_params.onclick = function() {
                let voxel_coordinates = {
                    x: this.coordinatesSlice.X,
                    y: this.coordinatesSlice.Y,
                    z: this.coordinatesSlice.Z
                };

                // Add a new trace on the plot
                addNewTrace(voxel_coordinates);
                currentTraceID++;
            };

            // Update the brainsprite canvas
            brain = brainsprite(sprite_params);
            canvasParamsUpdated = true;
         }
    });

    if(lastValidImageID > maxValidImageID) {
        maxValidImageID = lastValidImageID;
    }

    // Update volume range slider
    $("#volume-range-slider").attr("max", maxValidImageID);
    $("#volume-range-slider").val(imageID);

    // Display the current volume number
    document.getElementById("volumeNumber").innerHTML = imageID;
}
