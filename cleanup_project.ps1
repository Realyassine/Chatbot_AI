# Cleanup script for Chatbot AI project structure
# This script removes test files and other unnecessary files for production delivery

Write-Host "=========================================="
Write-Host "Chatbot AI - Project Structure Cleanup"
Write-Host "=========================================="
Write-Host ""

# Check if backup_tests folder exists
if (!(Test-Path -Path "backup_tests")) {
    New-Item -ItemType Directory -Path "backup_tests"
    Write-Host "Created backup_tests directory"
}

# Files to remove/move from backend directory
$testFiles = @(
    "test_*.py",
    "check_*.py",
    "detailed_test.py",
    "final_test.py",
    "inspect_db.py"
)

# Keep these files even though they match the patterns above
$keepFiles = @(
    "check_dependencies.py"
)

# Process backend directory
Write-Host "Cleaning up backend directory..."
foreach ($pattern in $testFiles) {
    $files = Get-ChildItem -Path "backend\" -Filter $pattern
    foreach ($file in $files) {
        # Skip files we want to keep
        if ($keepFiles -contains $file.Name) {
            Write-Host "  Keeping $($file.Name)"
            continue
        }
        
        # Copy to backup and remove
        Copy-Item -Path $file.FullName -Destination "backup_tests\" -Force
        Remove-Item -Path $file.FullName
        Write-Host "  Moved $($file.Name) to backup_tests\"
    }
}

# Remove root directory test files
Write-Host "Cleaning up root directory..."
$rootTestFiles = @(
    "test_*.mp3",
    "quick_test.html",
    "end_to_end_test.bat"
)

foreach ($pattern in $rootTestFiles) {
    $files = Get-ChildItem -Path "." -Filter $pattern
    foreach ($file in $files) {
        Copy-Item -Path $file.FullName -Destination "backup_tests\" -Force
        Remove-Item -Path $file.FullName
        Write-Host "  Moved $($file.Name) to backup_tests\"
    }
}

# Clean up any pycache files
Write-Host "Cleaning up __pycache__ directories..."
Get-ChildItem -Path "." -Filter "__pycache__" -Recurse | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
    Write-Host "  Removed $($_.FullName)"
}

# Move pre_delivery_checklist.bat to backup
Write-Host "Moving pre-delivery files to backup..."
if (Test-Path "pre_delivery_checklist.bat") {
    Copy-Item -Path "pre_delivery_checklist.bat" -Destination "backup_tests\" -Force
    Remove-Item -Path "pre_delivery_checklist.bat"
    Write-Host "  Moved pre_delivery_checklist.bat to backup_tests\"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Cleanup Complete!"
Write-Host "The project structure has been cleaned up for delivery."
Write-Host "All test files have been backed up to the backup_tests directory."
Write-Host "=========================================="
