function setup(){
	const values = [];
	for(let i = 0; i < 30; i++){
		values[i] = Math.floor(Math.random() * 100);
	}
	const shapeA = [3, 5, 2];
	const shapeB = [3, 2, 5];
	const a = tf.tensor(values, shapeA);
	const b = tf.tensor(values, shapeB);
	console.log(a.toString())
	console.log(b.toString())
	console.log(a.dataSync())

	const c = a.matMul(b)
	// a.print()
	// b.print()
	c.print()

}

setup()