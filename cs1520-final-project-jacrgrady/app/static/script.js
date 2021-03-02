function setup() {
	poller();
}


/***********************************************************
 * AJAX boilerplate
 ***********************************************************/

function makeRec(method, target, retCode, handlerAction, data) {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = makeHandler(httpRequest, retCode, handlerAction);
	httpRequest.open(method, target);

	if (data) {
		httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		httpRequest.send(data);
	}
	else {
		httpRequest.send();
	}
}


function makeHandler(httpRequest, retCode, action) {
	console.log("making handler!");
	function handler() {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === retCode) {
				console.log("recieved response text:  " + httpRequest.responseText);
				action(httpRequest.responseText);
			} else if (httpRequest.status === 404){
				console.error(JSON.parse(httpRequest.responseText).ERROR);
			}
			else{
				alert("There was a problem with the request.  you'll need to refresh the page!");
			}
		}
	}
	return handler;
}

//This is similar to the other makeRec, but argument for the method can be passed
function makeRec2(method, target, retCode, handlerAction, data) {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = makeHandler2(httpRequest, retCode, handlerAction,data);
	httpRequest.open(method, target);

	httpRequest.send();
	
}


function makeHandler2(httpRequest, retCode, action,data) {
	console.log("making handler!");
	function handler() {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === retCode) {
				console.log("recieved response text:  " + httpRequest.responseText);
				action(httpRequest.responseText,data);//Pass data for function
			}
			else if (httpRequest.status === 404){
				console.error(JSON.parse(httpRequest.responseText).ERROR);
			}else {
				alert("There was a problem with the request.  you'll need to refresh the page!");
			}
		}
	}
	return handler;
}

/*******************************************************
 * actual client-side app logic
 *******************************************************/

function poller() {
	var main = document.getElementById("mainDiv");
	var newCategoryButton = document.getElementById("newCategoryButton");
	if(newCategoryButton != null)
		newCategoryButton.addEventListener("click",newCat);
	var deleteCategoryButton = document.getElementById("deleteCategoryButton");
	if(deleteCategoryButton != null)
		deleteCategoryButton.addEventListener("click",deleteCat);
	var addPurchaseButton = document.getElementById("addPurchaseButton");
	if(addPurchaseButton != null)
		addPurchaseButton.addEventListener("click",addPurchase);

	if(main != null)
		makeRec("GET", "/cats", 200, repopulate);
}

function addError(error){
	console.error("ERROR: "+error);
}
function newCat() {
	var limit = document.getElementById("limit").value;
	var category_name = document.getElementById("category_name").value;
	if(!limit){
		addError("Please enter a limit");
	}
	else if(!category_name){
		addError("Please enter a name");
	}
	else{
		var data = {};
		data.name = category_name;
		data.limit = limit;
		console.log("sending " + JSON.stringify({"category":data}));
		makeRec("POST", "/cats", 201, poller,JSON.stringify({"category":data}));
	}
}


function deleteCat(catID) {
	var category = document.getElementById("category");
	console.log("DELETED");
	makeRec("DELETE", "/cats/" + category.value, 204, poller);
}


// helper function for repop:
function addCell(row, text) {
	var newCell = row.insertCell();
	var newText = document.createTextNode(text);
	newCell.appendChild(newText);
}

//Function for finding the balance of a category
function getBalance(total, num) {
  return total - parseInt(num["amount"]);
}
//Removes purchases that are not in the category
function filterFunc(category){
	return function(element) {
        return category["id"] == element["category_id"];
    }
	
}

function addCategory(category,purchases){
	var node = document.createElement("h2");
	purchases = purchases.filter(filterFunc(category));
	var left = parseInt(purchases.reduce(getBalance,parseInt(category["limit"])));
	if(category["name"] === "NONE"){
		left *= -1;
		left = "$"+left+" total";
	}
	else{
		if(left < 0)
			left = "overspent!";
		else
			left = "$"+left+" left";
	}
	node.innerHTML = category["name"]+" - "+left;

	return node;

}
function purch(responseText,categories){
	var main = document.getElementById("mainDiv");

	while (main.children.length > 0) {
		main.removeChild(main.childNodes[0]);
	}

	var purchases = JSON.parse(responseText)["purchases"];
	//console.log(purchases)
	if(purchases == "log in"){
		var node = document.createElement("h2");
		node.innerHTML = "Please log in";
		main.appendChild(node);
		return;
	}
	
	for(var i in categories){
		main.appendChild(addCategory(categories[i],purchases));
	}
}

function repopulate(responseText) {
	
	console.log("repopulating!");

	var categories = JSON.parse(responseText)["categories"];
	if(categories == null)
		return;
	//console.log(categories);
	makeRec2("GET", "/purchases", 200, purch,categories);
}



function addPurchase(){
	var amount = document.getElementById("amount");
	var item = document.getElementById("item");
	var date = document.getElementById("date");
	var category = document.getElementById("category");
	
	if(amount.value && item.value && date.value && category.value){
		
		var data = {};
		data.amount = amount.value;
		data.description = item.value;
		data.date = date.value;
		data.category_id = category.value;
		console.log("Sending "+JSON.stringify({"purchase":data}));
		makeRec("POST", "/purchases", 201, poller,JSON.stringify({"purchase":data}));
	}
	else{
		alert("Please fill out all sections");
	}
}

// setup load event
window.addEventListener("load", setup, true);
