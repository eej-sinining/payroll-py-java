@echo off
echo Compiling service.java...
javac service.java

if %errorlevel% neq 0 (
    echo Compilation failed.
    exit /b
)

echo Running service.class...
java service
pause
