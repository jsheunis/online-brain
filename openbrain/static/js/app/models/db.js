const DB_NAME = "openbrain";
const DB_VERSION = 1;
const DB_STORE_NAME = "rt-data";

var db;

var openDb = () => {
    var req = indexedDB.open(DB_NAME, DB_VERSION);

    req.onsuccess = function (evt) {
      db = this.result;
      console.log("openDb DONE");
    };

    req.onerror = function (evt) {
        console.log("Permission for accessing IndexedDB is required");
    };

    req.onupgradeneeded = function (evt) {
     console.log("openDb.onupgradeneeded");

    var store = evt.currentTarget.result.createObjectStore(
        DB_STORE_NAME);
    };
}

var getObjectStore = (store_name, mode) => {
    var tx = db.transaction(store_name, mode);
    console.log(tx);
    return tx.objectStore(store_name);
}

var addRTData = (data) => {
    var store = getObjectStore(DB_STORE_NAME, 'readwrite');
    var req;

    try {
        console.log(data["data"]);
        req = store.put(data["data"], data["data"]["experiment_name"].concat("_", currentImageID));
    }
    catch (e) {
      throw e;
    }

    req.onsuccess = function (evt) {
      console.log("Insertion in DB successful");
    };

    req.onerror = function() {
      console.error("insertion in db error", this.error);
    };
  }
