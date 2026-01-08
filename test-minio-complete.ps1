# ============================================================================
# MinIO Complete Test - Create User and Upload Image
# ============================================================================

Write-Host "`n=== MinIO COMPLETE TEST ===" -ForegroundColor Green

$baseUrl = "http://localhost:8000/api"

# 1. Erstelle einen User
Write-Host "`n=== 1. CREATE USER ===" -ForegroundColor Cyan
$userBody = @{
    name = "Test User"
    email = "testuser@technikum-wien.at"
    study_program = "Computer Science"
    interests = @("Programming", "Testing", "MinIO")
} | ConvertTo-Json

try {
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/users/" -Method POST -ContentType "application/json" -Body $userBody
    $userId = $userResponse.id
    Write-Host "✅ User created with ID: $userId" -ForegroundColor Green
    Write-Host "Name: $($userResponse.name)" -ForegroundColor Yellow
} catch {
    Write-Host "⚠ User creation failed (might already exist), checking existing users..." -ForegroundColor Yellow
    $users = Invoke-RestMethod -Uri "$baseUrl/users/"
    if ($users.Count -gt 0) {
        $userId = $users[0].id
        Write-Host "✅ Using existing user ID: $userId" -ForegroundColor Green
        Write-Host "Name: $($users[0].name)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ No users found. Please create a user first." -ForegroundColor Red
        exit
    }
}

# 2. Lade Test-Bild herunter
Write-Host "`n=== 2. DOWNLOAD TEST IMAGE ===" -ForegroundColor Cyan
$testImagePath = "$env:TEMP\test-minio-upload.jpg"
Write-Host "Downloading from picsum.photos..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "https://picsum.photos/800/600" -OutFile $testImagePath
Write-Host "✅ Image saved to: $testImagePath" -ForegroundColor Green

# 3. Upload Post mit Bild via Python (da PowerShell 5.1 multipart/form-data kompliziert ist)
Write-Host "`n=== 3. UPLOAD POST WITH IMAGE TO MINIO ===" -ForegroundColor Cyan

$pythonScript = @"
import requests
import json

url = 'http://localhost:8000/api/posts/'
image_path = '$($testImagePath.Replace('\', '/'))'

with open(image_path, 'rb') as img:
    files = {'image_file': img}
    data = {
        'user': '$userId',
        'title': 'MinIO Test - Real Image Upload',
        'text': 'This image is stored in MinIO object storage! 🎉'
    }
    
    response = requests.post(url, files=files, data=data)
    
    print(f'Status Code: {response.status_code}')
    
    if response.status_code in [200, 201]:
        result = response.json()
        print('\n✅ SUCCESS! Post created with image uploaded to MinIO!')
        print(f'Post ID: {result["id"]}')
        print(f'Title: {result["title"]}')
        print(f'Image Path in MinIO: {result.get("image", "N/A")}')
        
        # Speichere Post-ID für später
        import os
        with open(os.path.join(os.environ['TEMP'], 'last_post_id.txt'), 'w') as f:
            f.write(str(result["id"]))
    else:
        print(f'\n❌ ERROR: {response.text}')
"@

$scriptPath = "$env:TEMP\upload_to_minio.py"
$pythonScript | Out-File -FilePath $scriptPath -Encoding UTF8

python $scriptPath

# 4. Zeige den erstellten Post
if (Test-Path "$env:TEMP\last_post_id.txt") {
    $postId = Get-Content "$env:TEMP\last_post_id.txt"
    
    Write-Host "`n=== 4. RETRIEVE CREATED POST ===" -ForegroundColor Cyan
    $post = Invoke-RestMethod -Uri "$baseUrl/posts/$postId/"
    Write-Host ($post | ConvertTo-Json -Depth 3) -ForegroundColor Yellow
}

# 5. MinIO Web-UI Info
Write-Host "`n=== 5. CHECK MINIO WEB CONSOLE ===" -ForegroundColor Green
Write-Host "Open: http://localhost:9001/" -ForegroundColor Cyan
Write-Host "Username: minio" -ForegroundColor Cyan
Write-Host "Password: mino_admin" -ForegroundColor Cyan
Write-Host "Bucket: social-media-bucket" -ForegroundColor Cyan
Write-Host "`nYou should see your uploaded image in the posts folder!" -ForegroundColor Yellow

# Cleanup
Remove-Item $testImagePath -ErrorAction SilentlyContinue
Remove-Item $scriptPath -ErrorAction SilentlyContinue

Write-Host "`n✅ TEST COMPLETE!" -ForegroundColor Green
