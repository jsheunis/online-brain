/* ***************************************************************************
 * Data retrieval functions
 * ***************************************************************************/

//var getSprite = (imageID) => {
//    // Get the sprite data from the server for the requested image, based on
//    // the display mode
//    if (displayMode === 'fMRI'){
//        $.ajax({
//            url: '/api/sprite/' + experimentName + '/' + imageID,
//            type: 'GET',
//            success: function (response) {
//                updateCurrentBackgroundSprite(response, imageID);
//
//                let voxel_coordinates = {
//                    x: brain.coordinatesSlice.X,
//                    y: brain.coordinatesSlice.Y,
//                    z: brain.coordinatesSlice.Z
//                    };
//
//                extendCurrentTrace(currentTraceID, voxel_coordinates);
//            },
//            error: function (error) {
//                // If an image is not found, then show modal
//                $('#not-found-modal').modal('show');
//            }
//        });
//    } else if (displayMode === 'overlay') {
//        $.ajax({
//            url: '/api/sprite/overlay/' + experimentName + '/' + imageID,
//            type: 'GET',
//            success: function (response) {
//                updateCurrentBackgroundSprite(response, imageID, true, true);
//                let voxel_coordinates = {
//                    x: brain.coordinatesSlice.X,
//                    y: brain.coordinatesSlice.Y,
//                    z: brain.coordinatesSlice.Z
//                    };
//                extendCurrentTrace(currentTraceID, voxel_coordinates);
//            },
//            error: function (error) {
//                // If an image is not found, then show modal
//                $('#not-found-modal').modal('show');
//            }
//        });
//    }
//}


//var getVoxelValue = (voxel_coordinates, success_callback) => {
//    // Get the values of the selected voxel
//    return $.ajax({
//        url: '/api/voxel',
//        type: 'POST',
//        contentType: 'application/json',
//        data: JSON.stringify({ "experiment_name": experimentName, "image_id": currentImageID, "voxel_coordinates": voxel_coordinates }),
//        success: function (response) {
//            success_callback(response);
//        },
//        error: function (error) {
//            console.log(error);
//        }
//    });
//}
