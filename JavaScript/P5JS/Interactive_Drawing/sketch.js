let sketchRNN;
let currentStroke;
let x, y;
let nextPen = 'down'

function preload() {
  sketchRNN = ml5.sketchRNN('cat')
}

function setup() {
  createCanvas(400, 400);
  x = width / 2;
  y = height / 2;
  background(255)
  sketchRNN.generate(gotStrokePath)
}

function gotStrokePath(error, strokePath) {
  currentStroke = strokePath;
}

function draw() {
  if (currentStroke) {
    stroke(0)
    strokeWeight(4);
    
    if(nextPen == 'end'){
      noLoop();
      return;
    }
    
    if (nextPen == 'down') {
      line(x, y, x + currentStroke.dx, y + currentStroke.dy)
    }
    x += currentStroke.dx
    y += currentStroke.dy
    nextPen = currentStroke.pen;
    currentStroke = null;
    sketchRNN.generate(gotStrokePath)
  }
}