let numeros =  [7,10, 2,8]
let target = 17

function twosum(numeros, target) {
    let position = []
    for(let i = 0; i<numeros.length; i++){
        for(let j = 1; j<numeros.length; j++) {
            if(numeros[i] + numeros[j] === target) {
                position.push(i, j)
            }
        }
    }
    console.log("As posições que somando dão igual ao target é: " + position)
    console.log(position)
}

twosum(numeros, target)