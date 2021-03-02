//This is the green B I N G O table row
var bingoRow;

/*Setup / tear down*/
function setUp(){
	resetBoard();
	getLocalStorage("wins");	
	getLocalStorage("losses");	
}

function resetBoard(){
	document.getElementsByClassName("gameSelection")[0].style.display = "inline";
	document.getElementsByClassName("gameSelection")[1].style.display = "inline";
	document.getElementsByClassName("winOrLose")[0].style.display = "none";
	document.getElementsByClassName("winOrLose")[1].style.display = "none";

	bingoRow = document.createElement("table");
	bingoRow.setAttribute("id","bingotable");
	var row = document.createElement("tr");
	//Create bingoRow
	for(var i=0;i<5;i++){
		var letter = "BINGO".charAt(i);
		var node = document.createElement("th");
		node.setAttribute("id", letter);
		node.setAttribute("class", "BingoRow");
		var textnode = document.createTextNode(letter); 
		node.appendChild(textnode);                             
		row.appendChild(node);
	}
	bingoRow.appendChild(row);

	document.getElementById("bingotable").replaceWith(bingoRow);
}

/*Helper functions*/
function clickEvent(elmnt){
	var squareClass = elmnt.className;
	if(squareClass == "freeSquare")
		elmnt.setAttribute("class", "clickedSquare");
	else{
		if(elmnt.id != "square12")
			elmnt.setAttribute("class", "freeSquare");
		return;
	}
	if(checkForBingo())
		document.getElementById("win").setAttribute("style","background-color: #44c767;");
	else
		document.getElementById("win").setAttribute("style","background-color: grey;");
}

function getLocalStorage(key){
	var value = localStorage.getItem(key);
	if(value==null){
		localStorage.setItem(key, 0);
		value = 0;
	}
	document.getElementById(""+key).innerHTML  = value;	
	return value;
}


function won(){
	if(!checkForBingo()) return;
	alert("BINGO!");
	localStorage.setItem("wins",  parseInt(getLocalStorage("wins"))+1);
	getLocalStorage("wins");
	resetBoard();	
}
function lost(){
	localStorage.setItem("losses",  parseInt(getLocalStorage("losses"))+1);
	getLocalStorage("losses");
	resetBoard();	
}

function checkForBingo(){
	var isCheckedDiagonal1 = true;
	var isCheckedDiagonal2 = true;
	for(var i=0;i<5;i++){
		var isCheckedRow = true;
		var isCheckedCol = true;
		for(var j=0;j<5;j++){
			if(document.getElementById("square"+(5*j+i)).className == "freeSquare")
				isCheckedRow = false;
			if(document.getElementById("square"+(5*i+j)).className == "freeSquare")
				isCheckedCol = false;
		}
		if(isCheckedRow || isCheckedCol){
			return true;
		}
		if(document.getElementById("square"+(5*i+i)).className == "freeSquare")
				isCheckedDiagonal1 = false;
		if(document.getElementById("square"+(5*i+(4-i))).className == "freeSquare")
				isCheckedDiagonal2 = false;
	}
	if(isCheckedDiagonal1 || isCheckedDiagonal2){
		return true;
	}
	return false;
}

/*Create BINGO card functions*/
function newRandom(){
	var card = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]];
	for(var i=0;i<5;i++){
		for(var j=0;j<5;j++){
			card[j][i] = Math.floor(Math.random() * 15) + 15*j + 1;
			for(var k=0;k<i;k++){
				if(card[j][i] == card[j][k]){
					i--;
					break;
				}
			}
		}
	}
	card[2][2] = "f";
	newCard(card);
}



function newSpecified(){
	inputString = prompt("Enter a board");

	//This checks if there are 5 digits within the correct range with the format B()I()N()G()O()
	if(!/[Bb]\((((1\d)|\d),?){5}\)[Ii]\((((1[6789])|(2\d)|(30)),?){5}\)[Nn]\((((3[987654321])|4[01234]),?){2}[fF],(((3[987654321])|4[01234]),?){2}\)[Gg]\((((4[6789])|(5\d)|(60)),?){5}\)[Oo]\(((((6[987654321])|7[01234])),?){5}\)/g.test(inputString))
		return;

	//Removes BINGO and parentheses and replaces them with commas to make a single list 
	var stringArray = inputString.replaceAll(/\)[IiNnGgOo]\(/g,",").replaceAll(/[Bb\(\)]/g,"").split(",");

	//This checks to see if the values within the list are unique
	if(!/^(?!.*(\b(?:[\dfF]+)\b).*\b\1\b)(?:[\df]+)(?:,(?:[\dfF]+))*$/g.test(stringArray))
		return;


	var card = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
	for(var i=0;i<5;i++){
		for(var j=0;j<5;j++){
			card[j][i] = stringArray[5*j+i];
		}
	}
	newCard(card);
}

function newCard(card){
	document.getElementById("win").setAttribute("style","background-color: grey;");
	var root = bingoRow;

	for(var i=0;i<5;i++){
		row = document.createElement("tr");
		for(var j=0;j<5;j++){
			var node = document.createElement("th");
			node.setAttribute("id", "square"+(5*j+i));
			node.setAttribute("class", "freeSquare");
			node.onclick = function() {clickEvent(this)};
			var textnode = document.createTextNode(""+card[j][i]); 
			node.appendChild(textnode);                             
			row.appendChild(node);
		}
		root.appendChild(row);
	}

	//document.getElementById("bingotable").replaceChild(root,document.getElementById("c"));
	document.getElementById("bingotable").replaceWith(root);
	document.getElementById("square12").setAttribute("class", "clickedSquare");

	document.getElementsByClassName("gameSelection")[0].style.display = "none";
	document.getElementsByClassName("gameSelection")[1].style.display = "none";
	document.getElementsByClassName("winOrLose")[0].style.display = "inline";
	document.getElementsByClassName("winOrLose")[1].style.display = "inline";
}
