document.querySelector("button").addEventListener("click", ()=>{
    let initial = 50;
    let a = document.querySelector("[name='num1']");
    let b = document.querySelector("[name='num2']");
    if(a.value !== "" && b.value !== ""){
        document.querySelector(".output").textContent = initial + Number(a.value) + Number(b.value);
    }else{
        alert("both fields are required")
    }

})
