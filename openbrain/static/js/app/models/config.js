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
var socket = io();
var availableVolumesData = [];

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

var experimentName;
var operationMode;
