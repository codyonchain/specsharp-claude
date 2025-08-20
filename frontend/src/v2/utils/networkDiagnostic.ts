// Add this to intercept the API response
export const diagnoseAPIResponse = (response: any) => {
  console.group('🌐 API RESPONSE DIAGNOSTIC');
  console.log('Full response:', response);
  console.log('Building type in response:', response?.analysis?.parsed?.building_type);
  console.log('Response keys:', Object.keys(response || {}));
  console.log('Analysis keys:', Object.keys(response?.analysis || {}));
  console.log('Parsed keys:', Object.keys(response?.analysis?.parsed || {}));
  console.groupEnd();
  return response;
};