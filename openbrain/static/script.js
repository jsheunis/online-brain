var interval = null;
var currentImageID = 0;
var maxNumberOfImages = 155;
var repetitionTime = 2000;
var experimentName;
var lastValidImageID = 0;
var maxValidImageID = 0;
var spriteUpdated = false;
var sprite_params = {
    canvas: '3Dviewer',
    sprite: 'spriteImg',
    nbSlice: { 'Y':100 , 'Z':100 },
};

$("#startRTBtn").click(
    function(){
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
        console.log(currentImageID);
    }
});

$("#prevBtn").click(function() {
    if (currentImageID > 1) {
        currentImageID--;
        getSprite(currentImageID);
        console.log(currentImageID);
    }
});

$("#btnSaveSettings").click(function() {
    if ($("#exp_name").val()) {
        // Update variables in global scope
        experimentName = $("#exp_name").val();
        maxNumberOfImages = $("#no_of_volumes").val();
        repetitionTime = $("#repetition_time").val();          
            
        // Send experiment name to server
        $.ajax({
            url: '/api/settings/' + experimentName,
            type: 'GET',
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

function setSpriteInterval() {
    interval = setInterval(function() {
        if (currentImageID < maxNumberOfImages) {
            currentImageID = lastValidImageID + 1;
            getSprite(currentImageID);
        }
    }, repetitionTime);
}

function getSprite(imageID) {
    $.ajax({
        url: '/api/sprite/' + experimentName + '/' + imageID,
        type: 'GET',
        success: function (response) {            
            $("#spriteImg").attr("src", response.sprite_img);
            lastValidImageID = currentImageID;

            if (!spriteUpdated) {
                sprite_params = response.sprite_params; 
                var brain = brainsprite(sprite_params);
                spriteUpdated = true;
             }  

            if(lastValidImageID > maxValidImageID) {
                maxValidImageID = lastValidImageID;
            }

            $("#volume-range-slider").attr("max", maxValidImageID);
            $("#volume-range-slider").val(imageID);
        },
        error: function (error) {
            clearInterval(interval);
            // TODO: Add bootstrap modal notification when the end is reached
        }
    });
}