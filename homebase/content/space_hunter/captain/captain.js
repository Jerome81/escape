
var selectedDirection = "";

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

document.addEventListener('keypress', function(event) {
    console.log(`Key pressed: ${event.key}`);
    element = null;
    if (event.key == 'a') {
        console.log('highlight left');
        selectDirection(document.querySelector("#left"), "2");
    }
    if (event.key == 's') {
        console.log('highlight down');
        selectDirection(document.querySelector("#down"), "3");
    }
    if (event.key == 'd') {
        console.log('highlight right');
        selectDirection(document.querySelector("#right"), "4");
    }
    if (event.key == 'w') {
        console.log('highlight up');
        selectDirection(document.querySelector("#up"), "1");
    }


});

document.querySelectorAll(".card").forEach((c) => {
    c.addEventListener("click", () => {
      c.classList.toggle("active");
    });
  });

