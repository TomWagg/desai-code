
$(function() {
    refresh();
});


function refresh() {
    let container = document.body;
    let circles = []
    let count = 0;
    
    while (circles.length < 1000) {
        count += 1
        let new_circle = {
            "x": Math.floor(Math.random() * (window.innerWidth * 0.9)),
            "y": Math.floor(Math.random() * (window.innerHeight * 0.9))
        }
        if (conflict_check(circles, new_circle)) {
            circles.push(new_circle);
        }
    }

    for (var i = 0; i < circles.length; i++) {
        let circle = document.createElement("span");
        circle.classList.add("circle", "bg-primary");
        circle.style.top = circles[i].y;
        circle.style.left = circles[i].x;
        container.appendChild(circle);
    }
    console.log(circles, count);
}

function conflict_check(circles, new_circle) {
    return(true);
    for (let i = 0; i < circles.length; i++) {
        if (Math.sqrt(Math.pow(circles[i].x - new_circle.x, 2) - Math.pow(circles[i].y - new_circle.y, 2)) <= 20) {
            return(false);
        }
    }
    return(true)
}