const dancer = document.querySelector("#dancer");
const startDanceButton = document.querySelector(".startDance");
const danceMoves = ["rotate(10deg)", "rotate(-10deg)", "translateX(50px)", "rotate(60deg)", "rotateY(180deg)", "rotateY(270deg)", "rotateY(360deg)", "translateX(-50px)", "rotate(-60deg)", "rotate(20deg)", "rotate(-20deg)", "scale(1.2)"];

const startDance = ()=>{
    for(let i=0; i<danceMoves.length; i++){
        setTimeout(()=>{
        dancer.style.transform = danceMoves[i];
        }, i*1000);
    }
}
// startDanceButton.addEventListener("click", startDance)

//===================================
// Loop Dancing
//====================================
let dancing = false;
let moveIndex = 0;

function startDanceLoop() {
    if (dancing) return; // prevent multiple starts
    dancing = true;
    danceLoop();
}

function stopDance() {
    dancing = false;
}

function danceLoop() {
    if (!dancing) return;

    dancer.style.transform = danceMoves[moveIndex];

    moveIndex = (moveIndex + 1) % danceMoves.length; // loop moves

    // call again after 1s
    setTimeout(danceLoop, 1000);
}

startDanceButton.addEventListener("click", startDanceLoop)