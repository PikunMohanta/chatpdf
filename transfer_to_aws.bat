@echo off
REM PDFPixie - Transfer & Deploy to AWS (Windows)
REM Run this from your LOCAL Windows machine

echo ========================================
echo   PDFPixie - Transfer and Deploy to AWS
echo ========================================
echo.

REM Check if SSH key path is provided
if "%~1"=="" (
    echo Usage: transfer_to_aws.bat "path\to\your\key.pem"
    echo Example: transfer_to_aws.bat "C:\Users\YourName\.ssh\aws-key.pem"
    exit /b 1
)

set SSH_KEY=%~1
set AWS_IP=13.201.129.219
set AWS_USER=ubuntu
set REMOTE_PATH=/home/ubuntu/chatpdf

echo Configuration:
echo   AWS IP: %AWS_IP%
echo   SSH Key: %SSH_KEY%
echo   Remote Path: %REMOTE_PATH%
echo.

REM Check if key exists
if not exist "%SSH_KEY%" (
    echo Error: SSH key not found: %SSH_KEY%
    exit /b 1
)

echo Testing SSH connection...
ssh -i "%SSH_KEY%" -o ConnectTimeout=5 %AWS_USER%@%AWS_IP% "echo 'Connection successful'" >nul 2>&1
if errorlevel 1 (
    echo Error: Cannot connect to AWS instance
    echo Please check:
    echo   1. AWS security group allows SSH from your IP
    echo   2. SSH key is correct
    echo   3. AWS instance is running
    exit /b 1
)
echo Connection successful!
echo.

echo Transferring files to AWS...

REM Transfer frontend files
echo   - Frontend environment config...
scp -i "%SSH_KEY%" frontend\.env.production %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/frontend/

echo   - Frontend components...
scp -i "%SSH_KEY%" frontend\src\components\ChatWorkspace.tsx %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/frontend/src/components/
scp -i "%SSH_KEY%" frontend\src\components\UploadScreen.tsx %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/frontend/src/components/
scp -i "%SSH_KEY%" frontend\src\components\PdfViewer.tsx %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/frontend/src/components/
scp -i "%SSH_KEY%" frontend\src\components\ChatPanel.tsx %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/frontend/src/components/

echo   - Frontend App.tsx...
scp -i "%SSH_KEY%" frontend\src\App.tsx %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/frontend/src/

REM Transfer nginx configs
echo   - Nginx configurations...
scp -i "%SSH_KEY%" nginx\nginx.conf %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/nginx/
scp -i "%SSH_KEY%" nginx\conf.d\pdfpixie.conf %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/nginx/conf.d/

REM Transfer deployment scripts
echo   - Deployment scripts...
scp -i "%SSH_KEY%" deploy.sh %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/
scp -i "%SSH_KEY%" Dockerfile %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/

REM Transfer documentation
echo   - Documentation...
scp -i "%SSH_KEY%" AWS_DEPLOYMENT_GUIDE.md %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/
scp -i "%SSH_KEY%" FIX_SUMMARY.md %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/
scp -i "%SSH_KEY%" QUICK_DEPLOY.md %AWS_USER%@%AWS_IP%:%REMOTE_PATH%/

echo Files transferred successfully!
echo.

echo Deploying on AWS instance...
echo This may take several minutes...
echo.

ssh -i "%SSH_KEY%" %AWS_USER%@%AWS_IP% "cd %REMOTE_PATH% && chmod +x deploy.sh && ./deploy.sh"

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Your app is now accessible from any device at:
echo   * http://13.201.129.219
echo   * http://pdfpixie.duckdns.org (after DNS setup)
echo.
echo Test it from your phone or another device!
echo.
echo To check logs:
echo   ssh -i "%SSH_KEY%" %AWS_USER%@%AWS_IP% "docker logs pdfpixie -f"
echo.

pause
