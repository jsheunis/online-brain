/* ***************************************************************************
 * Plotting functions
 * ***************************************************************************/
//
//var addNewTrace = (voxel_coordinates) => {
//    if (currentTraceID === 1) {
//        // If a trace already exists, delete it
//        Plotly.deleteTraces(voxel_value_graph, 0);
//        currentTraceID--;
//    }
//
//    // Generate a random color
//    var randomColor = "#000000".replace(/0/g,function(){return (~~(Math.random()*16)).toString(16);});
//
//    // Get the values of the currently selected oxel and plot them
//    getVoxelValue(voxel_coordinates, function(response) {
//        Plotly.plot('voxel_value_graph', [{
//            x: Object.keys(response.voxel_values),
//            y: Object.values(response.voxel_values),
//            mode: 'lines',
//            name: '(' + parseInt(voxel_coordinates.x) + ', ' +
//                    parseInt(voxel_coordinates.y) + ', ' +
//                    parseInt(voxel_coordinates.z) + ')',
//            line: {color: randomColor}
//        }]);
//    });
//}
//
//
//var extendCurrentTrace = (trace_id, voxel_coordinates) => {
//    // Allow the extension on the x-axis only when the previous button has not
//    // been pressed
//    if(!prevBtnPressed){
//            if (trace_id === 0){
//                // If no trace has been added yet, then add a new one
//                addNewTrace(voxel_coordinates);
//                currentTraceID++;
//            } else {
//                // Get the values of the selected voxel and extend the
//                // current trace with the voxel value in the last
//                // processed volume
//                getVoxelValue(voxel_coordinates, function(response) {
//                    y_value = response.voxel_values[currentImageID - 1];
//                    Plotly.extendTraces('voxel_value_graph', {
//                        x: [[currentImageID]],
//                        y: [[ y_value ]]
//                    }, [trace_id - 1]);
//                });
//            }
//    }
//}
