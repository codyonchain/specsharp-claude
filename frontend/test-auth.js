// Test auth endpoint
fetch('http://localhost:8000/api/v2/auth/token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: 'username=test2@example.com&password=password123'
})
.then(res => res.json())
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));

// Test with axios like the app does
import axios from 'axios';

const formData = new FormData();
formData.append('username', 'test2@example.com');
formData.append('password', 'password123');

axios.post('http://localhost:8000/api/v2/auth/token', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
.then(res => console.log('Axios success:', res.data))
.catch(err => console.error('Axios error:', err.response?.data || err.message));