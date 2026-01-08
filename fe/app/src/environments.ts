export const backendUrl = {
  // Use relative '/api' so requests go through NGINX proxy inside the FE container
  apiUrl: 'api'
};

export const environment = {
  apiUrl: '/api',
  minioUrl: 'http://localhost:9000/social-media-bucket',
  aiServiceUrl: 'http://localhost:8001'
};
