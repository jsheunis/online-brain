
/* ***************************************************************************
 * Brain canvas update functions
 * ***************************************************************************/


//var setSpriteInterval = () => {
//    // Sets an interval that calls the getSprite function every
//    // <repetitionTime> milliseconds
//    interval = setInterval(function() {
//        if (currentImageID < maxNumberOfImages) {
//            currentImageID = lastValidImageID + 1;
//            //getSprite(currentImageID);
//        }
//    }, repetitionTime);
//}

//
//var updateCurrentBackgroundSprite = (response,
//                                     imageID,
//                                     overlay=false,
//                                     colormap=false) => {
//     // Set the sprite images
//     $("#spriteImg").attr("src", response.sprite_img);
//
//    if (overlay === true) {
//        $("#overlayImg").attr("src", response.stat_map_b64);
//    }
//
//    if (colormap === true) {
//        $("#colorMap").attr("src", response.cm_b64);
//    }
//
//    lastValidImageID = currentImageID;
//
//    // Execute after #spriteImg starts being loaded
//    $("#spriteImg").load(function() {
//        if (!canvasParamsUpdated) {
//            // If the canvas params are not yet updated, then update them
//            sprite_params = response.sprite_params;
//
//            sprite_params.onclick = function() {
//                let voxel_coordinates = {
//                    x: this.coordinatesSlice.X,
//                    y: this.coordinatesSlice.Y,
//                    z: this.coordinatesSlice.Z
//                };
//
//                // Add a new trace on the plot
//                addNewTrace(voxel_coordinates);
//                currentTraceID++;
//            };
//
//            // Update the brainsprite canvas
//            brain = brainsprite(sprite_params);
//            canvasParamsUpdated = true;
//         }
//    });
//
//    if(lastValidImageID > maxValidImageID) {
//        maxValidImageID = lastValidImageID;
//    }
//
//    // Update volume range slider
//    $("#volume-range-slider").attr("max", maxNumberOfImages);
//    $("#volume-range-slider").val(imageID);
//
//    // Display the current volume number
//    document.getElementById("volumeNumber").innerHTML = imageID;
//}

var updateSprite = (volume_data_dict) => {
    $("#spriteImg").attr("src", "data:image/png;base64," + volume_data_dict.sprite_b64);

    if (volume_data_dict.stat_map_b64 !== '') {
        $("#overlayImg").attr("src", "data:image/png;base64," + volume_data_dict.stat_map_b64);
    }

    if (volume_data_dict.colormap_b64 !== '') {
        $("#colorMap").attr("src", "data:image/png;base64," + volume_data_dict.colormap_b64);
    }

    lastValidImageID = currentImageID;

    // Execute after #spriteImg starts being loaded
    $("#spriteImg").load(function() {
        if (!canvasParamsUpdated) {
            parsed_sprite_json = JSON.parse(volume_data_dict.sprite_json)

            // If the canvas params are not yet updated, then update them
            sprite_params["canvas"] = volume_data_dict.canvas;
            sprite_params["sprite"] = volume_data_dict.sprite;
            sprite_params["colorBackground"] = volume_data_dict.colorBackground;
            sprite_params["crosshair"] = volume_data_dict.crosshair;
            sprite_params["flagCoordinates"] = volume_data_dict.flagCoordinates;
            sprite_params["title"] = volume_data_dict.title;
            sprite_params["colorFont"] = volume_data_dict.colorFont;
            sprite_params["flagValue"] = volume_data_dict.flagValue;
            sprite_params["colorCrosshair"] = volume_data_dict.colorCrosshair;
            sprite_params["voxelSize"] = volume_data_dict.voxelSize;
            sprite_params["affine"] = parsed_sprite_json.affine;
            sprite_params["min"] = parsed_sprite_json.min;
            sprite_params["max"] = parsed_sprite_json.max;
            sprite_params["nbSlice"] = parsed_sprite_json.nbSlice;

            sprite_params.onclick = function() {
                let voxel_coordinates = {
                    x: this.coordinatesSlice.X,
                    y: this.coordinatesSlice.Y,
                    z: this.coordinatesSlice.Z
                };

                // Add a new trace on the plot
                //addNewTrace(voxel_coordinates);
                //currentTraceID++;
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
    $("#volume-range-slider").attr("max", maxNumberOfImages);
//    $("#volume-range-slider").val(imageID);
//
//    // Display the current volume number
//    document.getElementById("volumeNumber").innerHTML = imageID;
}