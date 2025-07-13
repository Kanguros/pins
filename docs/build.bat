@echo off
REM Build script for Policy Inspector documentation (Windows)

setlocal enabledelayedexpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\"
set "DOCS_DIR=%SCRIPT_DIR%"
set "SOURCE_DIR=%DOCS_DIR%source"
set "BUILD_DIR=%DOCS_DIR%build"

REM Functions
:log_info
echo [INFO] %~1
goto :eof

:log_warn
echo [WARN] %~1
goto :eof

:log_error
echo [ERROR] %~1
goto :eof

:check_dependencies
call :log_info "Checking dependencies..."

where poetry >nul 2>nul
if %errorlevel% neq 0 (
    call :log_error "Poetry is not installed. Please install Poetry first."
    exit /b 1
)

poetry run python -c "import sphinx" >nul 2>nul
if %errorlevel% neq 0 (
    call :log_error "Sphinx not found. Please install documentation dependencies:"
    echo   poetry install --with docs
    exit /b 1
)

call :log_info "Dependencies check passed."
goto :eof

:clean_build
call :log_info "Cleaning build directory..."
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
call :log_info "Clean complete."
goto :eof

:build_html
call :log_info "Building HTML documentation..."

cd /d "%DOCS_DIR%"
poetry run sphinx-build -b html "%SOURCE_DIR%" "%BUILD_DIR%\html"
if %errorlevel% equ 0 (
    call :log_info "HTML documentation built successfully."
    echo   📁 Output: %BUILD_DIR%\html\index.html
) else (
    call :log_error "HTML build failed."
    exit /b 1
)
goto :eof

:build_html_strict
call :log_info "Building HTML documentation (strict mode - warnings as errors)..."

cd /d "%DOCS_DIR%"
poetry run sphinx-build -W -b html "%SOURCE_DIR%" "%BUILD_DIR%\html"
if %errorlevel% equ 0 (
    call :log_info "HTML documentation built successfully (strict mode)."
    echo   📁 Output: %BUILD_DIR%\html\index.html
) else (
    call :log_error "HTML build failed in strict mode."
    exit /b 1
)
goto :eof

:check_links
call :log_info "Checking external links..."

cd /d "%DOCS_DIR%"
poetry run sphinx-build -b linkcheck "%SOURCE_DIR%" "%BUILD_DIR%\linkcheck"
if %errorlevel% equ 0 (
    call :log_info "Link check completed successfully."
    echo   📁 Report: %BUILD_DIR%\linkcheck\output.txt
) else (
    call :log_warn "Link check found issues. Check the report for details."
)
goto :eof

:serve_docs
if not exist "%BUILD_DIR%\html" (
    call :log_warn "HTML documentation not found. Building first..."
    call :build_html
)

call :log_info "Starting local documentation server..."
echo   🌐 URL: http://localhost:8000
echo   🔄 Press Ctrl+C to stop

cd /d "%BUILD_DIR%\html"
python -m http.server 8000
goto :eof

:validate_docs
call :log_info "Validating documentation structure..."

REM Check required files exist
set "required_files=%SOURCE_DIR%\index.md %SOURCE_DIR%\conf.py %SOURCE_DIR%\guides\installation.md %SOURCE_DIR%\guides\quick-start.md %SOURCE_DIR%\api\index.md"

for %%f in (%required_files%) do (
    if not exist "%%f" (
        call :log_error "Required file missing: %%f"
        exit /b 1
    )
)

call :log_info "Documentation validation completed successfully."
goto :eof

:show_help
echo Policy Inspector Documentation Build Script
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo     html        Build HTML documentation (default)
echo     html-strict Build HTML documentation with warnings as errors
echo     clean       Clean build directory
echo     linkcheck   Check external links
echo     serve       Serve documentation locally on port 8000
echo     validate    Validate documentation structure and syntax
echo     all         Build HTML and check links
echo     help        Show this help message
echo.
echo Examples:
echo     %~nx0 html           # Build HTML documentation
echo     %~nx0 clean html     # Clean and build HTML documentation  
echo     %~nx0 serve          # Serve documentation locally
echo     %~nx0 all            # Build everything and validate
echo.
goto :eof

REM Main script logic
cd /d "%PROJECT_ROOT%"

set "command=%~1"
if "%command%"=="" set "command=html"

if "%command%"=="clean" (
    call :clean_build
) else if "%command%"=="html" (
    call :check_dependencies
    call :build_html
) else if "%command%"=="html-strict" (
    call :check_dependencies
    call :build_html_strict
) else if "%command%"=="linkcheck" (
    call :check_dependencies
    call :check_links
) else if "%command%"=="serve" (
    call :check_dependencies
    call :serve_docs
) else if "%command%"=="validate" (
    call :validate_docs
) else if "%command%"=="all" (
    call :check_dependencies
    call :validate_docs
    call :clean_build
    call :build_html_strict
    call :check_links
    call :log_info "🎉 All documentation tasks completed successfully!"
) else if "%command%"=="help" (
    call :show_help
) else if "%command%"=="-h" (
    call :show_help
) else if "%command%"=="--help" (
    call :show_help
) else (
    call :log_error "Unknown command: %command%"
    call :show_help
    exit /b 1
)

endlocal
