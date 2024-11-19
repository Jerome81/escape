
var selectedDirection = "";

const getData = async (url) => {
    response = await fetch("http://localhost:5002/get_data")        
    if (response.ok) {
        // Success
        data = await response.json();
        // console.log(data);
        return data;
    } else {
        // Error
        throw new Error(response.statusText);
    }
}

const retrievePossibleDirections = async (url) => {
    const json = await getData(url);       
    console.log(json);
    updatePossibleDirections(json["possible_directions"])
}

function updatePossibleDirections(dirs) {
    if (dirs != null) {
        enableOrDisableDirection("up", dirs.indexOf("1") >= 0);
        enableOrDisableDirection("right", dirs.indexOf("2") >= 0);
        enableOrDisableDirection("down", dirs.indexOf("3") >= 0);
        enableOrDisableDirection("left", dirs.indexOf("4") >= 0);
    } else {
        console.log("no possible directions.");
    }
}

function enableOrDisableDirection(dir, enable) {
    element = document.querySelector("#" + dir);
    if (enable) {
        element.setAttribute("style", "display: block;");
    } else {
        element.setAttribute("style", "display: none;");
    }
}


function selectDirection(element, direction) {
    console.log(element);

    var event = new MouseEvent('mouseover', {
    'view': window,
    'bubbles': true,
    'cancelable': true
    });

    console.log(selectedDirection);
    if (element.checkVisibility()) {
        unselectDirections();
        element.dispatchEvent(event);
        element.setAttribute("style", "border-color: #dcb8f050;box-shadow: 0 0 30px #c9a8e090, 0 0 2px #f9c8f0 inset");
        
        selectedDirection = direction;
        
    }
}

function unselectDirections() {
    unselect(document.querySelector("#left"));
    unselect(document.querySelector("#up"));
    unselect(document.querySelector("#right"));
    unselect(document.querySelector("#down"));
}

function unselect(element) {
    if (element.checkVisibility()) {
        element.setAttribute("style", "border-color: black;box-shadow: none;")
    }
}

function initiateJump() {
    if (selectedDirection == "") {
        console.log("No jump direction selected.");
        return;
    }

    console.log("Jumping in direction: " + selectedDirection);
    fetch("http://localhost:5002/move/" + selectedDirection);
    // Call server to initiate jump.

    // Disable controls.

    // Wait for callback.
}

document.addEventListener('keypress', function(event) {
    console.log(`Key pressed: ${event.key}`);
    element = null;
    if (event.key == 'a') {
        console.log('highlight left');
        selectDirection(document.querySelector("#left"), "4");
    }
    if (event.key == 's') {
        console.log('highlight down');
        selectDirection(document.querySelector("#down"), "3");
    }
    if (event.key == 'd') {
        console.log('highlight right');
        selectDirection(document.querySelector("#right"), "2");
    }
    if (event.key == 'w') {
        console.log('highlight up');
        selectDirection(document.querySelector("#up"), "1");
    }

    if (event.key == "Enter") {
        console.log("Initiating Jump");
        initiateJump();
    }

});

document.querySelectorAll(".card").forEach((c) => {
    c.addEventListener("click", () => {
      c.classList.toggle("active");
    });
  });

