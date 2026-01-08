# MinIO Upload Test
Write-Host "`n=== MINIO UPLOAD TEST ===" -ForegroundColor Green

# 1. User prüfen/erstellen
Write-Host "`n1. Checking users..." -ForegroundColor Cyan
$users = Invoke-RestMethod -Uri "http://localhost:8000/api/users/"

if ($users.Count -eq 0) {
    Write-Host "Creating user..." -ForegroundColor Yellow
    $userBody = @{
        name = "Felix Test"
        email = "felix@technikum-wien.at"
        study_program = "Software Engineering"
        interests = @("MinIO", "Testing")
    } | ConvertTo-Json
    
    $user = Invoke-RestMethod -Uri "http://localhost:8000/api/users/" -Method POST -ContentType "application/json" -Body $userBody
    $userId = $user.id
    Write-Host "User created: $userId" -ForegroundColor Green
} else {
    $userId = $users[0].id
    Write-Host "Using user: $userId" -ForegroundColor Green
}

# 2. Bild herunterladen
Write-Host "`n2. Downloading image..." -ForegroundColor Cyan
$imagePath = "$env:TEMP\test_minio.jpg"
Invoke-WebRequest -Uri "https://picsum.photos/800/600" -OutFile $imagePath -UseBasicParsing
Write-Host "Image saved" -ForegroundColor Green

# 3. Python Script erstellen
Write-Host "`n3. Uploading to MinIO..." -ForegroundColor Cyan

python -c "import requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    python -m pip install requests --quiet
}

# Python Script in Datei schreiben
$pyScript = "import requests`n"
$pyScript += "import sys`n"
$pyScript += "import json`n"
$pyScript += "`n"
$pyScript += "url = 'http://localhost:8000/api/posts/'`n"
$pyScript += "image_path = r'$imagePath'`n"
$pyScript += "user_id = '$userId'`n"
$pyScript += "`n"
$pyScript += "try:`n"
$pyScript += "    with open(image_path, 'rb') as img:`n"
$pyScript += "        files = {'image_file': ('test.jpg', img, 'image/jpeg')}`n"
$pyScript += "        data = {'user': user_id, 'title': 'MinIO Test', 'text': 'Stored in MinIO'}`n"
$pyScript += "        response = requests.post(url, files=files, data=data)`n"
$pyScript += "        if response.status_code in [200, 201]:`n"
$pyScript += "            result = response.json()`n"
$pyScript += "            print('SUCCESS')`n"
$pyScript += "            print(json.dumps(result, indent=2))`n"
$pyScript += "        else:`n"
$pyScript += "            print('ERROR')`n"
$pyScript += "            print(f'Status: {response.status_code}')`n"
$pyScript += "            print(response.text)`n"
$pyScript += "            sys.exit(1)`n"
$pyScript += "except Exception as e:`n"
$pyScript += "    print('ERROR')`n"
$pyScript += "    print(str(e))`n"
$pyScript += "    sys.exit(1)`n"

$pyScript | Out-File -FilePath "$env:TEMP\upload.py" -Encoding UTF8

# Python ausführen
$result = python "$env:TEMP\upload.py"

if ($result[0] -eq 'SUCCESS') {
    Write-Host "SUCCESS! Image uploaded to MinIO!" -ForegroundColor Green
    $jsonData = $result[1..($result.Length-1)] -join "`n" | ConvertFrom-Json
    Write-Host "`nPost ID: $($jsonData.id)" -ForegroundColor Cyan
    Write-Host "Image: $($jsonData.image)" -ForegroundColor Cyan
    
    Write-Host "`n=== MINIO WEB CONSOLE ===" -ForegroundColor Green
    Write-Host "URL: http://localhost:9001" -ForegroundColor Yellow
    Write-Host "User: minio" -ForegroundColor Yellow
    Write-Host "Pass: mino_admin" -ForegroundColor Yellow
    Write-Host "Bucket: social-media-bucket" -ForegroundColor Yellow
    
    Start-Process "http://localhost:9001"
} else {
    Write-Host "FAILED!" -ForegroundColor Red
    $result | ForEach-Object { Write-Host $_ -ForegroundColor Red }
}

# Cleanup
Remove-Item $imagePath -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\upload.py" -ErrorAction SilentlyContinue

Write-Host "`nDone!" -ForegroundColor Green
