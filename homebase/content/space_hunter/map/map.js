map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
];

movement_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
];
curX = 7
curY = 5

register("map", "localhost:5010")
//const data = await load_data();

//map = data[map];

//movement_map = null;//get_movement_map();

const getData = async (url) => {
    response = await fetch("http://localhost:5002/get_data")        
    if (response.ok) {
        // Success
        data = await response.json();
        console.log(data);
        return data;
    } else {
        // Error
        throw new Error(response.statusText);
    }
}

const updateStaticMap = async (url) => {
    const json = await getData(url);       
    drawMap(json["map"]);
    drawSpaceship(json["curX"], json["curY"]);
    drawMovementMap(json["movement_map"]);
}

const updateDynamicMap = async(url) => {
    const json = await getData(url);
    drawSpaceship(json["curX"], json["curY"]);
    drawMovementMap(json["movement_map"]);
}

updateStaticMap("http://localhost:5002/get_data");

function drawMap(map) {
    element = document.getElementById("map");

    for (y = 0; y < 16; y++) {
        for (x = 0; x < 16; x++) {
            tile = null;
            if (y == 0) {
                if (x == 0) {
                    tile = createElement("div", "coord");
                } else {
                    tile = createCoordTile(x);
                }
            } else {
                if (x == 0) {
                    tile = createCoordTile(y);
                } else {
                    tile = createTile(map[y - 1][x - 1]);
                    if (x % 5 == 0) {
                        appendClass(tile, "sector-right");
                    }
                    if (y % 5 == 0) {
                        appendClass(tile, "sector-down");
                    }
                }
            }
            tile.setAttribute("id", "coord-" + x + "-" + y);
            element.appendChild(tile);
        }
    }
}

function drawMovementMap(movement_map) {
    for (y = 1; y < 16; y++) {
        for (x = 1; x < 16; x++) {                   
            if (movement_map[y - 1][x - 1] > 0) {
                tile = document.getElementById("coord-" + x + "-" + y);
                if (tile.children.length == 0) {
                    console.log("creating element");
                    text = document.createElement("img", "arrow-" + movement_map[y - 1][x - 1]);
                    image = "arrow-" + movement_map[y - 1][x - 1];
                    if (y - 2 >= 0 && movement_map[y - 2][x - 1] == 3) {
                        image = image + "1";
                    }
                    if (y < movement_map.length && movement_map[y][x - 1] == 1) {
                        image = image + "3";
                    }
                    
                    if (x < movement_map[0].length && movement_map[y - 1][x] == 4) {
                        image = image + "2";
                    }
                    if (x - 2 >= 0 && movement_map[y - 1][x - 2] == 2) {
                        image = image + "4";
                    }
                    text.setAttribute("src", image + ".png");
                    text.setAttribute("width", "100%");
                    text.setAttribute("height", "100%");
                    console.log("appending");
                    tile.appendChild(text);
                } else {
                    console.log("coord-" + x + "-" + y + " has children");
                }
            }

        }
    }
}

function drawSpaceship(curX, curY) {
    e = document.getElementById("spaceship");
    if (e != null) {
        e.remove();
    }
    e = document.getElementById("coord-" + (curX + 1) + "-" + (curY + 1));
    console.log(e);
    if (e != null) {
        text = document.createElement("img", "spaceship");
        text.setAttribute("src", "spaceship.png");
        text.setAttribute("width", "100%");
        text.setAttribute("height", "100%");
        text.setAttribute("id", "spaceship");
        e.appendChild(text);
    }
}

function createTile(val) {
    tile = createElement("div", "tile");

    if (val == 0) {
        // Space       
    } else {
        text = document.createElement("img", "" + val);
        text.setAttribute("src", val + ".png");
        text.setAttribute("alt", "" + val);
        text.setAttribute("width", "100%");
        text.setAttribute("height", "100%");
        tile.appendChild(text);

    }

    return tile;
}


function createCoordTile(val) {
    tile = createElement("div", "coord");
    text = document.createTextNode(val);
    //text.setAttribute("style", "text-align: center");
    tile.appendChild(text);

    return tile;
}

function createElement(type, clazz) {
    e = document.createElement(type);
    e.setAttribute("class", clazz);
    return e;
}

function appendClass(tile, clazz) {
    tile.setAttribute("class", tile.getAttribute("class") + " " + clazz);
}

function register(type, url) {
    // Using fetch
    fetch("http://localhost:5002/register/" + type + "/" + url)
        .then(function (response) {
            if (response.ok) {
                // Success
                // return response.json();
            } else {
                // Error
                throw new Error(response.statusText);
            }
            }
        );
}

