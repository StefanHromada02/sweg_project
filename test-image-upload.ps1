# ============================================================================
# MinIO Image Upload Test - Social Media Posts
# ============================================================================

$baseUrl = "http://localhost:8000/api/posts/"

Write-Host "`n=== MinIO IMAGE UPLOAD TEST ===" -ForegroundColor Green

# Option 1: Lade ein echtes Test-Bild von Picsum herunter
$testImagePath = "$env:TEMP\test-post-image.jpg"

Write-Host "Downloading test image..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "https://picsum.photos/800/600" -OutFile $testImagePath
Write-Host "✅ Test image downloaded to: $testImagePath" -ForegroundColor Green

# Option 2: Alternativ kannst du einen eigenen Pfad angeben:
# $testImagePath = "C:\Pfad\zu\deinem\bild.jpg"

# ============================================================================
# 1. Erstelle erst einen User (falls noch nicht vorhanden)
# ============================================================================

Write-Host "`n`n=== 0. CREATE USER (if needed) ===" -ForegroundColor Green

$userBody = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

try {
    $userResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/users/" `
        -Method POST `
        -ContentType "application/json" `
        -Body $userBody -ErrorAction SilentlyContinue
    $userData = $userResponse.Content | ConvertFrom-Json
    $userId = $userData.id
    Write-Host "✅ User created with ID: $userId" -ForegroundColor Green
} catch {
    Write-Host "User might already exist, using ID: 1" -ForegroundColor Yellow
    $userId = 1
}

# ============================================================================
# 1. POST mit Bild-Upload (multipart/form-data)
# ============================================================================

Write-Host "`n`n=== 1. CREATE POST WITH IMAGE UPLOAD ===" -ForegroundColor Green

try {
    Write-Host "Uploading post with image..." -ForegroundColor Yellow
    
    # PowerShell 7+ Style mit -Form Parameter (einfacher!)
    $formData = @{
        user = $userId
        title = "Post with MinIO Image Upload"
        text = "This post includes an image stored in MinIO object storage"
        image_file = Get-Item -Path $testImagePath
    }
    
    $response = Invoke-WebRequest -Uri $baseUrl `
        -Method POST `
        -Form $formData
    
    Write-Host "✅ Success! Response:" -ForegroundColor Green
    $responseData = $response.Content | ConvertFrom-Json
    Write-Host ($responseData | ConvertTo-Json -Depth 3) -ForegroundColor Cyan
    
    $postId = $responseData.id
    $imagePath = $responseData.image
    
    Write-Host "`nPost ID: $postId" -ForegroundColor Magenta
    Write-Host "Image Path in MinIO: $imagePath" -ForegroundColor Magenta
    
    # ============================================================================
    # 2. GET Post und prüfe Image-URL
    # ============================================================================
    
    Write-Host "`n`n=== 2. RETRIEVE POST AND CHECK IMAGE ===" -ForegroundColor Green
    
    $getResponse = Invoke-WebRequest -Uri "$baseUrl$postId/"
    $postData = $getResponse.Content | ConvertFrom-Json
    
    Write-Host "Retrieved Post:" -ForegroundColor Yellow
    Write-Host ($postData | ConvertTo-Json -Depth 3) -ForegroundColor Cyan
    
    # ============================================================================
    # 3. DELETE Post (und damit auch das Bild aus MinIO)
    # ============================================================================
    
    Write-Host "`n`n=== 3. DELETE POST (removes image from MinIO) ===" -ForegroundColor Green
    
    Write-Host "Deleting post ID: $postId..." -ForegroundColor Yellow
    $deleteResponse = Invoke-WebRequest -Uri "$baseUrl$postId/" -Method DELETE
    
    Write-Host "✅ Post deleted! Status Code: $($deleteResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Image should also be removed from MinIO bucket." -ForegroundColor Cyan
    Write-Host ($updatedData | ConvertTo-Json -Depth 3) -ForegroundColor Cyan
    

    
} catch {
    Write-Host "❌ Error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}

# Cleanup
Remove-Item $testImagePath -ErrorAction SilentlyContinue

Write-Host "`n`n=== TEST COMPLETE ===" -ForegroundColor Green
Write-Host "Check MinIO Console at: http://localhost:9001/" -ForegroundColor Magenta
Write-Host "Login: minio / mino_admin" -ForegroundColor Magenta
Write-Host "Bucket: social-media-bucket" -ForegroundColor Magenta
