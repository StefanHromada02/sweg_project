# ============================================================================
# MinIO Test - Simple Image Upload
# ============================================================================

Write-Host "`n=== MinIO IMAGE UPLOAD TEST ===" -ForegroundColor Green

# 1. Lade Test-Bild herunter
$testImagePath = "$env:TEMP\test-minio-image.jpg"
Write-Host "Downloading test image..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "https://picsum.photos/800/600" -OutFile $testImagePath
Write-Host "✅ Image downloaded to: $testImagePath" -ForegroundColor Green

# 2. Upload via Python-Script (einfacher für PowerShell 5.1)
$pythonScript = @"
import requests

url = 'http://localhost:8000/api/posts/'
files = {'image_file': open('$($testImagePath.Replace('\', '/'))', 'rb')}
data = {
    'user': '1',
    'title': 'MinIO Test Post',
    'text': 'Testing image upload to MinIO storage'
}

try:
    response = requests.post(url, files=files, data=data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 201:
        post_data = response.json()
        print(f'\n✅ SUCCESS!')
        print(f'Post ID: {post_data["id"]}')
        print(f'Image Path: {post_data.get("image", "N/A")}')
except Exception as e:
    print(f'❌ Error: {e}')
"@

# Speichere Python-Script
$scriptPath = "$env:TEMP\test_minio_upload.py"
$pythonScript | Out-File -FilePath $scriptPath -Encoding UTF8

# Führe Python-Script aus
Write-Host "`nUploading image via Python..." -ForegroundColor Yellow
python $scriptPath

Write-Host "`n`n=== CHECK MINIO ===" -ForegroundColor Green
Write-Host "Open MinIO Console: http://localhost:9001/" -ForegroundColor Cyan
Write-Host "Login: minio / mino_admin" -ForegroundColor Cyan
Write-Host "Check bucket: social-media-bucket" -ForegroundColor Cyan

# Cleanup
Remove-Item $testImagePath -ErrorAction SilentlyContinue
Remove-Item $scriptPath -ErrorAction SilentlyContinue
