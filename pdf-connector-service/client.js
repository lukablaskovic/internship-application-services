import axios from 'axios';

// Define the URL you want to make a GET request to
const apiUrl = 'https://jsonplaceholder.typicode.com/posts/1';

// Make a GET request using Axios
axios.get(apiUrl)
  .then(response => {
    // Handle the successful response here
    console.log('Response data:');
    console.log(response.data);
  })
  .catch(error => {
    // Handle any errors here
    console.error('Error:', error);
  });
