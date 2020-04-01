document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
 
    socket.on('connect' , () => {

    	document.querySelectorAll('button').forEach(button => {
    		
    		button.onclick = () =>{
    			const selection = button.dataset.vote;
    			console.log(selection);
    			socket.emit('submit msg', {'selection':selection});
    		};

    	});

    });

    socket.on('annouce msg', data =>{

    	const li = document.createElement('li');
    	li.innerHTML = `YOUR MESSAGE IS: ${data.selection}`;
    	document.querySelector('#msgs').append(li);
    });



 });