let r,g,b, database;

function pickColor(){
	r = floor(random(256));
	g = floor(random(256));
	b = floor(random(256));
	background(r,g,b);
}
function setup(){

	var firebaseConfig = {
	    apiKey: "AIzaSyDzrZUScnXhP6YpxCWDj1k113hqBnFcoGc",
	    authDomain: "color-classification-eee25.firebaseapp.com",
	    databaseURL: "https://color-classification-eee25.firebaseio.com",
	    projectId: "color-classification-eee25",
	    storageBucket: "color-classification-eee25.appspot.com",
	    messagingSenderId: "664559696364",
	    appId: "1:664559696364:web:f68a040e4af400128a68c9",
	    measurementId: "G-WG36KR82FH"
  	};
  	firebase.initializeApp(firebaseConfig);
  	database = firebase.database();
	createCanvas(100,100);
	pickColor();

	let buttons = [];
	buttons.push(createButton('red-ish'))
	buttons.push(createButton('green-ish'))
	buttons.push(createButton('blue-ish'))
	buttons.push(createButton('orange-ish'))
	buttons.push(createButton('yellow-ish'))
	buttons.push(createButton('pink-ish'))
	buttons.push(createButton('purple-ish'))
	buttons.push(createButton('brown-ish'))
	buttons.push(createButton('grey-ish'))

	for(let i = 0; i < buttons.length;i++){
		buttons[i].mousePressed(sendData);
	}
}

function sendData(){
	console.log(this.html());
	let colorDatabase = database.ref('colors')
	let data = {
		r:r,
		g:g,
		b:b,
		label: this.html()
	}
	console.log("saving data")
	let color = colorDatabase.push(data,finished);
	console.log("Firebase generated key: " + color.key)

	function finished(err){
		if(err){
			console.error(err)
		}else{
			console.log("Success")
			pickColor();
		}
	}

}