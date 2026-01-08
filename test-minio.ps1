# MinIO Upload Test - Einfach und funktionierend
# =================================================

Write-Host "`n=== MINIO UPLOAD TEST ===" -ForegroundColor Green

# 1. Prüfe ob User existieren
Write-Host "`n1. Checking for users..." -ForegroundColor Cyan
$users = Invoke-RestMethod -Uri "http://localhost:8000/api/users/"

if ($users.Count -eq 0) {
    Write-Host "Creating test user..." -ForegroundColor Yellow
    $userBody = @{
        name = "Felix Test"
        email = "felix.test@technikum-wien.at"
        study_program = "Software Engineering"
        interests = @("MinIO", "Testing", "Cloud Storage")
    } | ConvertTo-Json -Depth 3
    
    $user = Invoke-RestMethod -Uri "http://localhost:8000/api/users/" `
        -Method POST `
        -ContentType "application/json" `
        -Body $userBody
    $userId = $user.id
    Write-Host "âœ… User created with ID: $userId" -ForegroundColor Green
} else {
    $userId = $users[0].id
    Write-Host "âœ… Using existing user ID: $userId" -ForegroundColor Green
}

# 2. Lade Test-Bild herunter
Write-Host "`n2. Downloading test image..." -ForegroundColor Cyan
$imagePath = "$env:TEMP\minio_test_image.jpg"
Invoke-WebRequest -Uri "https://picsum.photos/800/600" -OutFile $imagePath -UseBasicParsing
Write-Host "âœ… Image saved: $imagePath" -ForegroundColor Green

# 3. Upload via Python (weil PowerShell 5.1 multipart/form-data schwierig ist)
Write-Host "`n3. Uploading image to MinIO via backend..." -ForegroundColor Cyan

# Prüfe ob Python requests installiert ist
python -c "import requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python requests library..." -ForegroundColor Yellow
    python -m pip install requests --quiet
}

$uploadScript = @'
import requests
import sys
import json

url = 'http://localhost:8000/api/posts/'
image_path = r'{0}'
user_id = '{1}'

try:
    with open(image_path, 'rb') as img:
        files = {{'image_file': ('test.jpg', img, 'image/jpeg')}}
        data = {{
            'user': user_id,
            'title': 'MinIO Test Post',
            'text': 'This image is stored in MinIO! Check the MinIO console.'
        }}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print('SUCCESS')
            print(json.dumps(result, indent=2))
        else:
            print('ERROR')
            print(f'Status: {{response.status_code}}')
            print(response.text)
            sys.exit(1)
            
except Exception as e:
    print('ERROR')
    print(f'Exception: {{e}}')
    sys.exit(1)
'@ -f $imagePath, $userId

$uploadScript | Out-File -FilePath "$env:TEMP\upload_test.py" -Encoding UTF8
$result = python "$env:TEMP\upload_test.py"

if ($result[0] -eq 'SUCCESS') {
    Write-Host "âœ… Image uploaded successfully!" -ForegroundColor Green
    $resultJson = $result[1..($result.Length-1)] -join "`n" | ConvertFrom-Json
    Write-Host "`nPost Details:" -ForegroundColor Yellow
    Write-Host "  ID: $($resultJson.id)" -ForegroundColor Cyan
    Write-Host "  Title: $($resultJson.title)" -ForegroundColor Cyan
    Write-Host "  Image Path: $($resultJson.image)" -ForegroundColor Cyan
    
    # 4. Prüfe MinIO Web Console
    Write-Host "`n=== CHECK MINIO CONSOLE ===" -ForegroundColor Green
    Write-Host "URL: http://localhost:9001" -ForegroundColor Cyan
    Write-Host "Username: minio" -ForegroundColor Cyan  
    Write-Host "Password: mino_admin" -ForegroundColor Cyan
    Write-Host "Bucket: social-media-bucket" -ForegroundColor Cyan
    Write-Host "`nDein Bild sollte im 'posts/' Ordner zu sehen sein!" -ForegroundColor Yellow
    
    # Optional: Öffne MinIO Console automatisch
    Start-Process "http://localhost:9001"
    
} else {
    Write-Host "âŒ Upload failed:" -ForegroundColor Red
    $result[1..($result.Length-1)] | ForEach-Object { Write-Host $_ -ForegroundColor Red }
}

# Cleanup
Remove-Item $imagePath -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\upload_test.py" -ErrorAction SilentlyContinue

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Green
