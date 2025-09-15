const maxSize = 300;
const minSize = 20;
const balloon = document.querySelector("#balloon");
// let balloonSize = balloon.style.fontSize;
let pixelSize = window.getComputedStyle(balloon, null).getPropertyValue('font-size');
let balloonSize = parseFloat(pixelSize);
console.log(balloonSize);
const plusButton = document.querySelector(".up");
const blowUp = ()=>{
    console.log(balloonSize);
    balloonSize += 20;
    balloon.style.fontSize = `${balloonSize}px`;
    if(balloonSize>maxSize){
        balloon.innerText = "💥 POP!";
        balloon.style.fontSize = "30px";
        plusButton.removeEventListener("click", blowUp);
        minusButton.removeEventListener("click", shrink);
    }
}
plusButton.addEventListener("click", blowUp);
const minusButton = document.querySelector(".down");
const shrink = ()=>{
    console.log(balloonSize)
    balloonSize -= 20;
    balloon.style.fontSize = `${balloonSize}px`;
    if(balloonSize < minSize){
        balloon.innerText = "💨";
        balloon.style.fontSize = "20px";
        minusButton.removeEventListener("click", shrink);
        plusButton.removeEventListener("click", blowUp);
    }
}
minusButton.addEventListener("click", shrink);