document.addEventListener('DOMContentLoaded', () =>{

	document.querySelector('#name').onkeyup = () =>
	{
		
		const request = new XMLHttpRequest();
		const username = document.querySelector('#name').value;
		request.open('POST', '/check');

		request.onload = () => {
			// Extract json object 

			response = JSON.parse(request.responseText);
			console.log(response)
			if (response.flag){
				success = "User exists";
				document.querySelector('#result').innerHTML = success;
			}
			else{

				document.querySelector('#result').innerHTML = "User not found";
			}

		} 

		const data = new FormData();
		data.append('username',username);

		request.send(data);
		return false;
	}
});