@echo off
setlocal enableextensions enabledelayedexpansion
rem Ensure we run from the script folder to avoid issues with spaces/Unicode in parent paths
pushd "%~dp0\MinimalTimetableDisruptions"
set "CPLEX_JAR=C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\lib\cplex.jar"
set "GSON_JAR=MinimalTimetableDisruptions\jars\gson-2.6.2.jar"
set "SRC=MinimalTimetableDisruptions\src"
set "BIN=MinimalTimetableDisruptions\bin"
if not exist "%BIN%" mkdir "%BIN%"
if exist files.lst del /f /q files.lst
for /R "%SRC%" %%f in (*.java) do @echo "%%f">>files.lst
echo Compiling Java sources... 
javac -classpath "%CPLEX_JAR%;%GSON_JAR%" -d "%BIN%" @files.lst
if errorlevel 1 (
	echo Compilation failed
	type files.lst
	pause
	exit /b 1
)
echo Running Java harness...
java -Djava.library.path="C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\bin\x64_win64" -Dfile.encoding=UTF-8 -cp "%BIN%;%CPLEX_JAR%;%GSON_JAR%" core.Executor data\experiment_parameters_toy.txt
if errorlevel 1 (
	echo Java execution failed with code %errorlevel%
)
pause
endlocal
popd >nul 2>&1
