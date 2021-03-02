var timeoutID;
var timeout = 1000;
function setup() {
	timeoutID = window.setInterval(polling, timeout);

	var chatBox = document.getElementById("submitNewChat");
	if(!chatBox)
		return false;

	chatBox.addEventListener("click", makePost, true);

	var deleteRoom = document.getElementById("delete_room");
	if(deleteRoom){
		deleteRoom.addEventListener("click",delete_room,true)
	}
}

//helper function to get the current room
function getRoom(){
	var chatName = document.getElementById("chatName");
	if(!chatName)
		return null;
	return chatName.innerText;
}

function polling(){
	if(!document.getElementById("session_user"))
		return false;
	if(!Room_poller())
		return false;
	var chatBox = document.getElementById("submitNewChat");
	if(!chatBox)
		return false;
	poller();
}

function makePost(){
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	var newChat = document.getElementById("newChat").value;

	httpRequest.onreadystatechange = function() { 
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			var session_user = document.getElementById("session_user").innerText;
			addMesage({"author": session_user, "message": newChat});
			clearInput();
		} else {
			alert("There was a problem with the post request.");
			return false;
		}
	}
	};

	httpRequest.open("POST", "/new_item");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	data = "newChat=" + newChat;
	
	httpRequest.send(data);
}

function delete_room(){
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = function() { 
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			location.replace("/index");
			return true;
		} else {
			alert("There was a problem with the post request.");
			return false;
		}
	}
	};

	httpRequest.open("POST", "/deleteRoom");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	httpRequest.send("OK");
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = function() {
		if (this.readyState === XMLHttpRequest.DONE) {
			if (this.status === 200) {
				var rows = JSON.parse(httpRequest.responseText);

				console.log(httpRequest.responseText);

				if(rows.error){
					return false;
				}
				if(rows.name != document.getElementById("chatName").innerText){
					deleteMessages();
					document.getElementById("chatName").innerText = rows.name;
				}
				else{
					for (var i = 0; i < rows.messages.length; i++) {
						addMesage(rows.messages[i]);
					}
				}
				
			}
			else {
				alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
			}
		}
	};

	var chats = document.getElementById("chats");
	httpRequest.open("GET", "/items/"+chats.children.length);
	httpRequest.send();
}

function Room_poller(){
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = function() {
		if (this.readyState === XMLHttpRequest.DONE) {
			if (this.status === 200) {
				var rows = JSON.parse(httpRequest.responseText);
				if(rows.error){
					window.location.replace("/index/error");
					return false;
				}
				console.log(httpRequest.responseText);
				deleteRooms();

				var exists = false;
				for (var i = 0; i < rows.rooms.length; i++) {
					addRoom(rows.rooms[i]);
					if(!getRoom() || rows.rooms[i].name == getRoom())
						exists = true;
				}
				if(!exists && window.location.href.split("/")[3]=="chat"){
					window.location = "/index/error";
					return false;
				}
				if(rows.rooms.length == 0){
					var rooms = document.getElementById("actionlinks");
					var a = document.createElement("a"); 
					a.innerText = "There are no rooms";
					a.href = "/index";
					rooms.appendChild(a); 
				}
				
			}
			else {
				alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
			}
		}
	};
	
	httpRequest.open("GET", "/rooms");
	httpRequest.send();
	return true;
}

function addMesage(message){
	var chats = document.getElementById("chats");
	var node = document.createElement("div"); 
	if(message.author === document.getElementById("session_user").innerText)
		node.className  = "container darker";
	else
		node.className  = "container";
	var roomName = document.createElement("p"); 
	roomName.innerText = message.message;
	var author = document.createElement("span"); 
	author.innerText = message.author;
	author.className  = "message_author";

	node.appendChild(author);
	node.appendChild(roomName);

	chats.appendChild(node); 
}

function deleteRooms(){
	var rooms = document.getElementById("actionlinks");
	while(rooms.children.length>3){
		rooms.removeChild(rooms.lastElementChild);
	}
}

//deletes all messages. This is used when another tab switches to another room, and
//the original tab must refresh all messages
function deleteMessages(){
	var chats = document.getElementById("chats");
	while(chats.children.length>0){
		chats.removeChild(chats.lastElementChild);
	}
}

function addRoom(room){
	var rooms = document.getElementById("actionlinks");
	var a = document.createElement("a"); 
	a.innerText = room.name;
	a.href = "/chat/"+room.name.replace(" ","%20");
	rooms.appendChild(a); 
}

function clearInput(){
	document.getElementById("newChat").value = "";
}

window.addEventListener("load", setup, true);
