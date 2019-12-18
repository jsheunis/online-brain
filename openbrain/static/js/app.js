// Initialize the brainsprite canvas with template params
$( window ).load(function(){
    brain = brainsprite(sprite_params);
    if (!window.indexedDB) {
    console.log("Your browser doesn't support a stable version of IndexedDB.");
    }
});

// Hide the file selector
$( document ).ready(function(){
    $("#file-selector").addClass("d-none");
    $("#exp-dropdown-col").addClass("d-none");
    openDb();
});
