# Test image upload and resize service
$imagePath = "C:\Windows\Web\Wallpaper\Windows\img0.jpg"

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"title`"$LF",
    "Test Image Resize",
    "--$boundary",
    "Content-Disposition: form-data; name=`"text`"$LF",
    "Testing the image resize microservice",
    "--$boundary",
    "Content-Disposition: form-data; name=`"user`"$LF",
    "1",
    "--$boundary",
    "Content-Disposition: form-data; name=`"image_file`"; filename=`"test.jpg`"",
    "Content-Type: image/jpeg$LF",
    [System.IO.File]::ReadAllText($imagePath, [System.Text.Encoding]::GetEncoding("ISO-8859-1")),
    "--$boundary--$LF"
) -join $LF

$bytes = [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetBytes($bodyLines)

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/posts/" `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bytes
    
    Write-Host "Post created successfully!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host $_.Exception.Response.StatusCode
}
