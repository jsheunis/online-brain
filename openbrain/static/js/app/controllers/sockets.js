socket.on('volume-data', function(req_dict) {
    updateSprite(req_dict)

    var volume_data = new Object();
    volume_data["data"] = req_dict;
    addRTData(volume_data);
});

