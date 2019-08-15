var interval = null;
var currentImageID = 0;
var maxNumberOfImages = 155;
var repetitionTime = 2000;
var experimentName;
var lastValidImageID = 0;
var maxValidImageID = 0;
var spriteUpdated = false;
var roiFileName = null;
var displayMode = 'fMRI';
var currentTraceID = 0;
var brain;
var prevBtnPressed = false;

var sprite_params = {
    canvas: '3Dviewer',
    sprite: 'spriteImg',
    nbSlice: {"X": 74, "Y": 84, "Z": 65},
    min: 0.0,
    max: 1269.0,
    affine: [
         [2.9729700088500977, 0.0, 0.0, -106.54425907135008],
         [0.0, 2.9729700088500977, 0.0, -119.65008878707886],
         [0.0, 0.0, 2.9729700088500977, -70.0960693359375],
         [0.0, 0.0, 0.0, 1.0]
    ],
};

$( document ).ready(function(){
    $("#file-selector").addClass("d-none");
});

$( window ).load(function(){
    brain = brainsprite(sprite_params);
});


$("#startRTBtn").click(
    function() {
        if (currentImageID < maxNumberOfImages) {
            setSpriteInterval();
        } else {
            clearInterval(interval);
        }
    });

$("#stopRTBtn").click(function() {
    clearInterval(interval);
});

$("#nextBtn").click(function() {
    if (currentImageID < maxNumberOfImages) {
        currentImageID = lastValidImageID + 1;            
        getSprite(currentImageID);
    }
});

$("#prevBtn").click(function() {
    if (currentImageID > 1) {
        currentImageID--;
        getSprite(currentImageID);
        prevBtnPressed = true;
    }
});

$("#btnSaveSettings").click(function() {
    // TODO: Handle case when filename is empty
    if ($("#exp_name").val()) {
        // Update variables in global scope
        experimentName = $("#exp_name").val();
        maxNumberOfImages = $("#no_of_volumes").val();
        repetitionTime = $("#repetition_time").val();          
            
        // Send experiment settings to server
        $.ajax({
            url: '/api/settings',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ "experiment_name": experimentName, "display_mode": displayMode, "overlay_filename": roiFileName }),
            success: function (response) {
                console.log("Settings updated");            
            },
            error: function (error) {
                console.log(error);
            }
        });

        // Hide experiment settings
        $("#settingsForm").attr("class", "d-none");

        // Display visualization canvas and control buttons
        $("#vizControlButtons").attr("class", ".d-block");
        $("#vizCanvas").attr("class", ".d-block");
    }
});

$("#volume-range-slider").on('input', function(elem) {
    var currentSliderValue = $(this).val();
    getSprite(currentSliderValue);
});

$("#mode-select").on('change', function() {
    displayMode = this.value;
    if (displayMode === 'overlay') {
        $("#file-selector").addClass("d-block");
    } else if (displayMode == 'fMRI') {
        $("#file-selector").removeClass("d-block").addClass("d-none");
    }
});

$("#roi_file").change(function(e) {
    roiFileName = e.target.files[0].name;
    $("label[for = customFile]").text(roiFileName);
});

// "Not found" Modal buttons
$("#stopRTModalButton").click(() => {
    clearInterval(interval);
    $('#not-found-modal').modal('hide');
});


function setSpriteInterval() {
    interval = setInterval(function() {
        if (currentImageID < maxNumberOfImages) {
            currentImageID = lastValidImageID + 1;
            getSprite(currentImageID);
        }
    }, repetitionTime);
}

function updateCurrentBackgroundSprite(response, imageID, overlay=false, colormap=false) {
     $("#spriteImg").attr("src", response.sprite_img);

    if (overlay === true) {
        $("#overlayImg").attr("src", response.stat_map_b64);
    }    

    if (colormap === true) {
        $("#colorMap").attr("src", response.cm_b64);
    }

    lastValidImageID = currentImageID;

    $("#spriteImg").load(function() {
        if (!spriteUpdated) {
            sprite_params = response.sprite_params;

            sprite_params.onclick = function() {
                let voxel_coordinates = {
                    x: this.coordinatesSlice.X,
                    y: this.coordinatesSlice.Y,
                    z: this.coordinatesSlice.Z
                };
                addNewTrace(voxel_coordinates);
                currentTraceID++;
            };
            brain = brainsprite(sprite_params);
            spriteUpdated = true;
            console.log('updated sprite');
         }
    });

    if(lastValidImageID > maxValidImageID) {
        maxValidImageID = lastValidImageID;
    }

    $("#volume-range-slider").attr("max", maxValidImageID);
    $("#volume-range-slider").val(imageID);

    document.getElementById("volumeNumber").innerHTML = currentImageID;
}

function addNewTrace(voxel_coordinates) {
    if (currentTraceID === 1) {
        Plotly.deleteTraces(voxel_value_graph, 0);
        currentTraceID--;
    }

    var randomColor = "#000000".replace(/0/g,function(){return (~~(Math.random()*16)).toString(16);});
    getVoxelValue(voxel_coordinates, function(response) {
        Plotly.plot('voxel_value_graph', [{
            x: Object.keys(response.voxel_values),
            y: Object.values(response.voxel_values),
            mode: 'lines',
            name: '(' + parseInt(voxel_coordinates['x']) + ', ' + parseInt(voxel_coordinates['y']) + ', ' + parseInt(voxel_coordinates['z']) + ')',
            line: {color: randomColor}
        }]);
    });
}

function extendCurrentTrace(trace_id, voxel_coordinates) {
    if(!prevBtnPressed){
            if (trace_id === 0){
                addNewTrace(voxel_coordinates);
                currentTraceID++;
                console.log('added new trace');
            } else {
                getVoxelValue(voxel_coordinates, function(response) {
                    y_value = response.voxel_values[currentImageID - 1];
                    Plotly.extendTraces('voxel_value_graph', {
                        x: [[currentImageID]],
                        y: [[ y_value ]]
                    }, [trace_id - 1]);
                    console.log('extended trace', trace_id - 1);
                });
            }
    }
}

function getSprite(imageID) {
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
                console.log('id' + imageID + ' not found');
                $('#not-found-modal').modal('show');
            }
        });
    } else if (displayMode === 'overlay') {
        $.ajax({
            url: '/api/sprite/overlay/' + experimentName + '/' + imageID,
            type: 'GET',
            success: function (response) {       
                updateCurrentBackgroundSprite(response, imageID, true, true) ;   
            },
            error: function (error) {
                console.log('id' + image_id + ' not found');
                $('#not-found-modal').modal('show');
            }
        });
    } 
}

function getVoxelValue(voxel_coordinates, success_callback) {
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
