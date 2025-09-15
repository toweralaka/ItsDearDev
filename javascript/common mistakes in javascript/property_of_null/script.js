window.addEventListener("DOMContentLoaded", ()=>{
    const heading = document.querySelector('#main-heading');
    console.log(heading);
    heading.textContent = "Hello World!";

    showCircle(150, 150, 100).then(div => {
        div.classList.add('message-ball');
        div.append("Hello, world!");
    });
})



function showCircle(cx, cy, radius){
    let parent = document.querySelector(".container");
    let circleDiv = document.createElement("div");
    let currentRadius = 0;
    circleDiv.setAttribute("class","circle");
    circleDiv.setAttribute("id","text-div");
    circleDiv.style.top = `${ cx }px`;
    circleDiv.style.left = `${cy}px`;
    circleDiv.style.width = `${currentRadius}px`;
    circleDiv.style.height = `${currentRadius}px`;
    parent.appendChild(circleDiv);
    return new Promise(function (resolve, reject) {
        setTimeout(()=>{
            circleDiv.style.width = `${radius}px`;
            circleDiv.style.height = `${radius}px`;
            circleDiv.addEventListener('transitionend', function handler() {
                circleDiv.removeEventListener('transitionend', handler);
                resolve(circleDiv);
            });
        }, 0)
    })
    
}


