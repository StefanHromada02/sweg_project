# ============================================================================
# REST API Test Examples - Social Media Posts
# ============================================================================

$baseUrl = "http://localhost:8000/api/posts/"

Write-Host "`n=== 1. CREATE POSTS (POST Request) ===" -ForegroundColor Green

# Erstelle mehrere Test-Posts
$posts = @(
    @{
        user = 1
        title = "Django REST Framework Tutorial"
        text = "Learn how to build REST APIs with Django and DRF"
        image = "https://example.com/django-tutorial.jpg"
    },
    @{
        user = 2
        title = "Docker Container Best Practices"
        text = "Tips and tricks for optimizing Docker containers"
        image = "https://example.com/docker-tips.jpg"
    },
    @{
        user = 1
        title = "Python Programming Guide"
        text = "Complete guide to Python programming for beginners"
        image = "https://example.com/python-guide.jpg"
    },
    @{
        user = 3
        title = "PostgreSQL Database Administration"
        text = "Essential PostgreSQL admin tasks and optimization"
        image = "https://example.com/postgres-admin.jpg"
    }
)

foreach ($post in $posts) {
    $body = $post | ConvertTo-Json
    Write-Host "`nCreating post: $($post.title)" -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri $baseUrl -Method POST -ContentType "application/json" -Body $body
    Write-Host "Response: $($response.StatusCode) - $($response.Content)" -ForegroundColor Cyan
}

Write-Host "`n`n=== 2. GET ALL POSTS ===" -ForegroundColor Green
$response = Invoke-WebRequest -Uri $baseUrl
Write-Host $response.Content -ForegroundColor Cyan

Write-Host "`n`n=== 3. SEARCH FUNCTIONALITY ===" -ForegroundColor Green

# Suche nach "Django" im Titel oder Text
Write-Host "`nSearch for 'Django':" -ForegroundColor Yellow
$searchUrl = "$baseUrl`?search=Django"
$response = Invoke-WebRequest -Uri $searchUrl
Write-Host $response.Content -ForegroundColor Cyan

# Suche nach "Python"
Write-Host "`n`nSearch for 'Python':" -ForegroundColor Yellow
$searchUrl = "$baseUrl`?search=Python"
$response = Invoke-WebRequest -Uri $searchUrl
Write-Host $response.Content -ForegroundColor Cyan

# Suche nach "Docker"
Write-Host "`n`nSearch for 'Docker':" -ForegroundColor Yellow
$searchUrl = "$baseUrl`?search=Docker"
$response = Invoke-WebRequest -Uri $searchUrl
Write-Host $response.Content -ForegroundColor Cyan

Write-Host "`n`n=== 4. ORDERING (SORTING) ===" -ForegroundColor Green

# Sortiere nach Titel (aufsteigend)
Write-Host "`nOrder by title (ascending):" -ForegroundColor Yellow
$orderUrl = "$baseUrl`?ordering=title"
$response = Invoke-WebRequest -Uri $orderUrl
Write-Host $response.Content -ForegroundColor Cyan

# Sortiere nach Erstellungsdatum (absteigend - neueste zuerst)
Write-Host "`n`nOrder by created_at (newest first):" -ForegroundColor Yellow
$orderUrl = "$baseUrl`?ordering=-created_at"
$response = Invoke-WebRequest -Uri $orderUrl
Write-Host $response.Content -ForegroundColor Cyan

Write-Host "`n`n=== 5. GET SINGLE POST ===" -ForegroundColor Green
Write-Host "`nGet post with ID 1:" -ForegroundColor Yellow
$singleUrl = "$baseUrl`1/"
$response = Invoke-WebRequest -Uri $singleUrl
Write-Host $response.Content -ForegroundColor Cyan

Write-Host "`n`n=== 6. UPDATE POST (PUT Request) ===" -ForegroundColor Green
$updateBody = @{
    user = 1
    title = "Django REST Framework Tutorial - UPDATED"
    text = "Updated content: Learn how to build REST APIs with Django and DRF"
    image = "https://example.com/django-tutorial-updated.jpg"
} | ConvertTo-Json

Write-Host "`nUpdating post ID 1:" -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "$baseUrl`1/" -Method PUT -ContentType "application/json" -Body $updateBody
Write-Host $response.Content -ForegroundColor Cyan

Write-Host "`n`n=== 7. DELETE POST ===" -ForegroundColor Green
Write-Host "`nDeleting post ID 4:" -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "$baseUrl`4/" -Method DELETE
Write-Host "Response: $($response.StatusCode) - Deleted successfully" -ForegroundColor Cyan

Write-Host "`n`n=== 8. COMBINED SEARCH + ORDERING ===" -ForegroundColor Green
Write-Host "`nSearch for 'guide' and order by title:" -ForegroundColor Yellow
$combinedUrl = "$baseUrl`?search=guide&ordering=title"
$response = Invoke-WebRequest -Uri $combinedUrl
Write-Host $response.Content -ForegroundColor Cyan

Write-Host "`n`n=== DONE ===" -ForegroundColor Green
Write-Host "Check Swagger UI at: http://localhost:8000/api/schema/swagger-ui/" -ForegroundColor Magenta
Write-Host "Check ReDoc at: http://localhost:8000/api/schema/redoc/" -ForegroundColor Magenta
