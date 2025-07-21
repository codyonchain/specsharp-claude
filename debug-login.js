// Run this in the browser console to debug the login issue

async function debugLogin() {
    console.log('=== Starting Login Debug ===');
    
    // Test 1: Direct API call with FormData (mimicking the frontend)
    console.log('\n1. Testing with FormData (frontend method):');
    try {
        const formData = new FormData();
        formData.append('username', 'test2@example.com');
        formData.append('password', 'password123');
        
        const response = await fetch('http://localhost:8000/api/v1/auth/token', {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok) {
            console.log('✅ Login successful!');
            console.log('Token:', data.access_token);
        } else {
            console.log('❌ Login failed:', data);
        }
    } catch (error) {
        console.error('❌ Network error:', error);
    }
    
    // Test 2: Check localStorage for existing token
    console.log('\n2. Checking localStorage:');
    const token = localStorage.getItem('token');
    console.log('Existing token:', token ? 'Found' : 'Not found');
    
    // Test 3: Test with axios (if available)
    if (typeof axios !== 'undefined') {
        console.log('\n3. Testing with axios:');
        try {
            const axiosFormData = new FormData();
            axiosFormData.append('username', 'test2@example.com');
            axiosFormData.append('password', 'password123');
            
            const axiosResponse = await axios.post('http://localhost:8000/api/v1/auth/token', axiosFormData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            console.log('Axios response:', axiosResponse.data);
        } catch (error) {
            console.error('Axios error:', error.response?.data || error.message);
        }
    }
    
    console.log('\n=== Debug Complete ===');
}

// Run the debug function
debugLogin();