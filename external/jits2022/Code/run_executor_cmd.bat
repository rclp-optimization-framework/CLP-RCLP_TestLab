@echo off
setlocal enabledelayedexpansion

rem Map current folder to a short drive letter to avoid unicode/space issues
set CODE_DIR=%~dp0
set MTD_DRIVE=Z:
if exist Z:\nul (
  set MTD_DRIVE=Y:
)

subst %MTD_DRIVE% "%CODE_DIR%"
if errorlevel 1 (
  echo Failed to map drive with subst
  exit /b 1
)

pushd "%MTD_DRIVE%\MinimalTimetableDisruptions"

rem Update these if your CPLEX installation is in a different location
set CPLEX_JAR="C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\lib\cplex.jar"
set CPLEX_NATIVE_DIR="C:\Program Files\IBM\ILOG\CPLEX_Studio2212\cplex\bin\x64_win64"
set GSON_JAR="%MTD_DRIVE%\MinimalTimetableDisruptions\jars\gson-2.6.2.jar"

echo Gathering Java sources...
dir /b /s src\*.java > files.lst
if not exist files.lst (
  echo No Java sources found
  popd
  exit /b 1
)

echo Compiling Java sources...
javac -cp %CPLEX_JAR%;%GSON_JAR% @files.lst
if errorlevel 1 (
  echo Compilation failed
  popd
  exit /b 1
)

echo Running Executor...
set CLASSPATH=%CPLEX_JAR%;%GSON_JAR%;%MTD_DRIVE%\MinimalTimetableDisruptions\src;.
set SESSION_TIME=%DATE%_%TIME%

set CLEAN_PARAMS=%MTD_DRIVE%\data\experiment_parameters_clean.txt
break > "%CLEAN_PARAMS%"
for /f "usebackq delims=" %%L in ("%MTD_DRIVE%\data\experiment_parameters.txt") do echo %%L>>"%CLEAN_PARAMS%"

if "%EXPERIMENT_FILE%"=="" (
  set PARAM_FILE=../data/experiment_parameters_clean.txt
) else (
  set PARAM_FILE=%EXPERIMENT_FILE%
)

java -cp %CLASSPATH% -Djava.library.path=%CPLEX_NATIVE_DIR% -Dfile.encoding=UTF-8 core.Executor %PARAM_FILE% "%SESSION_TIME%"

set RC=%ERRORLEVEL%
popd
subst %MTD_DRIVE% /d >nul 2>nul
exit /b %RC%
